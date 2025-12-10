# services/crud.py

from models import Product, Workshop, ProductWorkshop, ProductType, Material
from schemas import ProductCreate 
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Импортируем функцию расчета времени из соседнего файла внутри services
from .calculation import calculate_total_time 

# -------------------------------------------------------------------
# A. ЧТЕНИЕ (READ)
# -------------------------------------------------------------------
def get_products(db: Session, skip: int = 0, limit: int = 100):
    """Возвращает список всей продукции."""
    return db.query(Product).offset(skip).limit(limit).all()

def get_all_workshops(db: Session):
    """Возвращает полный список всех цехов."""
    return db.query(Workshop).all()


# -------------------------------------------------------------------
# B. ДОБАВЛЕНИЕ (CREATE)
# -------------------------------------------------------------------
def create_product(db: Session, product_data: ProductCreate):
    """
    Создает новую продукцию в таблице Products и связи в ProductWorkshops.
    """
    try:
        # 1. Создание записи в таблице Products
        db_product = Product(
            product_name=product_data.product_name,
            article=product_data.article,
            min_partner_cost_db=product_data.min_partner_cost_db, 
            product_type_name=product_data.product_type_name,
            main_material_name=product_data.main_material_name
        )
        db.add(db_product)
        db.flush() 

        # 2. Создание связей в таблице ProductWorkshops
        time_column_key = "Время изготовления, ч" 
        for workshop_info in product_data.workshop_times:

            db_pw = ProductWorkshop(
                product_name=product_data.product_name,
                workshop_name=workshop_info['workshop_name'],
                time_in_hours_db=workshop_info.get(time_column_key) 
            )
            db.add(db_pw)

        db.commit() 
        db.refresh(db_product) 
        return db_product

    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Ошибка целостности данных: продукт, тип или материал, возможно, уже существуют или не найдены. {e}")