from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db
from .routes import products_router, categories_router, cart_router
import uvicorn


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    debug=settings.debug,
    docs_url='/api/docs',
    redoc_url='/api/redoc',
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')

app.include_router(products_router)
app.include_router(categories_router)
app.include_router(cart_router)


@app.get('/')
def root():
    return {
        'message': 'Welcome to FastAPI shop API',
        'docs': 'api/docs',
    }


@app.get('/health')
def health_check():
    return {'status': 'healthy'}