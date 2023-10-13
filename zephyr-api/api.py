from fastapi import FastAPI, HTTPException, WebSocket
import torch
import GPUtil
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

pipe = pipeline(
    "text-generation",
    model="HuggingFaceH4/zephyr-7b-alpha",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8501",
    # Add any other origins from which you want to allow requests
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryModel(BaseModel):
    user_message: str
    max_new_tokens: int = 256
    do_sample: bool = True
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95
    system_message: Optional[str] = "You are a friendly chatbot who always responds in the style of a python developer that uses a combination of natural language and markdown to answer questions."


@app.get("/")
async def root():
    return {"message": "Welcome to the Zephyr API! Please use the /zephyr endpoint to get a response from the Zephyr chatbot."}

## Endpoint for getting a raw response from the Zephyr chatbot, including system and assistant tokens
@app.post("/zephyr/raw")
async def raw_response(user_message: str):
    messages = [
        {
            "role": "system",
            "content": "You are a friendly chatbot who always responds in the style of a python developer that uses a combination of natural language and markdown to answer questions.",
        },
        {"role": "user", "content": user_message},
    ]
    
    prompt = pipe.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    
    return {"response": outputs[0]["generated_text"]}


## Endpoint for getting a pythonic response from the Zephyr chatbot
@app.post("/zephyr/python")
async def get_response(query: QueryModel):
    messages = [
        {
            "role": "system",
            "content": "You are a friendly chatbot who always responds in the style of a python developer that uses a combination of natural language and markdown to answer questions.",
        },
        {"role": "user", "content": query.user_message},
    ]
    
    prompt = pipe.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    outputs = pipe(
        prompt, 
        max_new_tokens=query.max_new_tokens, 
        do_sample=query.do_sample, 
        temperature=query.temperature, 
        top_k=query.top_k, 
        top_p=query.top_p
    )
    
    # Split at the last occurrence of '</s>' and take everything after it
    response = outputs[0]["generated_text"].split('</s>')[-1].strip()
    
    # Remove all leading newline characters
    while response.startswith("\n"):
        response = response[1:]
    
    if response.startswith("<|assistant|>\n"):
        response = response[len("<|assistant|>\n"):].lstrip()
    
    return {"response": response}

## This endpoint allows the user to specify a custom system message
@app.post("/zephyr/system-message")
async def get_custom_response(query: QueryModel):
    messages = [
        {
            "role": "system",
            "content": query.system_message,
        },
        {"role": "user", "content": query.user_message},
    ]
    
    prompt = pipe.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    outputs = pipe(
        prompt, 
        max_new_tokens=query.max_new_tokens, 
        do_sample=query.do_sample, 
        temperature=query.temperature, 
        top_k=query.top_k, 
        top_p=query.top_p
    )
    
    # Split at the last occurrence of '</s>' and take everything after it
    response = outputs[0]["generated_text"].split('</s>')[-1].strip()
    
    # Remove all leading newline characters
    while response.startswith("\n"):
        response = response[1:]
    
    if response.startswith("\n"):
        response = response[len("\n"):].lstrip()
        # Remove all leading newline characters
    while response.startswith("\n"):
        response = response[1:]
    
    if response.startswith("<|assistant|>\n"):
        response = response[len("<|assistant|>\n"):].lstrip()
    
    return {"response": response}


## Websocket for live GPU usage stats when querying the model
@app.websocket("zephyr/ws/gpu-stats")
async def websocket_gpu_usage(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Get GPU stats
            gpus = GPUtil.getGPUs()
            gpu_data = []
            for gpu in gpus:
                data = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "driver_version": gpu.driver,
                    "load": gpu.load * 100,  # in percentage
                    "memoryUsed": gpu.memoryUsed,
                    "memoryFree": gpu.memoryFree,
                    "memoryTotal": gpu.memoryTotal,
                }
                gpu_data.append(data)
            
            # Send GPU stats to client
            await websocket.send_json({"gpus": gpu_data})
            
            # Wait for some time before sending the next update
            await asyncio.sleep(1)  # send updates every second
    except:
        await websocket.close()
