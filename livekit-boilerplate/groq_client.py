import logging
import asyncio
from groq import AsyncGroq
from config import settings
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.interviewer_model = "llama-3.1-8b-instant"

        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    async def stream_chat(self, text: str, was_interrupted: bool = False):
        if was_interrupted and len(self.messages) > 1 and self.messages[-1]["role"] == "user":
            previous_text = self.messages.pop()["content"]
            text = f"{previous_text} ... {text}"
            logger.info(f"🔄 Interruption — concatenated: {text}")

        self.messages.append({"role": "user", "content": text})

        max_retries = 3
        stream = None
        for attempt in range(max_retries):
            try:
                stream = await self.client.chat.completions.create(
                    messages=self.messages,
                    model=self.interviewer_model,
                    stream=True,
                    temperature=0.7,
                    max_tokens=200,
                )
                break
            except Exception as e:
                if "429" in str(e) or "rate_limit" in str(e).lower():
                    logger.warning(f"Rate limit — retrying... ({attempt+1}/{max_retries})")
                    await asyncio.sleep(1)
                else:
                    logger.error(f"LLM error: {e}")
                    break

        full_reply = ""
        try:
            if stream:
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        word = chunk.choices[0].delta.content
                        full_reply += word
                        yield word
            else:
                fallback = "Sorry, I'm having a technical issue."
                full_reply = fallback
                yield fallback
        finally:
            if full_reply.strip():
                self.messages.append({"role": "assistant", "content": full_reply.strip()})

    async def stream_opening_message(self):
        opening_prompt = SYSTEM_PROMPT + "\nIntroduce yourself briefly and ask how you can help."
        max_retries = 3
        stream = None
        for attempt in range(max_retries):
            try:
                stream = await self.client.chat.completions.create(
                    messages=[{"role": "system", "content": opening_prompt}],
                    model=self.interviewer_model,
                    stream=True,
                    temperature=0.7,
                    max_tokens=100,
                )
                break
            except Exception as e:
                if "429" in str(e) or "rate_limit" in str(e).lower():
                    await asyncio.sleep(1)
                else:
                    break

        full_reply = ""
        if stream:
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    word = chunk.choices[0].delta.content
                    full_reply += word
                    yield word
        else:
            fallback = "Hi, I am your voice assistant. How can I help you today?"
            full_reply = fallback
            yield fallback

        self.messages.append({"role": "assistant", "content": full_reply})
