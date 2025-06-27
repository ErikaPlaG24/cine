from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.reserved_seats.get_all_reserved_seats import get_all_reserved_seats_controller
from controllers.reserved_seats.get_reserved_seat_by_id import get_reserved_seat_by_id_controller
from controllers.reserved_seats.create_reserved_seat import create_reserved_seat_controller
from controllers.reserved_seats.update_reserved_seat_by_id import update_reserved_seat_by_id_controller
from controllers.reserved_seats.delete_reserved_seat_by_id import delete_reserved_seat_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_reserved_seats(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_reserved_seats_controller(data)

@router.post("/by_id")
async def get_reserved_seat_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_reserved_seat_by_id_controller(data)

@router.post("/create")
async def create_reserved_seat(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_reserved_seat_controller(data)

@router.put("/update")
async def update_reserved_seat_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_reserved_seat_by_id_controller(data)

@router.delete("/delete")
async def delete_reserved_seat_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_reserved_seat_by_id_controller(data)
