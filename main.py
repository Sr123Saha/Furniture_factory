import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from fastapi import FastAPI, Depends, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db 
from services import crud, calculation 
from schemas import ProductCreate, Product
from typing import List

app = FastAPI(title="Подсистема Управления Продукцией")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, summary="Главная страница со списком продукции")
def read_products_page(request: Request, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    products_data = []
    for product_orm in products:
        total_time = calculation.calculate_total_time(db, product_orm.product_name)
        product_dict = product_orm.__dict__
        product_dict['total_time_hours'] = total_time if total_time is not None else 0
        products_data.append(product_dict)

    return templates.TemplateResponse(
        "products_list.html",
        {"request": request, "products": products_data}
    )

