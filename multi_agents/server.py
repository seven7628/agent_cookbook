from state import State
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import BaseMessage, ToolMessage, AIMessageChunk
from graph import create_graph
from typing import cast
import json
import uvicorn

app = FastAPI(
    title="MCPText",
    version="1.0",
    description="MCPText API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

g = create_graph()

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@app.post("/api/stream")
async def invoke(request: Request):
    # data = await request.json()
    form = await request.form()
    message = State(
        question=form.get('content'),
        human_feedback=False,
        plan=None,
        current_state=None,
        final_answer=None,
    )
    
    return StreamingResponse(get_stream_response(message), media_type="text/event-stream")

async def get_stream_response(message):
    async for agent, sub, event in g.astream(message, subgraphs=True, stream_mode=["messages", "updates"]):
        if sub == "updates":
            continue

        print("agent", agent)
        print('sub', sub)
        print("event", event)
        
        message_chunk, message_metadata = cast(
            tuple([BaseMessage, dict[str, any]]),
            event
        )
        event_stream_message : dict[str, any] = {
            # "thread_id": message_chunk.thread_id,
            "agent": agent[0].split(":")[0],
            "content": message_chunk.content,
            "run_id": message_chunk.id,
            "role": "assistant",
        }
        if isinstance(message_chunk, ToolMessage):
            # Tool Message - Return the result of the tool call
            event_stream_message["tool_call_id"] = message_chunk.tool_call_id
            yield _make_event("tool_call_result", event_stream_message)
        elif isinstance(message_chunk, AIMessageChunk):
            # AI Message - Raw message tokens
            if message_chunk.tool_calls:
                # AI Message - Tool Call
                event_stream_message["tool_calls"] = message_chunk.tool_calls
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks
                )
                yield _make_event("tool_calls", event_stream_message)
            elif message_chunk.tool_call_chunks:
                # AI Message - Tool Call Chunks
                event_stream_message["tool_call_chunks"] = (
                    message_chunk.tool_call_chunks
                )
                yield _make_event("tool_call_chunks", event_stream_message)
            else:
                # AI Message - Raw message tokens
                yield _make_event("message_chunk", event_stream_message)
        # yield f"event:{agent}\ndata: {event}\n\n"

def _make_event(event_type:str, data:dict[str,any]) -> str:
    return f"event:{event_type}\ndata:{json.dumps(data, ensure_ascii=False)}\n\n"

if __name__ == "__main__":
    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # asyncio.run(app)