import asyncio
from google import genai

# NOTE: Use the correct model name
model = "gemini-2.5-flash" 
prompt = "Explain why client cleanup is important in asyncio."

async def main():
    # 1. Instantiate the client
    client = genai.Client()
    
    try:
        # 2. Use the client for your API call
        print(f"Sending prompt to {model}...")
        response = await client.aio.models.generate_content(
            model=model,
            contents=[prompt],
        )
        
        print("--- Model Response ---")
        print(response.text)
        print("----------------------")

    except Exception as e:
        print(f"An error occurred during API call: {e}")
        
    finally:
        # 3. CRITICAL STEP: Explicitly close the asynchronous client
        # This cleans up the underlying aiohttp session and prevents the errors.
        print("Closing the genai client...")
        await client.aio.close()

if __name__ == "__main__":
    # You might also consider setting the policy on Windows 
    # if the Proactor error persists, but the client close is the main fix.
    asyncio.run(main())