# check_db.py
import sqlite3

conn = sqlite3.connect("data/raw/inventario.db")
cursor = conn.cursor()

# Consultar el catálogo maestro de SQLite para ver qué tablas existen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

print("====================================")
print("Tablas encontradas en inventario.db:")
print("====================================")
if tablas:
    for t in tablas:
        print(f"- {t[0]}")
else:
    print("¡Alerta! El archivo .db está completamente vacío.")
print("====================================")

conn.close()