import sqlite3
import pandas as pd
import streamlit as st

conn = sqlite3.connect("shop.db", check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, name TEXT UNIQUE, price REAL, stock INTEGER)""")

st.title("Shop Ledger")

with st.form("add_product", clear_on_submit=True):
    name = st.text_input("Product name")
    price = st.number_input("Price", min_value=0.0, step=1.0)
    stock = st.number_input("Stock", min_value=0, step=1)
    if st.form_submit_button("Add product") and name:
        conn.execute("INSERT OR REPLACE INTO products (name, price, stock) VALUES (?, ?, ?)",
                     (name, price, stock))
        conn.commit()

st.dataframe(pd.read_sql("SELECT name, price, stock FROM products", conn))
