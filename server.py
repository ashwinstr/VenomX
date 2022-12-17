from fastapi import FastAPI
import uvicorn
import asyncio
import os

app = FastAPI()

@app.get("/")
async def read_root():
    return "website is healthy."

api_port=os.environ.get("API_PORT")

if __name__=="__main__" and api_port:
    print("starting uvicorn")
    uvicorn.run(app,workers=1,host ="0.0.0.0" ,port=api_port,log_level="error")
