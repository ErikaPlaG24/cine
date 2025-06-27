from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.theaters.get_all_theaters import get_all_theaters_controller
from controllers.theaters.get_theater_by_id import get_theater_by_id_controller
from controllers.theaters.create_theater import create_theater_controller
from controllers.theaters.update_theater_by_id import update_theater_by_id_controller
from controllers.theaters.delete_theater_by_id import delete_theater_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_theaters(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_theaters_controller(data)

@router.post("/by_id")
async def get_theater_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_theater_by_id_controller(data)

@router.post("/create")
async def create_theater(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_theater_controller(data)

@router.put("/update")
async def update_theater_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_theater_by_id_controller(data)

@router.delete("/delete")
async def delete_theater_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_theater_by_id_controller(data)
