from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session
import os

from .database import get_db, engine
from . import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Furniture Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ---------- Products ----------

@app.get("/products", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    out: List[schemas.ProductOut] = []
    for p in products:
        time_sum = sum(pw.coefficient for pw in p.workshops)
        total_time = int(round(max(time_sum, 0)))
        out.append(
            schemas.ProductOut(
                product_id=p.product_id,
                product_name=p.product_name,
                article=p.article,
                min_partner_cost=p.min_partner_cost,
                product_type_name=p.product_type_name,
                main_material_name=p.main_material_name,
                total_production_time=total_time,
            )
        )
    return out


@app.post("/products", response_model=schemas.ProductOut)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    # проверка уникальности артикула
    exists = db.query(models.Product).filter(models.Product.article == product_in.article).first()
    if exists:
        raise HTTPException(status_code=400, detail="Артикул уже существует")

    product = models.Product(
        product_name=product_in.product_name,
        article=product_in.article,
        min_partner_cost=float(product_in.min_partner_cost),
        product_type_name=product_in.product_type_name,
        main_material_name=product_in.main_material_name,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    time_sum = sum(pw.coefficient for pw in product.workshops)
    total_time = int(round(max(time_sum, 0)))
    return schemas.ProductOut(
        product_id=product.product_id,
        product_name=product.product_name,
        article=product.article,
        min_partner_cost=product.min_partner_cost,
        product_type_name=product.product_type_name,
        main_material_name=product.main_material_name,
        total_production_time=total_time,
    )


@app.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product_in: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # проверка уникальности артикула
    same_article = (
        db.query(models.Product)
        .filter(models.Product.article == product_in.article, models.Product.product_id != product_id)
        .first()
    )
    if same_article:
        raise HTTPException(status_code=400, detail="Артикул уже существует")

    product.product_name = product_in.product_name
    product.article = product_in.article
    product.min_partner_cost = float(product_in.min_partner_cost)
    product.product_type_name = product_in.product_type_name
    product.main_material_name = product_in.main_material_name

    db.commit()
    db.refresh(product)

    time_sum = sum(pw.coefficient for pw in product.workshops)
    total_time = int(round(max(time_sum, 0)))
    return schemas.ProductOut(
        product_id=product.product_id,
        product_name=product.product_name,
        article=product.article,
        min_partner_cost=product.min_partner_cost,
        product_type_name=product.product_type_name,
        main_material_name=product.main_material_name,
        total_production_time=total_time,
    )


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}


# ---------- Workshops ----------

@app.get("/products/{product_id}/workshops", response_model=List[schemas.WorkshopOut])
def get_product_workshops(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    out: List[schemas.WorkshopOut] = []
    for pw in product.workshops:
        out.append(
            schemas.WorkshopOut(
                workshop_name=pw.workshop.workshop_name,
                workshop_type=pw.workshop.workshop_type,
                num_employees=pw.workshop.num_employees,
                time_in_workshop=pw.coefficient,
            )
        )
    return out


@app.get("/products/{product_id}/production_time")
def get_production_time(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    total = int(round(max(sum(pw.coefficient for pw in product.workshops), 0)))
    return {"product_id": product_id, "total_production_time": total}


# ---------- Dictionaries ----------

@app.get("/product-types", response_model=List[schemas.ProductTypeOut])
def get_product_types(db: Session = Depends(get_db)):
    types = db.query(models.ProductType).all()
    return [schemas.ProductTypeOut(product_type_name=t.product_type_name) for t in types]


@app.get("/materials", response_model=List[schemas.MaterialOut])
def get_materials(db: Session = Depends(get_db)):
    materials = db.query(models.Material).all()
    return [schemas.MaterialOut(material_name=m.material_name) for m in materials]


@app.get("/all-product-types", response_model=List[schemas.ProductTypeFullOut])
def get_all_product_types(db: Session = Depends(get_db)):
    types = db.query(models.ProductType).all()
    return [schemas.ProductTypeFullOut(product_type_name=t.product_type_name, type_coefficient=t.type_coefficient) for t in types]


@app.get("/all-materials", response_model=List[schemas.MaterialFullOut])
def get_all_materials(db: Session = Depends(get_db)):
    materials = db.query(models.Material).all()
    return [schemas.MaterialFullOut(material_name=m.material_name, loss_percentage=m.loss_percentage) for m in materials]


@app.get("/all-workshops", response_model=List[schemas.WorkshopFullOut])
def get_all_workshops(db: Session = Depends(get_db)):
    workshops = db.query(models.Workshop).all()
    return [schemas.WorkshopFullOut(workshop_name=w.workshop_name, workshop_type=w.workshop_type, num_employees=w.num_employees) for w in workshops]


@app.get("/all-product-workshops", response_model=List[schemas.ProductWorkshopOut])
def get_all_product_workshops(db: Session = Depends(get_db)):
    pw_list = db.query(models.ProductWorkshop).all()
    return [schemas.ProductWorkshopOut(product_name=pw.product_name, workshop_name=pw.workshop_name, coefficient=pw.coefficient) for pw in pw_list]


@app.get("/product-workshops/{product_id}", response_model=List[schemas.ProductWorkshopOut])
def get_product_workshops_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    pw_list = db.query(models.ProductWorkshop).filter(models.ProductWorkshop.product_name == product.product_name).all()
    return [schemas.ProductWorkshopOut(product_name=pw.product_name, workshop_name=pw.workshop_name, coefficient=pw.coefficient) for pw in pw_list]


# ---------- Raw material calculation ----------

@app.post("/calculate_raw_material", response_model=schemas.RawMaterialResponse)
def calculate_raw_material(req: schemas.RawMaterialRequest, db: Session = Depends(get_db)):
    product_type = (
        db.query(models.ProductType)
        .filter(models.ProductType.product_type_name == req.product_type_name)
        .first()
    )
    material = (
        db.query(models.Material)
        .filter(models.Material.material_name == req.material_name)
        .first()
    )
    if not product_type or not material:
        return schemas.RawMaterialResponse(required_raw_material=-1)

    base_per_unit = req.param1 * req.param2 * product_type.type_coefficient
    total_base = base_per_unit * req.quantity
    loss_coeff = 1 + material.loss_percentage / 100.0
    total_with_loss = total_base * loss_coeff
    required_raw = int(round(max(total_with_loss, 0)))
    return schemas.RawMaterialResponse(required_raw_material=required_raw)

