import os
import tempfile
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


async def transcribe_voice(bot, file_id: str) -> str:
    # Download voice file from Telegram
    voice_file = await bot.get_file(file_id)

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name

    await voice_file.download_to_drive(tmp_path)
    print(f"Voice file downloaded: {tmp_path}")

    # Transcribe using Groq Whisper
    with open(tmp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="text"
        )

    # Cleanup temp file
    os.unlink(tmp_path)

    print(f"Transcribed: {transcription}")
    return transcription