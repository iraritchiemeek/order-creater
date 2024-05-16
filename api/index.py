from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()
client = OpenAI()

@app.get("/api/chat")
async def chat(request: Request):
    user_message = request.query_params.get("message")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}]
    )
    return {"response": response.choices[0].message.content}

