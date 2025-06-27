from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.users.get_all_users import get_all_users_controller
from controllers.users.get_all_actived_users import get_all_active_users_controller
from controllers.users.get_if_user_is_active_by_id import get_if_user_is_active_by_id_controller
from controllers.users.get_id_by_username import get_id_by_username_controller
from controllers.users.get_value_from_user_by_id import get_value_from_user_by_id_controller
from controllers.users.search_user_by_name import search_user_by_name_controller
from controllers.users.get_if_user_exists import get_if_user_exists_controller
from controllers.users.create_user import create_user_controller
from controllers.users.update_user_by_id import update_user_by_id_controller
from controllers.users.delete_user_by_id import delete_user_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_users(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_users_controller(data)

@router.get("/all_active")
async def get_all_active_users(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_active_users_controller(data)

@router.post("/is_active")
async def is_user_active(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_if_user_is_active_by_id_controller(data)

@router.post("/id_by_username")
async def get_id_by_username_route(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_id_by_username_controller(data)

@router.post("/value_by_id")
async def get_value_from_user_by_id_route(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_value_from_user_by_id_controller(data)

@router.post("/search")
async def search_user_by_name_route(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return search_user_by_name_controller(data)

@router.post("/exists")
async def get_if_user_exists_route(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_if_user_exists_controller(data)

@router.post("/create")
async def create_user_route(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_user_controller(data)

@router.put("/update")
async def update_user_by_id_route(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_user_by_id_controller(data)

@router.delete("/delete")
async def delete_user_by_id_route(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_user_by_id_controller(data)
