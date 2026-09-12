from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import invoice
from app.database import engine
from app import models


app = FastAPI(
    title="Intelligent Invoice Analysis and Fraud Detection API",
    version="1.0.0",
    description="Backend API for invoice processing and fraud detection"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

models.Base.metadata.create_all(
    bind=engine
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth.router)

app.include_router(
    invoice.router,
    prefix="/invoices",
    tags=["Invoices"]
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message":
            "Welcome to Intelligent Invoice Analysis and Fraud Detection API"
    }