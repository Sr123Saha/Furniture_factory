from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ProductType(Base):
    __tablename__ = "ProductTypes"
    product_type_name = Column(String, primary_key=True, index=True) 
    type_coefficient = Column(Float)
    products = relationship("Product", back_populates="product_type")

class Material(Base):
    __tablename__ = "Materials"
    material_name = Column(String, primary_key=True, index=True)
    loss_percentage = Column(Float)
    products = relationship("Product", back_populates="main_material")

class Product(Base):
    __tablename__ = "Products"
    product_name = Column(String, primary_key=True, index=True) 
    article = Column(Integer)
    
    min_partner_cost_db = Column("Минимальная стоимость для партнера", String) 

    product_type_name = Column(String, ForeignKey("ProductTypes.product_type_name"))
    main_material_name = Column(String, ForeignKey("Materials.material_name"))

    product_type = relationship("ProductType", back_populates="products")
    main_material = relationship("Material", back_populates="products")
    product_workshops = relationship("ProductWorkshop", back_populates="product")

class Workshop(Base):
    __tablename__ = "Workshops"
    workshop_name = Column(String, primary_key=True, index=True)
    workshop_type = Column(String)
    employees = Column(Integer)
    workshop_products = relationship("ProductWorkshop", back_populates="workshop")

class ProductWorkshop(Base):
    __tablename__ = "ProductWorkshops"
    
    product_name = Column(String, ForeignKey("Products.product_name"), primary_key=True)
    workshop_name = Column(String, ForeignKey("Workshops.workshop_name"), primary_key=True)
    
    time_in_hours_db = Column("Время изготовления, ч", String) 
    

    product = relationship("Product", back_populates="product_workshops")
    workshop = relationship("Workshop", back_populates="workshop_products")