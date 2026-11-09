import pytest

import db


@pytest.fixture
def conn():
    return db.get_connection(":memory:")  # a throwaway database, nothing saved to disk


def first_product_id(conn):
    return int(db.get_products(conn).iloc[0]["id"])


def test_save_and_list_product(conn):
    db.save_product(conn, "Rice", 8000, 20)
    products = db.get_products(conn)
    assert len(products) == 1
    assert products.iloc[0]["name"] == "Rice"


def test_saving_same_name_updates_instead_of_duplicating(conn):
    db.save_product(conn, "Rice", 8000, 20)
    pid = first_product_id(conn)
    db.save_product(conn, "Rice", 9000, 30)
    products = db.get_products(conn)
    assert len(products) == 1
    assert first_product_id(conn) == pid
    assert products.iloc[0]["price"] == 9000


def test_sale_reduces_stock_and_returns_total(conn):
    db.save_product(conn, "Rice", 8000, 20)
    total = db.record_sale(conn, first_product_id(conn), 3)
    assert total == 24000
    assert db.get_products(conn).iloc[0]["stock"] == 17


def test_cannot_oversell(conn):
    db.save_product(conn, "Rice", 8000, 2)
    with pytest.raises(ValueError):
        db.record_sale(conn, first_product_id(conn), 5)
    assert db.get_products(conn).iloc[0]["stock"] == 2  # unchanged
    assert db.sales_history(conn).empty


def test_rejects_bad_input(conn):
    with pytest.raises(ValueError):
        db.save_product(conn, "   ", 100, 1)
    with pytest.raises(ValueError):
        db.save_product(conn, "Rice", -5, 1)