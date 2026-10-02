import pytest
import bcrypt
from src.database import (
    init_db,
    get_user_by_username,
    create_user,
    update_user_password,
    get_prediction_logs_df,
    User,
)

def test_init_db_creates_tables_and_admin_user():
    init_db()
    admin = get_user_by_username("admin")
    assert admin is not None
    assert admin.username == "admin"
    assert admin.role == "admin"
    assert len(admin.password_hash) > 20

def test_create_and_update_user():
    test_username = "test_officer_42"
    hashed = bcrypt.hashpw(b"secret42", bcrypt.gensalt()).decode("utf-8")

    existing = get_user_by_username(test_username)
    if not existing:
        created = create_user(test_username, hashed, role="loan_officer")
        assert created is True

    duplicate = create_user(test_username, hashed, role="loan_officer")
    assert duplicate is False

    new_hashed = bcrypt.hashpw(b"newsecret42", bcrypt.gensalt()).decode("utf-8")
    updated = update_user_password(test_username, new_hashed)
    assert updated is True

    user = get_user_by_username(test_username)
    assert user is not None
    assert bcrypt.checkpw(b"newsecret42", user.password_hash.encode("utf-8"))

def test_get_prediction_logs_df():
    df = get_prediction_logs_df()
    assert hasattr(df, "columns")
    assert hasattr(df, "shape")
