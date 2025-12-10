from models import ProductWorkshop 
from typing import Optional
import math
from sqlalchemy.orm import Session

def calculate_total_time(db: Session, product_name: str) -> Optional[int]:
    """
    Реализует алгоритм: рассчитывает общее время изготовления (SUM) и округляет до целого.
    """

    time_column_name = "Время изготовления, ч" 

    results = db.query(ProductWorkshop).filter(
        ProductWorkshop.product_name == product_name
    ).all()

    if not results:
        return None

    total_time = 0.0

    for pw in results:
        time_str = getattr(pw, time_column_name) 

        try:
            cleaned_time = float(time_str.replace(',', '.'))
            total_time += cleaned_time
        except (ValueError, AttributeError):
            continue

    final_time = math.ceil(total_time) 

    return int(final_time)