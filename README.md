# Zephyr-7B-α-api

This repo contains an api and a chat demo with a redis cache for the zephyr-7b-alpha model from Huggingface. This is an unofficial api that can be self hosted on docker, or if you wish you can add the additional configuration to push to ECS. Minimum  ideal container is p2.xlarge at $0.90/hour.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.3-blue)
![Docker](https://img.shields.io/badge/docker-latest-blue.svg)
![Huggingface](https://img.shields.io/badge/Huggingface-Transformers-orange)

This program is Linux dependent due to some of the dependecies required for the transformers/huggingface libraries. If you are on Windows you will likely need to use WSL to make this work.

If you need to use WSL you can just follow along with the local install instructions from the WSL powershell console.

## Installation

```
git clone https://github.com/tdolan21/zephyr-7b-alpha-api
cd zephyr-7b-alpha-api
docker compose up --build
```

If you wish to use a local/non-containerized install:

```
git clone https://github.com/tdolan21/zephyr-7b-alpha-api
cd zephyr-7b-alpha-api
pip install -r requirements.txt
chmod +x run.sh
./run.sh
```

After this the api and the application will be available at:
```
http://localhost:8000
http://localhost:8501
```
## Usage 

### Default Model Values

QueryModel is the system message standard moddel.

```python
class QueryModel(BaseModel):
    user_message: str
    max_new_tokens: int = 256
    do_sample: bool = True
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95
    system_message: Optional[str] = "You are a friendly chatbot who always responds in the style of a python developer that uses a combination of natural language and markdown to answer questions."
```
CodeDocQuery is the experimental model to teach zephyr how to recognize python and create markdown explanations of the code characteristics.

The code str is formatted by the ['black'](https://pypi.org/project/black/) code formatter

```bash
pip install black
```
The pip install is covered in the setup.

```python
class CodeDocQuery(BaseModel):
    code: str
    language: Optional[str] = "python"  # default to python, but allow for other languages if you plan on expanding
    include_comments: Optional[bool] = True # whether to generate comments for the code
    max_new_tokens: int = 256
    do_sample: bool = True
    temperature: float = 0.7
    top_k: int = 50
    top_p: float = 0.95
```

### Welcome Endpoint

Access the root of the API:

- **GET /**: returns a welcome screen with descriptions of the currently available endpoints
- **POST**: /zephyr/raw Returns unstructured output with system prompt and tokens still in place.

### Pythonic Chatbot Response

This endpoint provides a response that is a blend of natural language and structured python output:

```
POST /zephyr/python
```
Payload:

```json

{
  "user_message": "string",
  "max_new_tokens": 256,
  "do_sample": true,
  "temperature": 0.7,
  "top_k": 50,
  "top_p": 0.95,
}
```
## Custom System Message

If you want to control the system message for yourself:
```
POST /zephyr/system-message
```

Payload:

```json

{
  "user_message": "Your message here",
  "system_message": "Your custom system message here",
  "max_new_tokens": 256,
  "do_sample": true,
  "temperature": 0.7,
  "top_k": 50,
  "top_p": 0.95
}
```

## Markdown Document Creators

These two endpoints are fairly similar, but for right now the Structured Code Documentation functions more predictably.

For the best results with either of these you will want to make sure that the "code" parameter or the "user_message" parameter is is formatted so that all the text is on one line.

**This is different than JSONL**

JSONL has the entire entry on one line, whereas this requires only long context inputs to be formatted on one line. This is subject to change. If you wish to change both the client-side and server-side to JSONL that is fine you just need to add lines=True in the corresponding positions.

**Client side and server side must both be in the same format.**

### Markdown Code Documentation Creator

Get markdown documentation for provided code:
```
POST /zephyr/code-doc
```
Payload:

```json
{
  "code": "outputs = pipe(prompt, max_new_tokens=query.max_new_tokens, do_sample=query.do_sample, temperature=query.temperature, top_k=query.top_k, top_p=query.top_p)",
  "language": "python",
  "include_comments": true,
  "max_new_tokens": 256,
  "do_sample": true,
  "temperature": 0.7,
  "top_k": 50,
  "top_p": 0.95
}
```
### Structured Code Documentation

This endpoint is similar to the markdown code documentation creator, but it has a predefined structure that it will follow to generate.
```
POST /zephyr/structured-code-doc
```
Payload:

```json

{
  "user_message": "outputs = pipe(prompt, max_new_tokens=query.max_new_tokens, do_sample=query.do_sample, temperature=query.temperature, top_k=query.top_k, top_p=query.top_p)",
  "max_new_tokens": 256,
  "do_sample": true,
  "temperature": 0.7,
  "top_k": 50,
  "top_p": 0.95,
  "system_message": "You are a friendly chatbot who always responds in the style of a python developer that uses a combination of natural language and markdown to answer questions."
}
```
## Statistics

### Live GPU Usage Stats

Connect via a WebSocket to get live GPU usage statistics when querying the model:
```
ws://localhost:8000/zephyr/ws/gpu-stats"
```

## Front-End Features

- Pseudo streaming implemented with live updating of the model output.
- Session state and chat memory
- Dynamic configurations

## Known Issues 

The websocket feature is experimental and may not work properly.

Remember that this is a 7b parameter model and may very well have issues or generate harmful content. All responsibility falls to the end-user. 