import { COLORS } from '../theme/colors';

const BACKEND_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function requestStartCall({ schoolCode, studentId, name, grade }) {
  try {
    const response = await fetch(`${BACKEND_URL}/start_call`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        school_code: schoolCode,
        student_id: studentId,
        name: name || 'Student',
        grade: grade || 'Grade 8',
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Server returned ${response.status}: ${errText}`);
    }

    const data = await response.json();
    return {
      success: true,
      roomName: data.room_name,
      token: data.token,
      wsUrl: data.ws_url || 'ws://127.0.0.1:8880',
    };
  } catch (error) {
    console.warn('Backend API request failed. Falling back to local session simulation:', error.message);
    // Dev Fallback for seamless local preview if FastAPI server is temporarily unreachable
    return {
      success: true,
      roomName: `chat-${Math.random().toString(36).substring(2, 10)}`,
      token: 'mock-jwt-token-dev',
      wsUrl: 'ws://127.0.0.1:8880',
      isMock: true,
    };
  }
}
