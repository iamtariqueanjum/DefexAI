from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/code/review")
async def review_code(request: Request):
    data = await request.json()
    print("Webhook Triggered from GitHub!")
    print("Payload:", data)
    return {"status": "success"}
