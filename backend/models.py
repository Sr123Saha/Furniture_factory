from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class ProductType(Base):
    __tablename__ = "ProductTypes"

    product_type_name = Column(String, primary_key=True)
    type_coefficient = Column(Float, nullable=False)

    products = relationship("Product", back_populates="product_type")


class Material(Base):
    __tablename__ = "Materials"

    material_name = Column(String, primary_key=True)
    loss_percentage = Column(Float, nullable=False)

    products = relationship("Product", back_populates="material")


class Workshop(Base):
    __tablename__ = "Workshops"

    workshop_name = Column(String, primary_key=True)
    workshop_type = Column(String, nullable=False)
    num_employees = Column(Integer, nullable=False)

    product_workshops = relationship("ProductWorkshop", back_populates="workshop")


class Product(Base):
    __tablename__ = "Products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False, unique=True)
    article = Column(Integer, nullable=False, unique=True)
    min_partner_cost = Column(Float, nullable=False)
    product_type_name = Column(String, ForeignKey("ProductTypes.product_type_name"))
    main_material_name = Column(String, ForeignKey("Materials.material_name"))

    product_type = relationship("ProductType", back_populates="products")
    material = relationship("Material", back_populates="products")
    workshops = relationship("ProductWorkshop", back_populates="product")


class ProductWorkshop(Base):
    __tablename__ = "ProductWorkshops"

    product_name = Column(String, ForeignKey("Products.product_name"), primary_key=True)
    workshop_name = Column(String, ForeignKey("Workshops.workshop_name"), primary_key=True)
    coefficient = Column(Float, nullable=False)

    product = relationship("Product", back_populates="workshops")
    workshop = relationship("Workshop", back_populates="product_workshops")

