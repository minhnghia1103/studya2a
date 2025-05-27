import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def llm_stream(location: str):
    """Stream response từ LLM về thời tiết."""
    
    try:
        # Tạo request tới OpenAI với stream=True
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý thời tiết. Trả lời ngắn gọn bằng tiếng Việt."},
                {"role": "user", "content": f"Hãy mô tả thời tiết hôm nay ở {location}"}
            ],
            stream=True,
            max_tokens=200
        )
        
        # Stream từng chunk từ OpenAI
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content})}\n\n"
                await asyncio.sleep(0.01)  # Nhỏ delay để smooth streaming
        
        # Kết thúc stream
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.get("/weather/stream/{location}")
async def stream_weather(location: str):
    """Stream thông tin thời tiết từ LLM."""
    return StreamingResponse(
        llm_stream(location),
        media_type="text/event-stream"
    )

@app.get("/")
async def root():
    return {"message": "LLM Weather Streaming API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)