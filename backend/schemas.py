from typing import Optional, List
from pydantic import BaseModel, conint, PositiveFloat


# ---------- Products ----------

class ProductBase(BaseModel):
    product_name: str
    article: conint(ge=0)
    min_partner_cost: float
    product_type_name: Optional[str] = None
    main_material_name: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    product_id: int
    total_production_time: int

    class Config:
        from_attributes = True


# ---------- Workshops ----------

class WorkshopOut(BaseModel):
    workshop_name: str
    workshop_type: str
    num_employees: int
    time_in_workshop: float

    class Config:
        from_attributes = True


# ---------- Raw material calculation ----------

class RawMaterialRequest(BaseModel):
    product_type_name: str
    material_name: str
    quantity: conint(ge=0)
    param1: PositiveFloat
    param2: PositiveFloat


class RawMaterialResponse(BaseModel):
    required_raw_material: int


# ---------- Dictionaries ----------

class ProductTypeOut(BaseModel):
    product_type_name: str

    class Config:
        from_attributes = True


class MaterialOut(BaseModel):
    material_name: str

    class Config:
        from_attributes = True

