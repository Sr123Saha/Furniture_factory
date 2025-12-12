from typing import Optional, List
from pydantic import BaseModel, conint, PositiveFloat



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



class WorkshopOut(BaseModel):
    workshop_name: str
    workshop_type: str
    num_employees: int
    time_in_workshop: float

    class Config:
        from_attributes = True



class RawMaterialRequest(BaseModel):
    product_type_name: str
    material_name: str
    quantity: conint(ge=0)
    param1: PositiveFloat
    param2: PositiveFloat


class RawMaterialResponse(BaseModel):
    required_raw_material: int



class ProductTypeOut(BaseModel):
    product_type_name: str

    class Config:
        from_attributes = True


class MaterialOut(BaseModel):
    material_name: str

    class Config:
        from_attributes = True


class ProductTypeFullOut(BaseModel):
    product_type_name: str
    type_coefficient: float

    class Config:
        from_attributes = True


class MaterialFullOut(BaseModel):
    material_name: str
    loss_percentage: float

    class Config:
        from_attributes = True


class WorkshopFullOut(BaseModel):
    workshop_name: str
    workshop_type: str
    num_employees: int

    class Config:
        from_attributes = True


class ProductWorkshopOut(BaseModel):
    product_name: str
    workshop_name: str
    coefficient: float

    class Config:
        from_attributes = True

