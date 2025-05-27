from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
from python_a2a import A2AServer, skill, agent, TaskStatus, TaskState

app = FastAPI()

@agent(
    name="Weather Agent",
    description="Provides weather information",
    version="1.0.0"
)
class WeatherAgent(A2AServer):
    
    @skill(
        name="Get Weather",
        description="Get current weather for a location",
        tags=["weather", "forecast"]
    )
    def get_weather(self, location):
        """Get weather for a location."""
        # Mock implementation
        return f"It's sunny and 75°F in {location}"
    
    def handle_task(self, task):
        # Extract location from message
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else ""
        
        if "weather" in text.lower() and "in" in text.lower():
            location = text.split("in", 1)[1].strip().rstrip("?.")
            
            # Get weather and create response
            weather_text = self.get_weather(location)
            task.artifacts = [{
                "parts": [{"type": "text", "text": weather_text}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
        else:
            task.status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message={"role": "agent", "content": {"type": "text", 
                         "text": "Please ask about weather in a specific location."}}
            )
        return task


weather_agent = WeatherAgent()

# SSE stream để gửi dữ liệu thời tiết
async def weather_stream(location: str):
    task = type('Task', (), {
        'message': {'content': {'text': f"weather in {location}"}},
        'artifacts': [],
        'status': None
    })()
    
    processed_task = weather_agent.handle_task(task)
    
    if processed_task.status.state == TaskState.COMPLETED:
        weather_data = processed_task.artifacts[0]["parts"][0]["text"]
        yield f"data: {weather_data}\n\n"
    else:
        yield f"data: Error: {processed_task.status.message['content']['text']}\n\n"

@app.get("/weather/stream/{location}")
async def stream_weather(location: str):
    return StreamingResponse(
        weather_stream(location),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)