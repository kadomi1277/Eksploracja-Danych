"""Generator bazy sales.db do zajęć z eksploracji danych.

Tworzy dwie tabele:
  stores(store_id, city, latitude, longitude)
  sales(id, product, quantity, price, date, store_id)

Dane są syntetyczne (ziarno losowania stałe), ok. 2500 transakcji
z okresu 1.09-30.11.2026: weekendy są słabsze, jest lekki trend wzrostowy
i Black Friday (27.11). W danych ukryto kilka błędów do znalezienia.
"""
import sqlite3
from datetime import date, timedelta

import numpy as np

STORES = [
    (1, "Łódź", 51.7592, 19.4560),
    (2, "Warszawa", 52.2297, 21.0122),
    (3, "Kraków", 50.0647, 19.9450),
    (4, "Gdańsk", 54.3520, 18.6466),
    (5, "Wrocław", 51.1079, 17.0385),
    (6, "Poznań", 52.4064, 16.9252),
]
STORE_WEIGHTS = [0.15, 0.30, 0.18, 0.10, 0.15, 0.12]

# produkt: (cena bazowa, średnia liczba sztuk w transakcji)
PRODUCTS = {
    "Laptop": (3200, 1.3),
    "Monitor": (850, 2.0),
    "Klawiatura": (150, 3.0),
    "Mysz": (55, 4.0),
    "Słuchawki": (300, 2.0),
    "Kamera": (250, 1.5),
}


def create_sales_db(path="sales.db", n_days=91, seed=42):
    rng = np.random.default_rng(seed)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    # DROP zamiast CREATE IF NOT EXISTS: ponowne uruchomienie nie dubluje danych
    cur.executescript("""
        DROP TABLE IF EXISTS sales;
        DROP TABLE IF EXISTS stores;
        CREATE TABLE stores (
            store_id  INTEGER PRIMARY KEY,
            city      TEXT NOT NULL,
            latitude  REAL NOT NULL,
            longitude REAL NOT NULL
        );
        CREATE TABLE sales (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            product  TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price    REAL NOT NULL,
            date     TEXT NOT NULL,
            store_id INTEGER NOT NULL REFERENCES stores(store_id)
        );
    """)
    cur.executemany("INSERT INTO stores VALUES (?, ?, ?, ?)", STORES)

    rows = []
    start = date(2026, 9, 1)
    names = list(PRODUCTS)
    for d in range(n_days):
        day = start + timedelta(days=d)
        factor = 1 + 0.4 * d / n_days               # trend
        if day.weekday() >= 5:                      # weekend
            factor *= 0.6
        if day == date(2026, 11, 27):               # Black Friday
            factor *= 3.0
        for _ in range(rng.poisson(26 * factor)):
            product = rng.choice(names)
            base_price, mean_qty = PRODUCTS[product]
            qty = int(rng.poisson(mean_qty - 1) + 1)
            price = round(base_price * rng.uniform(0.9, 1.1), 2)
            if day == date(2026, 11, 27):
                price = round(price * 0.8, 2)       # promocja
            store = int(rng.choice([s[0] for s in STORES], p=STORE_WEIGHTS))
            rows.append((product, qty, price, day.isoformat(), store))

    # ukryte błędy danych do znalezienia podczas eksploracji
    rows[150] = ("Laptop", 1, 32000.0, rows[150][3], rows[150][4])   # literówka w cenie
    rows[900] = ("Mysz", -5, 52.0, rows[900][3], rows[900][4])       # ujemna ilość
    rows[1700] = ("Monitor", 400, 860.0, rows[1700][3], rows[1700][4])  # podejrzanie duże zamówienie

    cur.executemany(
        "INSERT INTO sales (product, quantity, price, date, store_id) VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    return len(rows)


if __name__ == "__main__":
    n = create_sales_db()
    print(f"Utworzono sales.db: {n} transakcji, {len(STORES)} sklepów.")
