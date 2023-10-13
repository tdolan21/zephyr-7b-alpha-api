# zephyr-7b-alpha-api

This repo contains an api with postgreSQL database for the zephyr-7b-alpha model from Huggingface. In the future it may also contain a demo application.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.3-blue)
![Docker](https://img.shields.io/badge/docker-latest-blue.svg)
![Huggingface](https://img.shields.io/badge/Huggingface-Transformers-orange)


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
cd zephyr-api
uvicorn api:app --reload
cd ../zephyr-chat
streamlit run app.py
```
After this the api and the application will be available at:
```
http://localhost:8000
http://localhost:8501
```
## Usage 

### Welcome Endpoint

Access the root of the API:

GET /: returns a welcome screen
POST /zephyr/raw

- Returns unstructured output with system prompt and tokens still in place.

### Pythonic Chatbot Response

This endpoint provides a response that is a blend of natural language and structured python output:

```
POST /zephyr/python
```
Payload:

```json

{
  "user_message": "Your message here",
  "max_new_tokens": 256,
  "do_sample": true,
  "temperature": 0.7,
  "top_k": 50,
  "top_p": 0.95
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
  "function_name": "Your function name here",
  "return_type": "Return type of the function",
  "max_new_tokens": 256,
  "do_sample": true,
  "temperature": 0.7,
  "top_k": 50,
  "top_p": 0.95
}
```
### Live GPU Usage Stats

Connect via a WebSocket to get live GPU usage statistics when querying the model:
```
WebSocket /zephyr/ws/gpu-stats
```