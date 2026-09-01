import logging
import asyncio
import json
from groq import AsyncGroq
from config import settings
from schemas import ConversationalResponse, ExtractionResponse

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.interviewer_model = settings.GROQ_MODEL 
        self.extractor_model = settings.EXTRACTOR_MODEL

    async def _resolve_working_model(self, requested_model: str) -> str:
        try:
            models_page = await self.client.models.list()
            available = [m.id for m in models_page.data]
            logger.info(f"📋 Currently available Groq models: {available}")
            if requested_model in available:
                return requested_model
            
            # Fallback preference order
            for fallback in ["llama-3.1-8b-instant", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"]:
                if fallback in available:
                    logger.warning(f"⚠️ Requested model '{requested_model}' unavailable. Auto-fallback to '{fallback}'")
                    return fallback
            
            if available:
                return available[0]
        except Exception as e:
            logger.error(f"Failed to fetch available Groq models: {e}")
        
        return "llama-3.1-8b-instant"

    async def get_conversational_decision(self, prompt: str) -> ConversationalResponse:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = await self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a JSON-only AI. Always output valid JSON matching the schema requested." },
                        {"role": "user", "content": prompt}
                    ],
                    model=self.interviewer_model,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                content = chat_completion.choices[0].message.content
                logger.info(f"LLM Raw JSON: {content}")
                
                data = json.loads(content)
                return ConversationalResponse(**data)
                
            except Exception as e:
                logger.error(f"LLM attempt {attempt+1} failed ({self.interviewer_model}): {e}")
                if "decommissioned" in str(e).lower() or "not_found" in str(e).lower() or "404" in str(e) or "400" in str(e):
                    self.interviewer_model = await self._resolve_working_model(self.interviewer_model)
                await asyncio.sleep(1)
        
        # Fallback if everything fails
        return ConversationalResponse(
            action="ERROR",
            response="I'm sorry, I'm having a technical issue right now."
        )

    async def extract_answer(self, prompt: str) -> ExtractionResponse:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = await self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a JSON-only Data Extractor. Always output valid JSON matching the schema requested." },
                        {"role": "user", "content": prompt}
                    ],
                    model=self.extractor_model,
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                
                content = chat_completion.choices[0].message.content
                logger.info(f"Extractor LLM JSON: {content}")
                
                data = json.loads(content)
                return ExtractionResponse(**data)
                
            except Exception as e:
                logger.error(f"Extractor LLM attempt {attempt+1} failed ({self.extractor_model}): {e}")
                if "decommissioned" in str(e).lower() or "not_found" in str(e).lower() or "404" in str(e) or "400" in str(e):
                    self.extractor_model = await self._resolve_working_model(self.extractor_model)
                await asyncio.sleep(1)
                
        return ExtractionResponse(
            answer_status="unknown",
            answer=None
        )

class GeminiClient:
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")
        self.interviewer_model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-3.1-flash-lite') or 'gemini-3.1-flash-lite'
        self.extractor_model_name = getattr(settings, 'EXTRACTOR_MODEL', 'gemini-3.1-flash-lite') or 'gemini-3.1-flash-lite'
        
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.genai = genai
        logger.info("Initialized google.generativeai SDK client.")

    async def get_conversational_decision(self, prompt: str) -> ConversationalResponse:
        max_retries = 3
        models_to_try = [self.interviewer_model_name]
        unique_models = list(dict.fromkeys([m for m in models_to_try if m]))

        for model_name in unique_models:
            for attempt in range(max_retries):
                try:
                    logger.info(f"Calling Gemini ({model_name})...")
                    model = self.genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction="You are a JSON-only AI. Always output valid JSON matching the schema requested."
                    )
                    config = self.genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.3
                    )
                    response = await model.generate_content_async(prompt, generation_config=config)
                    content = response.text

                    logger.info(f"Gemini Raw JSON ({model_name}): {content}")
                    data = json.loads(content)
                    return ConversationalResponse(**data)
                except Exception as e:
                    logger.error(f"Gemini attempt {attempt+1} with model {model_name} failed: {e}")
                    await asyncio.sleep(1)

        return ConversationalResponse(
            action="ERROR",
            response="I'm sorry, I'm having a technical issue right now."
        )

    async def extract_answer(self, prompt: str) -> ExtractionResponse:
        max_retries = 3
        models_to_try = [self.extractor_model_name]
        unique_models = list(dict.fromkeys([m for m in models_to_try if m]))

        for model_name in unique_models:
            for attempt in range(max_retries):
                try:
                    model = self.genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction="You are a JSON-only Data Extractor. Always output valid JSON matching the schema requested."
                    )
                    config = self.genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                    response = await model.generate_content_async(prompt, generation_config=config)
                    content = response.text

                    logger.info(f"Extractor Gemini JSON ({model_name}): {content}")
                    data = json.loads(content)
                    return ExtractionResponse(**data)
                except Exception as e:
                    logger.error(f"Extractor Gemini attempt {attempt+1} with model {model_name} failed: {e}")
                    await asyncio.sleep(1)

        return ExtractionResponse(
            answer_status="unknown",
            answer=None
        )

    async def stream_opening_message(self, student_name: str = None):
        name_str = f" {student_name}" if student_name and student_name.lower() != "student" else ""
        opening = f"नमस्ते{name_str}! मैं आपकी AI इंटरव्यूअर बोध हूँ। आज हम आपकी पढ़ाई और सब्जेक्ट्स के बारे में बात करेंगे। यहाँ कोई सही या गलत उत्तर नहीं हैं। क्या हम शुरू करें?"
        yield opening


# Use GeminiClient by default or GroqClient based on LLM_PROVIDER
if getattr(settings, 'LLM_PROVIDER', 'gemini').lower() == 'groq':
    LLMClient = GroqClient
else:
    LLMClient = GeminiClient


