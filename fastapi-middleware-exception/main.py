from fastapi import FastAPI,Request
import time
import asyncio

app = FastAPI()

@app.middleware('http')
async def first_middleware(request:Request,call_next):
    print("Before Processing Request")
    print("Method of the request " + request.method)
    print("URL Path of the request " + request.url.path)

    response = await call_next(request)

    print("After Processing Request")
    
    return response


@app.get("/hello")
async def hello_world():
    await asyncio.sleep(10)
    return {
  "message": "Hello, Welcome to FastAPI!"
}


