import sqlite3
import json


def fetch_products(info=None, price=None, name=None, db_path='./../db.sqlite3'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT * FROM home_product WHERE 1=1"

    params = []
    if info is not None:
        query += " AND info=?"
        params.append(info)
    if price is not None:
        query += " AND price=?"
        params.append(price)
    if name is not None:
        query += " AND name=?"
        params.append(name)

    cursor.execute(query, params)
    records = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    results = []
    for record in records:
        results.append(dict(zip(columns, record)))

    cursor.close()
    conn.close()
    return json.dumps(results, ensure_ascii=False)
