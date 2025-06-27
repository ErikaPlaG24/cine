from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.memberships.get_all_memberships import get_all_memberships_controller
from controllers.memberships.get_membership_by_id import get_membership_by_id_controller
from controllers.memberships.create_membership import create_membership_controller
from controllers.memberships.update_membership_by_id import update_membership_by_id_controller
from controllers.memberships.delete_membership_by_id import delete_membership_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_memberships(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_memberships_controller(data)

@router.post("/by_id")
async def get_membership_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_membership_by_id_controller(data)

@router.post("/create")
async def create_membership(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_membership_controller(data)

@router.put("/update")
async def update_membership_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_membership_by_id_controller(data)

@router.delete("/delete")
async def delete_membership_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_membership_by_id_controller(data)
