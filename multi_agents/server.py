from state import State
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from graph import create_graph
import uvicorn

app = FastAPI(
    title="MCPText",
    version="1.0",
    description="MCPText API",
)

g = create_graph()

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@app.post("/generate")
async def invoke(request: Request):
    data = await request.json()
    message = State(
        question=data['content'],
        human_feedback=True,
        plan=None,
        current_state=None,
        final_answer=None,
    )
    # async def
    #     for chunk in g.astream(message):
    #         yield chunk

    async def get_stream_response(message):
        async for agent, data in g.astream(message, subgraphs=True):
            print("agent", agent)
            print("data", data)
            yield data.content
    return StreamingResponse(get_stream_response(message), media_type="text/event-stream")



if __name__ == "__main__":
    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # asyncio.run(app)