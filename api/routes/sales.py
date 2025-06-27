from typing import *
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from controllers.sales.get_all_sales import get_all_sales_controller
from controllers.sales.get_sale_by_id import get_sale_by_id_controller
from controllers.sales.create_sale import create_sale_controller
from controllers.sales.update_sale_by_id import update_sale_by_id_controller
from controllers.sales.delete_sale_by_id import delete_sale_by_id_controller
from helpers.token import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user_dep(token: str = Depends(oauth2_scheme)):
    return get_current_user(token)

@router.get("/all")
async def get_all_sales(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_all_sales_controller(data)

@router.post("/by_id")
async def get_sale_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return get_sale_by_id_controller(data)

@router.post("/create")
async def create_sale(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return create_sale_controller(data)

@router.put("/update")
async def update_sale_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return update_sale_by_id_controller(data)

@router.delete("/delete")
async def delete_sale_by_id(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(current_user_dep)
):
    return delete_sale_by_id_controller(data)
