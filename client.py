import httpx
import asyncio
import json
import sys

async def sse_client(url):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                if line.strip():  # Chỉ cần check line không rỗng
                    try:
                        # Parse JSON trực tiếp
                        data = json.loads(line)
                        if 'content' in data:
                            print(f"{data['content']}", end="", flush=True)  # Thêm flush=True
                        elif 'error' in data:
                            print(f"Error: {data['error']}", flush=True)
                    except json.JSONDecodeError:
                        # Nếu không phải JSON thì in trực tiếp
                        if line == "[DONE]":
                            print("\nStream finished", flush=True)
                            break
                        else:
                            print(line, end="", flush=True)  # Thêm flush=True

async def main():
    location = "Hanoi"
    url = f"http://localhost:5000/weather/stream/{location}"
    await sse_client(url)

if __name__ == "__main__":
    asyncio.run(main())