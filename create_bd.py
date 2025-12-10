import sqlite3
import pandas as pd
import os

DB_NAME = 'furniture_production.db'

CSV_DIR = 'data' 
FILES = {
    'ProductTypes': 'Product_type_import.csv',
    'Materials': 'Material_type_import.csv',
    'Workshops': 'Workshops_import.csv', 
    'Products': 'Products_import.csv',
    'ProductWorkshops': 'Product_workshops_import.csv'
}

SQL_SETUP = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS ProductTypes (
    product_type_name TEXT PRIMARY KEY,
    type_coefficient REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS Materials (
    material_name TEXT PRIMARY KEY,
    loss_percentage REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS Workshops (
    workshop_name TEXT PRIMARY KEY,
    workshop_type TEXT NOT NULL,
    num_employees INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    article INTEGER UNIQUE NOT NULL,
    min_partner_cost REAL NOT NULL,
    
    product_type_name TEXT, 
    main_material_name TEXT,
    
    FOREIGN KEY (product_type_name) REFERENCES ProductTypes(product_type_name) 
        ON DELETE RESTRICT,
    FOREIGN KEY (main_material_name) REFERENCES Materials(material_name) 
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ProductWorkshops (
    product_name TEXT NOT NULL,
    workshop_name TEXT NOT NULL,
    coefficient REAL NOT NULL,
    
    PRIMARY KEY (product_name, workshop_name),
    
    FOREIGN KEY (product_name) REFERENCES Products(product_name) 
        ON DELETE CASCADE,
    FOREIGN KEY (workshop_name) REFERENCES Workshops(workshop_name) 
        ON DELETE RESTRICT
);
"""

def create_db_and_tables(conn):
    """Создание БД и всех таблиц."""
    print("Создание базы данных и таблиц...")
    cursor = conn.cursor()
    cursor.executescript(SQL_SETUP)
    conn.commit()
    print("База данных и таблицы созданы успешно.")

def load_data(conn, table_name, csv_file, column_mapping):
    """Загрузка данных из CSV в таблицу."""
    print(f"\nЗагрузка данных в таблицу {table_name} из {csv_file}...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, csv_file), sep=';') 
        
        df = df.rename(columns=column_mapping)
        
        df.to_sql(
            table_name, 
            conn, 
            if_exists='replace', 
            index=False
        )
        print(f"Успешно загружено {len(df)} записей в {table_name}.")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл {csv_file} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при загрузке данных в {table_name}: {e}")


if __name__ == '__main__':
    conn = sqlite3.connect(DB_NAME)
    
    conn.execute("PRAGMA foreign_keys = ON;") 
    
    create_db_and_tables(conn)
    
    load_data(conn, 'ProductTypes', FILES['ProductTypes'], {
        'Тип продукции': 'product_type_name',
        'Коэффициент типа продукции': 'type_coefficient'
    })

    load_data(conn, 'Materials', FILES['Materials'], {
        'Тип материала': 'material_name',
        'Процент потерь сырья': 'loss_percentage'
    })
    
    load_data(conn, 'Workshops', FILES['Workshops'], {
        'Название цеха': 'workshop_name',
        'Тип цеха': 'workshop_type',
        'Количество человек для производства': 'num_employees'
    })
    
    load_data(conn, 'Products', FILES['Products'], {
        'Наименование продукции': 'product_name',
        'Тип продукции': 'product_type_name',
        'Артикул': 'article',
        'Минимальная стоимость для партнер': 'min_partner_cost',
        'Основной материал': 'main_material_name'
    })

    load_data(conn, 'ProductWorkshops', FILES['ProductWorkshops'], {
        'Наименование продукции': 'product_name',
        'Название цеха': 'workshop_name',
        'Коэффициент': 'coefficient'
    })

    conn.close()
    print("\nПроцесс загрузки завершен. База данных furniture_production.db готова.")