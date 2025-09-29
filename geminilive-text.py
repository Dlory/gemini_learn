import asyncio
from google import genai

client = genai.Client()
model = "gemini-live-2.5-flash-preview"

config = {"response_modalities": ["TEXT"]}

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        turns = [
            {"role": "user", "parts": [{"text": "What is the capital of France?"}]},
            {"role": "model", "parts": [{"text": "Paris"}]},
        ]
        await session.send_client_content(turns=turns, turn_complete=False)

        turns = [{"role": "user", "parts": [{"text": "What is the capital of Germany?"}]}]

        await session.send_client_content(turns=turns, turn_complete=True)

        async for response in session.receive():
            if response.text is not None:
                print(response.text, end="")

if __name__ == "__main__":
    asyncio.run(main())