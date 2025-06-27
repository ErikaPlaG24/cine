from typing import *
from fastapi import APIRouter, Body
from controllers.auth.login import login_controller
from controllers.auth.refresh import refresh_token_controller

router = APIRouter()

# Recibir JSON directamente en el body
@router.post("/login")
async def login(data: Dict[str, Any] = Body(...)):
    return login_controller(data)

@router.post("/refresh")
async def refresh_token(data: Dict[str, Any] = Body(...)):
    return refresh_token_controller(data)