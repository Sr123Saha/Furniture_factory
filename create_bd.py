"""
Создание SQLite базы и загрузка данных из CSV.
"""
import os
import sqlite3
import pandas as pd

DB_NAME = "furniture_production.db"
CSV_DIR = "data"

FILES = {
    "ProductTypes": "Product_type_import.csv",
    "Materials": "Material_type_import.csv",
    "Workshops": "Workshops_import.csv",
    "Products": "Products_import.csv",
    "ProductWorkshops": "Product_workshops_import.csv",
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
    product_name TEXT NOT NULL UNIQUE,
    article INTEGER UNIQUE NOT NULL,
    min_partner_cost REAL NOT NULL,
    product_type_name TEXT,
    main_material_name TEXT,
    FOREIGN KEY (product_type_name) REFERENCES ProductTypes(product_type_name) ON DELETE RESTRICT,
    FOREIGN KEY (main_material_name) REFERENCES Materials(material_name) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ProductWorkshops (
    product_name TEXT NOT NULL,
    workshop_name TEXT NOT NULL,
    coefficient REAL NOT NULL,
    PRIMARY KEY (product_name, workshop_name),
    FOREIGN KEY (product_name) REFERENCES Products(product_name) ON DELETE CASCADE,
    FOREIGN KEY (workshop_name) REFERENCES Workshops(workshop_name) ON DELETE RESTRICT
);
"""


def _to_float(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .replace({"": None, "nan": None, "None": None})
        .apply(lambda x: pd.to_numeric(x, errors="coerce"))
    )


def create_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(SQL_SETUP)
    conn.commit()


def load_table(conn: sqlite3.Connection, table: str, csv_file: str, mapping: dict, preprocess=None) -> None:
    print(f"Загрузка {table} из {csv_file}")
    path = os.path.join(CSV_DIR, csv_file)
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df = df.dropna(how="all")
    df = df[~df.apply(lambda x: x.astype(str).str.strip().eq("").all(), axis=1)]
    df = df.rename(columns=mapping)
    if preprocess:
        df = preprocess(df)
    df = df.dropna(how="all")

    conn.execute(f"DELETE FROM {table};")
    df.to_sql(table, conn, if_exists="append", index=False)
    print(f"  → {len(df)} записей")


def preprocess_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["product_type_name"])
    df["product_type_name"] = df["product_type_name"].str.strip()
    df["type_coefficient"] = _to_float(df["type_coefficient"])
    df = df.dropna(subset=["type_coefficient"])
    return df


def preprocess_materials(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["material_name"])
    df["material_name"] = df["material_name"].str.strip()
    df["loss_percentage"] = _to_float(df["loss_percentage"])
    df = df.dropna(subset=["loss_percentage"])
    return df


def preprocess_workshops(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["workshop_name"])
    df["workshop_name"] = df["workshop_name"].str.strip()
    df["workshop_type"] = df["workshop_type"].str.strip()
    df["num_employees"] = pd.to_numeric(df["num_employees"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["num_employees"])
    return df


def preprocess_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["product_name"])
    df["product_name"] = df["product_name"].str.strip()
    df.insert(0, "product_id", range(1, len(df) + 1))
    df["article"] = pd.to_numeric(df["article"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["article"])
    df["min_partner_cost"] = _to_float(df["min_partner_cost"])
    df = df.dropna(subset=["min_partner_cost"])
    if "product_type_name" in df.columns:
        df["product_type_name"] = df["product_type_name"].astype(str).str.strip().replace({"": None})
    if "main_material_name" in df.columns:
        df["main_material_name"] = df["main_material_name"].astype(str).str.strip().replace({"": None})
    return df


def preprocess_product_workshops(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["product_name", "workshop_name"])
    df["product_name"] = df["product_name"].str.strip()
    df["workshop_name"] = df["workshop_name"].str.strip()
    df["coefficient"] = _to_float(df["coefficient"])
    df = df.dropna(subset=["coefficient"])
    return df


def main():
    if not os.path.exists(CSV_DIR):
        raise FileNotFoundError("Каталог data с CSV не найден")

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    create_db(conn)

    load_table(
        conn,
        "ProductTypes",
        FILES["ProductTypes"],
        {"Тип продукции": "product_type_name", "Коэффициент типа продукции": "type_coefficient"},
        preprocess=preprocess_types,
    )

    load_table(
        conn,
        "Materials",
        FILES["Materials"],
        {"Тип материала": "material_name", "Процент потерь сырья": "loss_percentage"},
        preprocess=preprocess_materials,
    )

    load_table(
        conn,
        "Workshops",
        FILES["Workshops"],
        {
            "Название цеха": "workshop_name",
            "Тип цеха": "workshop_type",
            "Количество человек для производства": "num_employees",
        },
        preprocess=preprocess_workshops,
    )

    load_table(
        conn,
        "Products",
        FILES["Products"],
        {
            "Наименование продукции": "product_name",
            "Тип продукции": "product_type_name",
            "Артикул": "article",
            "Минимальная стоимость для партнера": "min_partner_cost",
            "Основной материал": "main_material_name",
        },
        preprocess=preprocess_products,
    )

    load_table(
        conn,
        "ProductWorkshops",
        FILES["ProductWorkshops"],
        {
            "Наименование продукции": "product_name",
            "Название цеха": "workshop_name",
            "Время изготовления, ч": "coefficient",
        },
        preprocess=preprocess_product_workshops,
    )

    conn.close()
    print("Готово: база данных создана и заполнена.")


if __name__ == "__main__":
    main()
import os
import sqlite3
import pandas as pd

DB_NAME = "furniture_production.db"

CSV_DIR = "data"
FILES = {
    "ProductTypes": "Product_type_import.csv",
    "Materials": "Material_type_import.csv",
    "Workshops": "Workshops_import.csv",
    "Products": "Products_import.csv",
    "ProductWorkshops": "Product_workshops_import.csv",
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


def create_db_and_tables(conn: sqlite3.Connection) -> None:
    """Создание БД и таблиц со включенным FK."""
    print("Создание базы данных и таблиц...")
    cursor = conn.cursor()
    cursor.executescript(SQL_SETUP)
    conn.commit()
    print("База данных и таблицы созданы успешно.")


def _to_float(series: pd.Series) -> pd.Series:
    """Привести значения вида '0,80%' к float."""
    return (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .replace({"": None, "nan": None, "None": None})
        .apply(lambda x: pd.to_numeric(x, errors="coerce"))
    )


def load_data(conn: sqlite3.Connection, table_name: str, csv_file: str, column_mapping: dict, preprocess=None) -> None:
    """Загрузка данных из CSV в таблицу без потери ограничений."""
    print(f"\nЗагрузка данных в таблицу {table_name} из {csv_file}...")
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, csv_file), sep=";", encoding="utf-8")
        
        # Удаляем пустые строки
        df = df.dropna(how="all")
        
        # Фильтруем строки, где все значения пустые или только пробелы
        df = df[~df.apply(lambda x: x.astype(str).str.strip().eq("").all(), axis=1)]
        
        if len(df) == 0:
            print(f"Предупреждение: Файл {csv_file} не содержит данных для загрузки.")
            return
        
        df = df.rename(columns=column_mapping)

        if preprocess:
            df = preprocess(df)
        
        # Удаляем строки с пустыми значениями после предобработки
        df = df.dropna(how="all")

        # очищаем таблицу, чтобы append не нарушил уникальные ограничения
        conn.execute(f"DELETE FROM {table_name};")
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"Успешно загружено {len(df)} записей в {table_name}.")

    except FileNotFoundError:
        print(f"Ошибка: Файл {csv_file} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при загрузке данных в {table_name}: {e}")
        import traceback
        traceback.print_exc()


def preprocess_product_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["product_type_name"])
    df = df[df["product_type_name"].str.strip() != ""]
    df["type_coefficient"] = _to_float(df["type_coefficient"])
    df = df.dropna(subset=["type_coefficient"])
    return df


def preprocess_materials(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["material_name"])
    df = df[df["material_name"].str.strip() != ""]
    df["loss_percentage"] = _to_float(df["loss_percentage"])
    df = df.dropna(subset=["loss_percentage"])
    return df


def preprocess_workshops(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["workshop_name"])
    df = df[df["workshop_name"].str.strip() != ""]
    df["num_employees"] = pd.to_numeric(df["num_employees"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["num_employees"])
    df["workshop_name"] = df["workshop_name"].str.strip()
    return df


def preprocess_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["product_name"])
    df = df[df["product_name"].str.strip() != ""]
    df.insert(0, "product_id", range(1, len(df) + 1))
    df["article"] = pd.to_numeric(df["article"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["article"])
    df["min_partner_cost"] = _to_float(df["min_partner_cost"])
    df = df.dropna(subset=["min_partner_cost"])
    df["product_name"] = df["product_name"].str.strip()
    if "product_type_name" in df.columns:
        df["product_type_name"] = df["product_type_name"].str.strip().replace("", None)
    if "main_material_name" in df.columns:
        df["main_material_name"] = df["main_material_name"].str.strip().replace("", None)
    return df


def preprocess_product_workshops(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["product_name", "workshop_name"])
    df = df[(df["product_name"].str.strip() != "") & (df["workshop_name"].str.strip() != "")]
    df["coefficient"] = _to_float(df["coefficient"])
    df = df.dropna(subset=["coefficient"])
    df["product_name"] = df["product_name"].str.strip()
    df["workshop_name"] = df["workshop_name"].str.strip()
    return df


if __name__ == "__main__":
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")

    create_db_and_tables(conn)

    load_data(
        conn,
        "ProductTypes",
        FILES["ProductTypes"],
        {
            "Тип продукции": "product_type_name",
            "Коэффициент типа продукции": "type_coefficient",
        },
        preprocess=preprocess_product_types,
    )

    load_data(
        conn,
        "Materials",
        FILES["Materials"],
        {
            "Тип материала": "material_name",
            "Процент потерь сырья": "loss_percentage",
        },
        preprocess=preprocess_materials,
    )

    load_data(
        conn,
        "Workshops",
        FILES["Workshops"],
        {
            "Название цеха": "workshop_name",
            "Тип цеха": "workshop_type",
            "Количество человек для производства": "num_employees",
        },
        preprocess=preprocess_workshops,
    )

    load_data(
        conn,
        "Products",
        FILES["Products"],
        {
            "Наименование продукции": "product_name",
            "Тип продукции": "product_type_name",
            "Артикул": "article",
            "Минимальная стоимость для партнера": "min_partner_cost",
            "Основной материал": "main_material_name",
        },
        preprocess=preprocess_products,
    )

    load_data(
        conn,
        "ProductWorkshops",
        FILES["ProductWorkshops"],
        {
            "Наименование продукции": "product_name",
            "Название цеха": "workshop_name",
            "Время изготовления, ч": "coefficient",
        },
        preprocess=preprocess_product_workshops,
    )

    conn.close()
    print("\nПроцесс загрузки завершен. База данных furniture_production.db готова.")
