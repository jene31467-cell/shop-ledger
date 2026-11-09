import streamlit as st

import db

LOW_STOCK_LEVEL = 5


@st.cache_resource
def get_conn():
    return db.get_connection()


conn = get_conn()
st.title("Shop Ledger")

if "msg" in st.session_state:
    st.success(st.session_state.pop("msg"))

products = db.get_products(conn)
tab_stock, tab_sale, tab_today = st.tabs(["Stock", "Record a sale", "Today"])

with tab_stock:
    with st.form("add_product", clear_on_submit=True):
        name = st.text_input("Product name")
        price = st.number_input("Price", min_value=0.0, step=1.0)
        stock = st.number_input("Stock", min_value=0, step=1)
        if st.form_submit_button("Save product"):
            try:
                db.save_product(conn, name, price, int(stock))
                st.session_state["msg"] = f"Saved {name.strip()}"
                st.rerun()
            except ValueError as e:
                st.error(str(e))
    st.dataframe(products, hide_index=True)

with tab_sale:
    if products.empty:
        st.info("Add a product in the Stock tab first.")
    else:
        with st.form("sale", clear_on_submit=True):
            choice = st.selectbox(
                "Product",
                products["id"],
                format_func=lambda pid: products.loc[products["id"] == pid, "name"].iloc[0],
            )
            qty = st.number_input("Quantity", min_value=1, step=1)
            if st.form_submit_button("Record sale"):
                try:
                    total = db.record_sale(conn, int(choice), int(qty))
                    st.session_state["msg"] = f"Sold {int(qty)} for {total:,.2f}"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

with tab_today:
    today = db.sales_today(conn)
    st.metric("Sales today", f"{today['total'].sum():,.2f}")
    st.dataframe(today, hide_index=True)

    low = products[products["stock"] <= LOW_STOCK_LEVEL]
    if not low.empty:
        st.warning("Running low:")
        st.dataframe(low[["name", "stock"]], hide_index=True)

    st.download_button(
        "Download all sales (CSV)",
        data=db.sales_history(conn).to_csv(index=False),
        file_name="sales.csv",
        mime="text/csv",
    )