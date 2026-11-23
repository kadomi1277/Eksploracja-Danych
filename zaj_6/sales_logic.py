"""Warstwa logiki: zapytania do bazy i wykresy.

Ten sam moduł importują notebook, aplikacja Streamlit, Panel i Mercury.
Interfejs (widżety) zmienia się, a logika zostaje ta sama.
"""
import sqlite3

import pandas as pd
import plotly.express as px

DB_PATH = "sales.db"


def get_connection(path=DB_PATH):
    return sqlite3.connect(path)


def get_products(conn):
    return pd.read_sql("SELECT DISTINCT product FROM sales ORDER BY product", conn)["product"].tolist()


def get_stores(conn):
    return pd.read_sql("SELECT * FROM stores ORDER BY store_id", conn)


def get_sales(conn, products=None, date_from=None, date_to=None):
    """Sprzedaż połączona ze sklepami, z opcjonalnymi filtrami.

    Filtry trafiają do zapytania jako parametry (?), nigdy przez f-string.
    """
    query = """
        SELECT s.id, s.product, s.quantity, s.price,
               s.quantity * s.price AS revenue,
               s.date, st.city, st.latitude, st.longitude
        FROM sales AS s
        JOIN stores AS st ON s.store_id = st.store_id
        WHERE 1 = 1
    """
    params = []
    if products:
        query += f" AND s.product IN ({', '.join('?' * len(products))})"
        params += list(products)
    if date_from:
        query += " AND s.date >= ?"
        params.append(str(date_from))
    if date_to:
        query += " AND s.date <= ?"
        params.append(str(date_to))
    df = pd.read_sql(query + " ORDER BY s.date", conn, params=params)
    df["date"] = pd.to_datetime(df["date"])
    return df


def daily_revenue(df):
    return df.groupby("date", as_index=False)["revenue"].sum()


def revenue_by_product(df):
    return (df.groupby("product", as_index=False)
              .agg(quantity=("quantity", "sum"), revenue=("revenue", "sum"))
              .sort_values("revenue", ascending=False))


def revenue_by_city(df):
    return (df.groupby(["city", "latitude", "longitude"], as_index=False)
              .agg(revenue=("revenue", "sum"), transactions=("id", "count")))


def add_sale(conn, product, quantity, price, date, store_id):
    if quantity <= 0 or price <= 0:
        raise ValueError("Ilość i cena muszą być dodatnie.")
    conn.execute(
        "INSERT INTO sales (product, quantity, price, date, store_id) VALUES (?, ?, ?, ?, ?)",
        (product, int(quantity), float(price), str(date), int(store_id)),
    )
    conn.commit()


# --- wykresy (Plotly Express) ---

def fig_daily(df):
    return px.line(daily_revenue(df), x="date", y="revenue", markers=True,
                   title="Sprzedaż dzienna [zł]",
                   labels={"date": "Data", "revenue": "Przychód [zł]"})


def fig_products(df):
    return px.bar(revenue_by_product(df), x="product", y="quantity",
                  hover_data=["revenue"], title="Sprzedane sztuki wg produktu",
                  labels={"product": "Produkt", "quantity": "Sztuki", "revenue": "Przychód [zł]"})


def fig_map(df):
    return px.scatter_map(revenue_by_city(df), lat="latitude", lon="longitude",
                          size="revenue", hover_name="city",
                          hover_data={"revenue": ":.0f", "transactions": True,
                                      "latitude": False, "longitude": False},
                          zoom=5, height=450, title="Przychód wg sklepu")
