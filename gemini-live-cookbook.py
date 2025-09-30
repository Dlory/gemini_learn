import asyncio
import wave
from google import genai

client = genai.Client(http_options={"api_version": "v1alpha"})
model = "gemini-live-2.5-flash-preview"

config={
    "response_modalities": ["TEXT"]
}

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        message = "Hello? Gemini are you there?"
        print("> ", message, "\n")
        await session.send_client_content(
                turns={"role": "user", "parts": [{"text": message}]}, turn_complete=True
        )

        # For text responses, When the model's turn is complete it breaks out of the loop.
        turn = session.receive()
        async for chunk in turn:
            if chunk.text is not None:
                print(f'- {chunk.text}')

if __name__ == "__main__":
    asyncio.run(main())