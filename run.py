"""
Запуск: создает БД при отсутствии и стартует FastAPI.
"""
import os
import subprocess
import sys


def ensure_db():
    if not os.path.exists("furniture_production.db"):
        print("База не найдена. Создаю...")
        subprocess.check_call([sys.executable, "create_bd.py"])
    else:
        print("База уже существует.")


def run_server():
    print("Запускаю сервер на http://127.0.0.1:8000")
    subprocess.check_call(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
    )


def main():
    ensure_db()
    run_server()


if __name__ == "__main__":
    main()

