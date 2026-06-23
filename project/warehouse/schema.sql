-- DROP existing tables (if rebuilding)
DROP SCHEMA IF EXISTS warehouse CASCADE;
CREATE SCHEMA warehouse;
SET search_path TO warehouse;

-- =====================================================
-- DIMENSION TABLES
-- =====================================================

CREATE TABLE dim_date (
    date_key DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    week_of_year INTEGER,
    is_weekend BOOLEAN,
    academic_year_label VARCHAR(20)
);

CREATE TABLE dim_student (
    student_key INTEGER PRIMARY KEY,
    student_id VARCHAR(50),
    batch INTEGER,
    year_level INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    first_name_kh VARCHAR(100),
    last_name_kh VARCHAR(100),
    full_name_kh VARCHAR(200),
    gender VARCHAR(20),
    date_of_birth DATE,
    age INTEGER,
    place_of_birth VARCHAR(200),
    phone_number VARCHAR(50),
    email VARCHAR(100),
    status_code INTEGER,
    status_label VARCHAR(50),
    shift_label VARCHAR(50),
    is_scholarship BOOLEAN,
    major_id INTEGER,
    major_name VARCHAR(100),
    created_at TIMESTAMP
);

CREATE TABLE dim_teacher (
    teacher_key INTEGER PRIMARY KEY,
    title VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    first_name_kh VARCHAR(100),
    last_name_kh VARCHAR(100),
    gender VARCHAR(20),
    start_date DATE,
    qualification VARCHAR(200),
    room VARCHAR(50),
    office_day VARCHAR(100),
    office_time VARCHAR(100),
    phone_number VARCHAR(50),
    email VARCHAR(100),
    teaching_rate DECIMAL(10,2),
    department_id INTEGER,
    is_active BOOLEAN
);

CREATE TABLE dim_course (
    course_key INTEGER PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(200),
    name_kh VARCHAR(200),
    description TEXT,
    credit INTEGER,
    department_id INTEGER,
    semester_number INTEGER,
    year_level INTEGER,
    is_active BOOLEAN
);

CREATE TABLE dim_class (
    class_key INTEGER PRIMARY KEY,
    name VARCHAR(100),
    type_code INTEGER,
    room VARCHAR(50),
    semester_id INTEGER,
    academic_year VARCHAR(50),
    semester_number INTEGER,
    semester_start_date DATE,
    semester_end_date DATE,
    major_id INTEGER,
    year_level INTEGER,
    is_active BOOLEAN
);

CREATE TABLE dim_evaluation_question (
    evaluation_key INTEGER PRIMARY KEY,
    question_no INTEGER,
    question_text TEXT,
    type_code INTEGER,
    type_label VARCHAR(50),
    department_id INTEGER,
    is_active BOOLEAN
);

CREATE TABLE dim_user (
    user_key INTEGER PRIMARY KEY,
    username VARCHAR(100),
    user_type_code INTEGER,
    user_type_label VARCHAR(50),
    account_id INTEGER,
    photo VARCHAR(500),
    created_at TIMESTAMP
);

-- =====================================================
-- FACT TABLES
-- =====================================================

CREATE TABLE fact_enrollment (
    enrollment_key INTEGER PRIMARY KEY,
    student_key INTEGER,
    schedule_key INTEGER,
    course_key INTEGER,
    teacher_key INTEGER,
    class_key INTEGER,
    semester_id INTEGER,
    enrollment_date_key DATE,
    score_attendance DECIMAL(5,2),
    score_research DECIMAL(5,2),
    score_quiz DECIMAL(5,2),
    score_midterm DECIMAL(5,2),
    score_final DECIMAL(5,2),
    total_score DECIMAL(5,2),
    letter_grade VARCHAR(5),
    gpa_points DECIMAL(5,2),
    attendance_present INTEGER,
    attendance_late INTEGER,
    attendance_absent INTEGER,
    attendance_total_sessions INTEGER,
    attendance_rate_pct DECIMAL(5,2),
    note TEXT
);

CREATE TABLE fact_attendance (
    attendance_key INTEGER PRIMARY KEY,
    student_key INTEGER,
    user_key INTEGER,
    schedule_time_key INTEGER,
    schedule_key INTEGER,
    course_key INTEGER,
    teacher_key INTEGER,
    class_key INTEGER,
    check_in_date_key DATE,
    check_in_time TIME,
    check_out_time TIME,
    check_in_status_code INTEGER,
    check_in_status_label VARCHAR(50),
    check_out_status_code INTEGER,
    check_out_status_label VARCHAR(50),
    duration_hours DECIMAL(5,2),
    reason TEXT,
    day_of_week INTEGER,
    day_name VARCHAR(20)
);

CREATE TABLE fact_grade (
    grade_key INTEGER PRIMARY KEY,
    student_key INTEGER,
    semester_id INTEGER,
    semester_date_key DATE,
    gpa DECIMAL(5,2),
    total_credit INTEGER,
    earned_credit INTEGER,
    credit_completion_rate DECIMAL(5,2),
    remarks TEXT
);

CREATE TABLE fact_evaluation_rating (
    eval_rating_key INTEGER PRIMARY KEY,
    enrollment_key INTEGER,
    student_key INTEGER,
    teacher_key INTEGER,
    course_key INTEGER,
    evaluation_key INTEGER,
    eval_date_key DATE,
    rate INTEGER,
    eval_type_code INTEGER,
    eval_type_label VARCHAR(50)
);

CREATE TABLE fact_evaluation_text (
    eval_text_key INTEGER PRIMARY KEY,
    enrollment_key INTEGER,
    student_key INTEGER,
    teacher_key INTEGER,
    evaluation_key INTEGER,
    response_text TEXT,
    eval_type_code INTEGER,
    eval_type_label VARCHAR(50)
);

CREATE TABLE fact_permission_request (
    permission_key INTEGER PRIMARY KEY,
    user_key INTEGER,
    student_key INTEGER,
    reason TEXT,
    attachment_url VARCHAR(500)
);