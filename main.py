from sys import prefix

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from middlewares.exception_handler import ExceptionHandlerMiddleware
from routes import series

app = FastAPI()

# Configura CORS para permitir todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middlewares
app.add_middleware(ExceptionHandlerMiddleware)

# Routes
app.include_router(series.router, prefix="/api/series", tags=["Series: donghua - anime"])


