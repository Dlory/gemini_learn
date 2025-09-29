import asyncio
import io
from google import genai
from google.genai import types
import soundfile as sf
import librosa

client = genai.Client()
model = "gemini-live-2.5-flash-preview"
config = {"response_modalities": ["TEXT"]}

# 假设这里是你的音频加载和转换逻辑
def get_audio_blob(file_path="sample.wav"):
    buffer = io.BytesIO()
    # 假设 librosa/sf 是可用的，并且 file_path 存在
    y, sr = librosa.load(file_path, sr=16000)
    sf.write(buffer, y, sr, format='RAW', subtype='PCM_16')
    buffer.seek(0)
    audio_bytes = buffer.read()
    return types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")

async def main():
    # 确保 client.aio.close() 被调用以避免 Unclosed client session 错误
    client = genai.Client() 
    audio_blob = get_audio_blob()
    
    # 存储对话历史
    history = []

    async with client.aio.live.connect(model=model, config=config) as session:
        print("--- 第 1 回合：发送音频 ---")
        
        # 1. 发送音频数据
        await session.send_realtime_input(audio=audio_blob)

        # 2. 接收模型对音频的转录或总结
        audio_response_text = ""
        async for chunk in session.receive():
            if chunk.text:
                audio_response_text += chunk.text
                print(chunk.text, end="", flush=True)
        print("\n-------------------------")
        
        # 3. 将用户音频和模型响应添加到历史中 (Live API 自动处理)
        # 实际上，Live API 会在服务器端记住这个回合。

    # --- 关键：开始第 2 回合，引用第 1 回合的上下文 ---

    # 由于 Live API 实时会话通常设计为短生命周期，
    # 并且不支持跨 Live Session 传递复杂的历史对象，
    # 最佳实践是使用 GenAI 的标准 Chat API 来管理多模态历史。

    # **如果你必须使用 Live API 并在新的 Live Session 中启动对话:**
    # 这是一个高级且非标准的操作。你需要将模型的转录结果作为“System Instruction”或
    # 第一次 send_client_content 的历史来启动新会话。
    
    if audio_response_text:
        # 构建一个包含音频转录结果的历史记录
        initial_history_turn = {
            "role": "model",
            # 假设模型对音频的转录是这个文本
            "parts": [{"text": f"用户之前的音频内容是：{audio_response_text}"}]
        }
        
        # 用户的新问题
        new_user_question = {
            "role": "user",
            "parts": [{"text": "请总结刚才提到的内容，并告诉我最关键的三个信息点。"}]
        }
        
        print("\n--- 第 2 回合：发送新的上下文请求 ---")
        
        # 启动一个新的 Live Session 来发送文本
        async with client.aio.live.connect(model=model, config=config) as new_session:
            # 1. 发送历史（将上一个回合的音频转录作为历史注入）
            # 注意: 这里的 turns 是一个列表，包含历史和当前问题
            turns_to_send = [initial_history_turn, new_user_question]

            await new_session.send_client_content(
                turns=turns_to_send, 
                turn_complete=True # 立即触发响应
            )

            # 2. 接收响应
            async for chunk in new_session.receive():
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print("\n-------------------------------------")

if __name__ == "__main__":
    # 确保你已经安装了 helpers 并且 'sample.wav' 文件存在
    # pip install librosa soundfile
    # 下载测试文件: https://storage.googleapis.com/generativeai-downloads/data/16000.wav 并改名为 sample.wav
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"发生错误：{e}")