-- =====================================================
-- DIMENSION TABLES
-- =====================================================

-- Date Dimension (for time-based analysis)
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    week INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    academic_year VARCHAR(20),
    semester_name VARCHAR(50)
);

-- Student Dimension (slowly changing dimension - Type 2)
CREATE TABLE dim_student (
    student_sk INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    student_bk INTEGER, -- business key from source
    student_code VARCHAR(20),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender VARCHAR(10),
    date_of_birth DATE,
    phone VARCHAR(20),
    email VARCHAR(150),
    batch INTEGER,
    year_level INTEGER,
    shift INTEGER,
    is_scholarship BOOLEAN,
    major_id INTEGER,
    major_name VARCHAR(100),
    department_id INTEGER,
    department_name VARCHAR(100),
    faculty_id INTEGER,
    faculty_name VARCHAR(100),
    status INTEGER,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teacher Dimension
CREATE TABLE dim_teacher (
    teacher_sk INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    teacher_bk INTEGER,
    title VARCHAR(225),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender VARCHAR(50),
    qualification VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    department_id INTEGER,
    department_name VARCHAR(100),
    faculty_name VARCHAR(100),
    teaching_rate VARCHAR(50),
    status BOOLEAN,
    is_current BOOLEAN DEFAULT true
);

-- Course Dimension
CREATE TABLE dim_course (
    course_sk INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    course_bk INTEGER,
    code VARCHAR(10),
    name VARCHAR(100),
    name_kh VARCHAR(255),
    description VARCHAR(225),
    credit INTEGER,
    department_id INTEGER,
    department_name VARCHAR(100),
    semester INTEGER,
    year INTEGER,
    is_active BOOLEAN
);

-- Class Dimension
CREATE TABLE dim_class (
    class_sk INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    class_bk INTEGER,
    name VARCHAR(100),
    type INTEGER,
    room VARCHAR(100),
    start_month INTEGER,
    evaluate_type INTEGER,
    major_id INTEGER,
    major_name VARCHAR(100),
    year INTEGER,
    color VARCHAR(10),
    is_active BOOLEAN
);

-- Time Dimension (Schedule times)
CREATE TABLE dim_schedule_time (
    schedule_time_sk INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    schedule_time_bk INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(10),
    start_time TIME,
    end_time TIME,
    amount_in_hour DECIMAL(5,2),
    room VARCHAR(100),
    label VARCHAR(100),
    is_confirm BOOLEAN
);

-- Academic Period Dimension
CREATE TABLE dim_semester (
    semester_sk INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    semester_bk INTEGER,
    semester_number INTEGER,
    year INTEGER,
    academic_year VARCHAR(100),
    start_date DATE,
    end_date DATE,
    final_period VARCHAR(50),
    number_of_months INTEGER,
    start_month INTEGER,
    major_id INTEGER,
    major_name VARCHAR(100)
);

-- =====================================================
-- FACT TABLES
-- =====================================================

-- Fact Attendance (daily attendance tracking)
CREATE TABLE fact_attendance (
    attendance_id INTEGER PRIMARY KEY,
    student_sk INTEGER REFERENCES dim_student(student_sk),
    schedule_time_sk INTEGER REFERENCES dim_schedule_time(schedule_time_sk),
    date_sk INTEGER REFERENCES dim_date(date_id),
    semester_sk INTEGER REFERENCES dim_semester(semester_sk),
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    check_in_status INTEGER,
    check_out_status INTEGER,
    reason VARCHAR(200),
    is_late BOOLEAN,
    is_absent BOOLEAN,
    duration_minutes INTEGER,
    created_at TIMESTAMP
);

-- Fact Enrollment (student enrollment in courses)
CREATE TABLE fact_enrollment (
    enroll_id INTEGER PRIMARY KEY,
    student_sk INTEGER REFERENCES dim_student(student_sk),
    course_sk INTEGER REFERENCES dim_course(course_sk),
    class_sk INTEGER REFERENCES dim_class(class_sk),
    teacher_sk INTEGER REFERENCES dim_teacher(teacher_sk),
    semester_sk INTEGER REFERENCES dim_semester(semester_sk),
    date_sk INTEGER REFERENCES dim_date(date_id),
    score_attendance DECIMAL(5,2),
    score_research DECIMAL(5,2),
    score_quiz DECIMAL(5,2),
    score_midterm DECIMAL(5,2),
    score_final DECIMAL(5,2),
    total_score DECIMAL(5,2),
    letter_grade VARCHAR(5),
    grade_point DECIMAL(3,2),
    note VARCHAR(50),
    enroll_date TIMESTAMP
);

-- Fact Score (academic performance summary)
CREATE TABLE fact_score (
    score_id INTEGER PRIMARY KEY,
    student_sk INTEGER REFERENCES dim_student(student_sk),
    semester_sk INTEGER REFERENCES dim_semester(semester_sk),
    date_sk INTEGER REFERENCES dim_date(date_id),
    total_credit INTEGER,
    earned_credit INTEGER,
    gpa DECIMAL(3,2),
    cumulative_gpa DECIMAL(3,2),
    remarks VARCHAR(500)
);

-- Fact Schedule (class scheduling)
CREATE TABLE fact_schedule (
    schedule_id INTEGER PRIMARY KEY,
    course_sk INTEGER REFERENCES dim_course(course_sk),
    teacher_sk INTEGER REFERENCES dim_teacher(teacher_sk),
    class_sk INTEGER REFERENCES dim_class(class_sk),
    schedule_time_sk INTEGER REFERENCES dim_schedule_time(schedule_time_sk),
    semester_sk INTEGER REFERENCES dim_semester(semester_sk),
    teaching_rate_hours DECIMAL(5,2),
    is_online BOOLEAN,
    status INTEGER,
    no_alert BOOLEAN
);

-- Fact Evaluation (course evaluations by students)
CREATE TABLE fact_evaluation (
    evaluation_id INTEGER PRIMARY KEY,
    student_sk INTEGER REFERENCES dim_student(student_sk),
    course_sk INTEGER REFERENCES dim_course(course_sk),
    evaluation_question_sk INTEGER,
    date_sk INTEGER REFERENCES dim_date(date_id),
    rating INTEGER,
    text_response VARCHAR(1000),
    evaluation_type INTEGER
);

-- =====================================================
-- BRIDGE TABLE (for many-to-many relationships)
-- =====================================================
CREATE TABLE bridge_teacher_course (
    teacher_sk INTEGER REFERENCES dim_teacher(teacher_sk),
    course_sk INTEGER REFERENCES dim_course(course_sk),
    PRIMARY KEY (teacher_sk, course_sk)
);