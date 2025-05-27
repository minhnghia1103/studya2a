import httpx
import asyncio

async def sse_client(url):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = line[5:].strip()  # Loại bỏ "data:" và khoảng trắng
                    print(f"Received weather update: {data}")

async def main():
    location = "Hanoi"  # Thay bằng địa điểm bạn muốn
    url = f"http://localhost:5000/weather/stream/{location}"
    await sse_client(url)

if __name__ == "__main__":
    asyncio.run(main())