from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.customer_memberships.get_all_customer_memberships import get_all_customer_memberships_controller
from controllers.customer_memberships.get_customer_membership_by_id import get_customer_membership_by_id_controller
from controllers.customer_memberships.create_customer_membership import create_customer_membership_controller
from controllers.customer_memberships.update_customer_membership_by_id import update_customer_membership_by_id_controller
from controllers.customer_memberships.delete_customer_membership_by_id import delete_customer_membership_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_customer_memberships(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_customer_memberships_controller(data)

@router.post("/by_id")
async def get_customer_membership_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_customer_membership_by_id_controller(data)

@router.post("/create")
async def create_customer_membership(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_customer_membership_controller(data)

@router.put("/update")
async def update_customer_membership_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_customer_membership_by_id_controller(data)

@router.delete("/delete")
async def delete_customer_membership_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_customer_membership_by_id_controller(data)
