
import os

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return "Website is healthy."


api_port = int(os.environ.get("API_PORT"))

if __name__ == "__main__" and api_port:
    print("Starting uvicorn")
    uvicorn.run(app, workers=1, host="0.0.0.0", port=api_port, log_level="error")
