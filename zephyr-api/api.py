from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import torch
import GPUtil
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import black
import base64
import asyncio

app = FastAPI()

templates = Jinja2Templates(directory="templates")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

pipe = pipeline(
    "text-generation",
    model="HuggingFaceH4/zephyr-7b-alpha",
    torch_dtype=torch.bfloat16,
    device_map=device,
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

class CodeDocQuery(BaseModel):
    code: str
    language: Optional[str] = "python"  # default to python, but allow for other languages if you plan on expanding
    include_comments: Optional[bool] = True # whether to generate comments for the code
    max_new_tokens: int = 256
    do_sample: bool = True
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95

# class FunctionDocQuery(BaseModel):
#     code: str
#     brief_description: Optional[str] = ""
#     max_new_tokens: int = 256
#     do_sample: bool = True
#     temperature: float = 0.7
#     top_k: int = 50
#     top_p: float = 0.95

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    routes = [route for route in request.app.routes]
    endpoints = [
        {
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods)
        }
        for route in routes
    ]

    return templates.TemplateResponse("welcome.html", {"request": request, "endpoints": endpoints})


## Endpoint for getting a raw response from the Zephyr chatbot, including system and assistant tokens
@app.post("/zephyr/raw", description="Get a raw response from the Zephyr chatbot, including system and assistant tokens.")
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
@app.post("/zephyr/python", description="Get a pythonic response from the Zephyr chatbot.")
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
    print("Received query:", query)
    print("Generated prompt:", prompt)
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
@app.post("/zephyr/system-message", description="Get a response from the Zephyr chatbot with a custom system message. The default message is geared towards python code.")
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

from fastapi import HTTPException

@app.post("/zephyr/code-doc", description="Get a README in markdown format for a code snippet.")
async def get_code_documentation(query: CodeDocQuery):
    try:
        system_instruction = f"Generate markdown documentation for the following {query.language} code."
     
        messages = [
            {
                "role": "system",
                "content": system_instruction,
            },
            {"role": "user", "content": query.code},
        ]

        # Assuming pipe.tokenizer.apply_chat_template constructs a prompt for the model
        prompt = pipe.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # Call the model (or service) to generate the markdown documentation
        outputs = pipe(
            prompt, 
            max_new_tokens=query.max_new_tokens, 
            do_sample=query.do_sample, 
            temperature=query.temperature, 
            top_k=query.top_k, 
            top_p=query.top_p
        )

        # Extract and clean the generated text
        response = outputs[0]["generated_text"].split('</s>')[-1].strip()
        while response.startswith("\n"):
            response = response[1:]
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
    except Exception as e:
        # Catch any unexpected errors and return a clearer message to the client
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/zephyr/structured-code-doc", description="Get a README in pre-defined format that takes some of the compute burden off of the model.")
async def get_structured_code_documentation(query: QueryModel):
   
    system_instruction = (
        "Generate markdown documentation for the following python code."
    )
    
    messages = [
        {
            "role": "system",
            "content": system_instruction,
        },
        {"role": "user", "content": system_instruction},
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
    
    
    # Extract and clean the generated text
    response = outputs[0]["generated_text"].split('</s>')[-1].strip()
    while response.startswith("\n"):
            response = response[1:]
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




# ## Websocket for live GPU usage stats when querying the model
# @app.websocket("zephyr/ws/gpu-stats")
# async def websocket_gpu_usage(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             # Get GPU stats
#             gpus = GPUtil.getGPUs()
#             gpu_data = []
#             for gpu in gpus:
#                 data = {
#                     "id": gpu.id,
#                     "name": gpu.name,
#                     "driver_version": gpu.driver,
#                     "load": gpu.load * 100,  # in percentage
#                     "memoryUsed": gpu.memoryUsed,
#                     "memoryFree": gpu.memoryFree,
#                     "memoryTotal": gpu.memoryTotal,
#                 }
#                 gpu_data.append(data)
            
#             # Send GPU stats to client
#             await websocket.send_json({"gpus": gpu_data})
            
#             # Wait for some time before sending the next update
#             await asyncio.sleep(1)  # send updates every second
#     except:
#         await websocket.close()
