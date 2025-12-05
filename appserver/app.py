from fastapi import FastAPI
from .apps.account.endpoints import router as account_router

app = FastAPI()

def include_routers(_app: FastAPI):
    _app.include_router(account_router)

# app.include_router(account_router)

@app.get("/")
def hello_world() -> dict:
    return {"message": "Hello World"}