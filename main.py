from fastapi import FastAPI
import os

app = FastAPI()


@app.get("/")
@app.get("/{param}")
async def docroot(param=""):
    return "And They Have a Plan"
