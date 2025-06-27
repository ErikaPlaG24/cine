from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.showtimes.get_all_showtimes import get_all_showtimes_controller
from controllers.showtimes.get_showtime_by_id import get_showtime_by_id_controller
from controllers.showtimes.create_showtime import create_showtime_controller
from controllers.showtimes.update_showtime_by_id import update_showtime_by_id_controller
from controllers.showtimes.delete_showtime_by_id import delete_showtime_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_showtimes(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_showtimes_controller(data)

@router.post("/by_id")
async def get_showtime_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_showtime_by_id_controller(data)

@router.post("/create")
async def create_showtime(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_showtime_controller(data)

@router.put("/update")
async def update_showtime_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_showtime_by_id_controller(data)

@router.delete("/delete")
async def delete_showtime_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_showtime_by_id_controller(data)
