import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    Text,
    Date,
    Enum,
    JSON,
    ForeignKey,
    DECIMAL,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()


def utc_now():
    return datetime.now(timezone.utc)


logger = logging.getLogger("Database")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQLITE_DB_PATH = PROJECT_ROOT / "loan_system.db"

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "loan_system")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum("Male", "Female", "Other"), default=None)
    email = Column(String(100), unique=True)
    phone = Column(String(20), nullable=False)
    address = Column(Text)
    city = Column(String(50))
    state = Column(String(50))
    postal_code = Column(String(10))
    national_id = Column(String(50), unique=True)
    employment_type = Column(
        Enum("Salaried", "Self-Employed", "Unemployed", "Retired"), default="Salaried"
    )
    employer_name = Column(String(100))
    employment_years = Column(DECIMAL(4, 1), default=0.0)
    annual_income = Column(DECIMAL(12, 2), default=0.00)
    home_ownership = Column(Enum("RENT", "OWN", "MORTGAGE", "OTHER"), default="RENT")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    applications = relationship(
        "LoanApplication", back_populates="customer", cascade="all, delete-orphan"
    )


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    application_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False
    )
    loan_amount = Column(DECIMAL(12, 2), nullable=False)
    loan_purpose = Column(
        Enum(
            "PERSONAL",
            "EDUCATION",
            "MEDICAL",
            "VENTURE",
            "HOMEIMPROVEMENT",
            "DEBTCONSOLIDATION",
            "AUTO",
            "OTHER",
        ),
        nullable=False,
    )
    loan_term_months = Column(Integer, default=12)
    interest_rate = Column(DECIMAL(5, 2), default=None)
    currency = Column(String(3), default="USD")
    status = Column(
        Enum(
            "SUBMITTED",
            "DOCUMENTS_PENDING",
            "UNDER_REVIEW",
            "ML_SCORED",
            "APPROVED",
            "REJECTED",
            "DISBURSED",
            "CLOSED",
            "DEFAULTED",
        ),
        default="SUBMITTED",
    )
    applied_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    customer = relationship("Customer", back_populates="applications")
    documents = relationship(
        "Document", back_populates="application", cascade="all, delete-orphan"
    )
    credit_checks = relationship(
        "CreditCheck", back_populates="application", cascade="all, delete-orphan"
    )
    predictions = relationship(
        "MLPrediction", back_populates="application", cascade="all, delete-orphan"
    )
    approvals = relationship(
        "Approval", back_populates="application", cascade="all, delete-orphan"
    )
    emi_schedules = relationship(
        "EMISchedule", back_populates="application", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(
        Integer,
        ForeignKey("loan_applications.application_id", ondelete="CASCADE"),
        nullable=False,
    )
    document_type = Column(
        Enum(
            "IDENTITY",
            "INCOME_PROOF",
            "BANK_STATEMENT",
            "ADDRESS_PROOF",
            "EMPLOYMENT_LETTER",
            "TAX_RETURN",
            "OTHER",
        ),
        nullable=False,
    )
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_kb = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(String(100), default=None)
    verified_at = Column(DateTime, default=None)
    uploaded_at = Column(DateTime, default=utc_now)

    application = relationship("LoanApplication", back_populates="documents")


class CreditCheck(Base):
    __tablename__ = "credit_checks"

    check_id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(
        Integer,
        ForeignKey("loan_applications.application_id", ondelete="CASCADE"),
        nullable=False,
    )
    bureau_name = Column(String(50), default="Equifax")
    credit_score = Column(Integer, default=None)
    credit_history_years = Column(DECIMAL(4, 1), default=0.0)
    total_existing_debt = Column(DECIMAL(12, 2), default=0.00)
    open_accounts = Column(Integer, default=0)
    missed_payments = Column(Integer, default=0)
    bankruptcies = Column(Integer, default=0)
    report_json = Column(JSON, default=None)
    checked_at = Column(DateTime, default=utc_now)

    application = relationship("LoanApplication", back_populates="credit_checks")


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(
        Integer,
        ForeignKey("loan_applications.application_id", ondelete="CASCADE"),
        nullable=False,
    )
    model_name = Column(String(50), default="xgboost")
    model_version = Column(String(20), default="1.0.0")
    prediction = Column(Enum("Default", "Non-Default"), nullable=False)
    default_probability = Column(DECIMAL(6, 4), nullable=False)
    risk_level = Column(Enum("Low Risk", "Medium Risk", "High Risk"), nullable=False)
    recommended_max_loan_amount = Column(DECIMAL(12, 2), default=0.00)
    feature_importance_json = Column(JSON, default=None)
    reason_codes = Column(JSON, default=None)
    scored_at = Column(DateTime, default=utc_now)

    application = relationship("LoanApplication", back_populates="predictions")


class Approval(Base):
    __tablename__ = "approvals"

    approval_id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(
        Integer,
        ForeignKey("loan_applications.application_id", ondelete="CASCADE"),
        nullable=False,
    )
    approved_by = Column(String(100), nullable=False)
    decision = Column(Enum("APPROVED", "REJECTED", "REFERRED"), nullable=False)
    approved_amount = Column(DECIMAL(12, 2), default=None)
    approved_term_months = Column(Integer, default=None)
    interest_rate = Column(DECIMAL(5, 2), default=None)
    conditions = Column(Text, default=None)
    decision_at = Column(DateTime, default=utc_now)

    application = relationship("LoanApplication", back_populates="approvals")


class EMISchedule(Base):
    __tablename__ = "emi_schedules"

    emi_id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(
        Integer,
        ForeignKey("loan_applications.application_id", ondelete="CASCADE"),
        nullable=False,
    )
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    principal_amount = Column(DECIMAL(12, 2), nullable=False)
    interest_amount = Column(DECIMAL(12, 2), nullable=False)
    total_emi_amount = Column(DECIMAL(12, 2), nullable=False)
    outstanding_balance = Column(DECIMAL(12, 2), nullable=False)
    status = Column(
        Enum("PENDING", "PAID", "OVERDUE", "PARTIALLY_PAID"), default="PENDING"
    )

    application = relationship("LoanApplication", back_populates="emi_schedules")
    payments = relationship(
        "Payment", back_populates="emi", cascade="all, delete-orphan"
    )


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    emi_id = Column(
        Integer, ForeignKey("emi_schedules.emi_id", ondelete="CASCADE"), nullable=False
    )
    application_id = Column(
        Integer,
        ForeignKey("loan_applications.application_id", ondelete="CASCADE"),
        nullable=False,
    )
    amount_paid = Column(DECIMAL(12, 2), nullable=False)
    payment_method = Column(
        Enum("BANK_TRANSFER", "CARD", "CASH", "CHEQUE", "UPI", "OTHER"),
        default="BANK_TRANSFER",
    )
    transaction_ref = Column(String(100), default=None)
    paid_at = Column(DateTime, default=utc_now)

    emi = relationship("EMISchedule", back_populates="payments")


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now)
    age = Column(Integer)
    income = Column(Float)
    employment_years = Column(Float)
    home_ownership = Column(String(20))
    loan_amount = Column(Float)
    loan_purpose = Column(String(30))
    credit_history_years = Column(Float)
    prediction = Column(String(20))
    default_probability = Column(Float)
    risk_level = Column(String(20))
    recommended_max_loan_amount = Column(Float)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="loan_officer")
    created_at = Column(DateTime, default=utc_now)


def seed_default_user():
    """Ensure at least one default loan officer / admin account exists."""
    import bcrypt

    session = SessionLocal()
    try:
        existing = session.query(User).filter_by(username="admin").first()
        if not existing:
            hashed_pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
            admin_user = User(
                username="admin",
                password_hash=hashed_pw,
                role="admin",
            )
            session.add(admin_user)
            session.commit()
    except Exception as e:
        session.rollback()
        logger.warning(f"Could not seed default user: {e}")
    finally:
        session.close()


def init_db():
    """Create all tables if they don't exist, falling back to SQLite if MySQL is offline."""
    global engine, SessionLocal, DATABASE_URL
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Connected to primary database successfully.")
    except Exception as e:
        logger.warning(
            f"Primary DB connection failed ({e}). Falling back to local SQLite database..."
        )
        sqlite_url = f"sqlite:///{SQLITE_DB_PATH.as_posix()}"
        engine = create_engine(
            sqlite_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

    seed_default_user()


def get_db():
    """FastAPI dependency - yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_username(username: str):
    """Retrieve user record by username."""
    session = SessionLocal()
    try:
        return session.query(User).filter_by(username=username).first()
    finally:
        session.close()


def create_user(username: str, password_hash: str, role: str = "loan_officer") -> bool:
    """Create a new user in the database."""
    session = SessionLocal()
    try:
        if session.query(User).filter_by(username=username).first():
            return False
        new_user = User(username=username, password_hash=password_hash, role=role)
        session.add(new_user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating user: {e}")
        raise
    finally:
        session.close()


def update_user_password(username: str, new_password_hash: str) -> bool:
    """Update user password hash."""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False
        user.password_hash = new_password_hash
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating password: {e}")
        raise
    finally:
        session.close()


def get_prediction_logs_df():
    """Fetch all prediction logs into a pandas DataFrame."""
    import pandas as pd
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(
                "SELECT * FROM prediction_logs ORDER BY timestamp DESC", conn
            )
    except Exception as e:
        logger.error(f"Error fetching prediction logs: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    init_db()
    try:
        connection = engine.connect()
        print("[OK] Database connected successfully!")
        print(f"   Engine URL: {engine.url}")
        connection.close()
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")

