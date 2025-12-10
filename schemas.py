from pydantic import BaseModel, Field, ConfigDict
from typing import List

class ProductWorkshopRead(BaseModel):
    time_in_hours_db: str
    workshop_name: str
    model_config = ConfigDict(from_attributes=True) 

class Product(BaseModel):
    product_name: str
    article: int
    min_partner_cost_db: str 
    product_type_name: str
    main_material_name: str
    product_workshops: List[ProductWorkshopRead]
    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    product_name: str = Field(..., json_schema_extra={'example': "Диван 'Новый'"})
    article: int = Field(..., json_schema_extra={'example': 5050})
    
    min_partner_cost_db: str = Field(
        ..., 
        alias="Минимальная стоимость для партнера", 
        json_schema_extra={'example': "15000,50"}
    )
    
    product_type_name: str = Field(..., json_schema_extra={'example': "Мягкая мебель"})
    main_material_name: str = Field(..., json_schema_extra={'example': "Дерево"})

    workshop_times: List[dict] = Field(
        ..., 
        json_schema_extra={'example': [
            {"workshop_name": "Раскроя", "Время изготовления, ч": "0,5"},
            {"workshop_name": "Сборки", "Время изготовления, ч": "2,0"}
        ]}
    )