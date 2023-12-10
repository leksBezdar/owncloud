from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import router as api_router
from src.auth.routers import router as auth_router


app = FastAPI()

origins = [
    "*"
]

# Добавление middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, tags=["api"])
app.include_router(auth_router, tags=["auth"])


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return f"""
    <a href="{str(request.url)}docs"><h1>Documentation</h1></a><br>
    <a href="{str(request.url)}redoc"><h1>ReDoc</h1></a>
    """
