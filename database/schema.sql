-- ============================================================
-- AI Loan Default Prediction System — Full Database Schema
-- ============================================================
-- Flow: customers → applications → documents → credit_checks
--       → ml_predictions → approvals → emi_schedules → payments
-- ============================================================

CREATE DATABASE IF NOT EXISTS loan_system;
USE loan_system;

-- ============================================================
-- 1. CUSTOMERS — Core applicant information
-- ============================================================
CREATE TABLE customers (
    customer_id     INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100)    NOT NULL,
    date_of_birth   DATE            NOT NULL,
    gender          ENUM('Male', 'Female', 'Other') DEFAULT NULL,
    email           VARCHAR(100)    UNIQUE,
    phone           VARCHAR(20)     NOT NULL,
    address         TEXT,
    city            VARCHAR(50),
    state           VARCHAR(50),
    postal_code     VARCHAR(10),
    national_id     VARCHAR(50)     UNIQUE COMMENT 'NIC / Passport / SSN',
    employment_type ENUM('Salaried', 'Self-Employed', 'Unemployed', 'Retired') DEFAULT 'Salaried',
    employer_name   VARCHAR(100),
    employment_years DECIMAL(4,1)   DEFAULT 0.0,
    annual_income   DECIMAL(12,2)   DEFAULT 0.00,
    home_ownership  ENUM('RENT', 'OWN', 'MORTGAGE', 'OTHER') DEFAULT 'RENT',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_customer_email (email),
    INDEX idx_customer_phone (phone),
    INDEX idx_customer_national_id (national_id)
) ENGINE=InnoDB;


-- ============================================================
-- 2. LOAN APPLICATIONS — Each loan request
-- ============================================================
CREATE TABLE loan_applications (
    application_id  INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT             NOT NULL,
    loan_amount     DECIMAL(12,2)   NOT NULL,
    loan_purpose    ENUM(
        'PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE',
        'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION', 'AUTO', 'OTHER'
    ) NOT NULL,
    loan_term_months INT            NOT NULL DEFAULT 12,
    interest_rate   DECIMAL(5,2)    DEFAULT NULL COMMENT 'Annual % — set after approval',
    currency        VARCHAR(3)      DEFAULT 'USD',
    status          ENUM(
        'SUBMITTED', 'DOCUMENTS_PENDING', 'UNDER_REVIEW',
        'ML_SCORED', 'APPROVED', 'REJECTED', 'DISBURSED',
        'CLOSED', 'DEFAULTED'
    ) DEFAULT 'SUBMITTED',
    applied_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_app_customer (customer_id),
    INDEX idx_app_status (status)
) ENGINE=InnoDB;


-- ============================================================
-- 3. DOCUMENTS — KYC & supporting documents
-- ============================================================
CREATE TABLE documents (
    document_id     INT AUTO_INCREMENT PRIMARY KEY,
    application_id  INT             NOT NULL,
    document_type   ENUM(
        'IDENTITY', 'INCOME_PROOF', 'BANK_STATEMENT',
        'ADDRESS_PROOF', 'EMPLOYMENT_LETTER', 'TAX_RETURN', 'OTHER'
    ) NOT NULL,
    file_name       VARCHAR(255)    NOT NULL,
    file_path       VARCHAR(500)    NOT NULL,
    file_size_kb    INT             DEFAULT 0,
    is_verified     BOOLEAN         DEFAULT FALSE,
    verified_by     VARCHAR(100)    DEFAULT NULL,
    verified_at     TIMESTAMP       NULL,
    uploaded_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_doc_application (application_id)
) ENGINE=InnoDB;


-- ============================================================
-- 4. CREDIT CHECKS — Bureau / credit history data
-- ============================================================
CREATE TABLE credit_checks (
    check_id            INT AUTO_INCREMENT PRIMARY KEY,
    application_id      INT             NOT NULL,
    bureau_name         VARCHAR(50)     DEFAULT 'Equifax' COMMENT 'Equifax / Experian / TransUnion',
    credit_score        INT             DEFAULT NULL,
    credit_history_years DECIMAL(4,1)   DEFAULT 0.0,
    total_existing_debt DECIMAL(12,2)   DEFAULT 0.00,
    open_accounts       INT             DEFAULT 0,
    missed_payments     INT             DEFAULT 0,
    bankruptcies        INT             DEFAULT 0,
    report_json         JSON            DEFAULT NULL COMMENT 'Full raw bureau response',
    checked_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_credit_application (application_id)
) ENGINE=InnoDB;


-- ============================================================
-- 5. ML PREDICTIONS — Model scoring results
-- ============================================================
CREATE TABLE ml_predictions (
    prediction_id               INT AUTO_INCREMENT PRIMARY KEY,
    application_id              INT             NOT NULL,
    model_name                  VARCHAR(50)     DEFAULT 'xgboost',
    model_version               VARCHAR(20)     DEFAULT '1.0.0',
    prediction                  ENUM('Default', 'Non-Default') NOT NULL,
    default_probability         DECIMAL(6,4)    NOT NULL COMMENT '0.0000 to 1.0000',
    risk_level                  ENUM('Low Risk', 'Medium Risk', 'High Risk') NOT NULL,
    recommended_max_loan_amount DECIMAL(12,2)   DEFAULT 0.00,
    feature_importance_json     JSON            DEFAULT NULL COMMENT 'SHAP / feature explanation',
    reason_codes                JSON            DEFAULT NULL COMMENT 'List of risk reason strings',
    scored_at                   TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_pred_application (application_id),
    INDEX idx_pred_risk (risk_level)
) ENGINE=InnoDB;


-- ============================================================
-- 6. APPROVALS — Final banker decision
-- ============================================================
CREATE TABLE approvals (
    approval_id         INT AUTO_INCREMENT PRIMARY KEY,
    application_id      INT             NOT NULL,
    approved_by         VARCHAR(100)    NOT NULL COMMENT 'Banker / officer name',
    decision            ENUM('APPROVED', 'REJECTED', 'REFERRED') NOT NULL,
    approved_amount     DECIMAL(12,2)   DEFAULT NULL,
    approved_term_months INT            DEFAULT NULL,
    interest_rate       DECIMAL(5,2)    DEFAULT NULL,
    conditions          TEXT            DEFAULT NULL COMMENT 'Special conditions or notes',
    decision_at         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_approval_application (application_id)
) ENGINE=InnoDB;


-- ============================================================
-- 7. EMI SCHEDULES — Monthly installment plan
-- ============================================================
CREATE TABLE emi_schedules (
    emi_id              INT AUTO_INCREMENT PRIMARY KEY,
    application_id      INT             NOT NULL,
    installment_number  INT             NOT NULL,
    due_date            DATE            NOT NULL,
    principal_amount    DECIMAL(12,2)   NOT NULL,
    interest_amount     DECIMAL(12,2)   NOT NULL,
    total_emi_amount    DECIMAL(12,2)   NOT NULL,
    outstanding_balance DECIMAL(12,2)   NOT NULL,
    status              ENUM('PENDING', 'PAID', 'OVERDUE', 'PARTIALLY_PAID') DEFAULT 'PENDING',
    
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_emi_application (application_id),
    INDEX idx_emi_due_date (due_date)
) ENGINE=InnoDB;


-- ============================================================
-- 8. PAYMENTS — Actual payment records
-- ============================================================
CREATE TABLE payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    emi_id          INT             NOT NULL,
    application_id  INT             NOT NULL,
    amount_paid     DECIMAL(12,2)   NOT NULL,
    payment_method  ENUM('BANK_TRANSFER', 'CARD', 'CASH', 'CHEQUE', 'UPI', 'OTHER') DEFAULT 'BANK_TRANSFER',
    transaction_ref VARCHAR(100)    DEFAULT NULL,
    paid_at         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (emi_id) REFERENCES emi_schedules(emi_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_payment_emi (emi_id),
    INDEX idx_payment_application (application_id)
) ENGINE=InnoDB;


-- ============================================================
-- 9. PREDICTION LOGS — MLOps monitoring (backward compatible)
-- ============================================================
CREATE TABLE prediction_logs (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    timestamp           TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    age                 INT,
    income              DECIMAL(12,2),
    employment_years    DECIMAL(4,1),
    home_ownership      VARCHAR(20),
    loan_amount         DECIMAL(12,2),
    loan_purpose        VARCHAR(30),
    credit_history_years DECIMAL(4,1),
    prediction          VARCHAR(20),
    default_probability DECIMAL(6,4),
    risk_level          VARCHAR(20),
    recommended_max_loan_amount DECIMAL(12,2)
) ENGINE=InnoDB;
