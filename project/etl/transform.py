import pandas as pd

STUDENT_STATUS = {1: "Active", 3: "On Leave", 5: "Graduated", 6: "Withdrawn"}
SHIFT_MAP = {1.0: "Morning", 2.0: "Afternoon"}
USER_TYPE = {1: "Student", 2: "Admin", 3: "Teacher", 4: "Super Admin"}
EVAL_TYPE = {1: "Midterm", 2: "Final"}
CHECKIN_STATUS = {0: "On Time", 1: "Late", 2: "Absent", 3: "Excused"}
CHECKOUT_STATUS = {0.0: "On Time", 1.0: "Late", 2.0: "Early Leave"}
DAY_NAME = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
LETTER_GPA = {
    "A": 4.0, "A-": 3.67, "B+": 3.33, "B": 3.0, "B-": 2.67,
    "C+": 2.33, "C": 2.0, "C-": 1.67, "D+": 1.33, "D": 1.0, "F": 0.0,
}


def build_dim_date(start="2022-01-01", end="2028-12-31") -> pd.DataFrame:
    dates = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"date_key": dates})
    df["year"] = df["date_key"].dt.year
    df["month"] = df["date_key"].dt.month
    df["month_name"] = df["date_key"].dt.strftime("%B")
    df["quarter"] = df["date_key"].dt.quarter
    df["day_of_week"] = df["date_key"].dt.dayofweek + 1  # 1=Mon, 7=Sun
    df["day_name"] = df["date_key"].dt.strftime("%A")
    df["week_of_year"] = df["date_key"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["day_of_week"].isin([6, 7])
    df["academic_year_label"] = df.apply(
        lambda r: f"{r['year']}-{r['year'] + 1}" if r["month"] >= 8
        else f"{r['year'] - 1}-{r['year']}",
        axis=1,
    )
    df["date_key"] = df["date_key"].dt.date
    return df


def build_dim_student(student: pd.DataFrame, major: pd.DataFrame) -> pd.DataFrame:
    if student.empty: return pd.DataFrame()
    df = student[student["DeletedAt"].isna()].copy()
    major_slim = major[["Id", "Name"]].rename(columns={"Id": "MajorId", "Name": "major_name"}) if not major.empty else pd.DataFrame(columns=["MajorId", "major_name"])
    df = df.merge(major_slim, on="MajorId", how="left")

    today = pd.Timestamp.today()
    df["DateOfBirth"] = pd.to_datetime(df["DateOfBirth"], errors="coerce")
    df["age"] = ((today - df["DateOfBirth"]).dt.days // 365).astype("Int64")

    df["full_name"] = df["FirstName"].fillna("").str.strip() + " " + df["LastName"].fillna("").str.strip()
    
    if "FirstNameKh" in df.columns and "LastNameKh" in df.columns:
        df["full_name_kh"] = df["FirstNameKh"].fillna("").str.strip() + " " + df["LastNameKh"].fillna("").str.strip()
    else:
        df["first_name_kh"] = None
        df["last_name_kh"] = None
        df["full_name_kh"] = None

    df["Status"] = pd.to_numeric(df["Status"], errors="coerce")
    df["status_label"] = df["Status"].map(STUDENT_STATUS).fillna("Unknown")
    df["Shift"] = pd.to_numeric(df["Shift"], errors="coerce")
    df["shift_label"] = df["Shift"].map(SHIFT_MAP).fillna("Unknown")
    
    if "PlaceOfBirth" not in df.columns:
        df["PlaceOfBirth"] = None

    return df.rename(columns={
        "Id": "student_key", "StudentId": "student_id", "Batch": "batch",
        "Year": "year_level", "FirstName": "first_name", "LastName": "last_name",
        "FirstNameKh": "first_name_kh", "LastNameKh": "last_name_kh",
        "Gender": "gender", "DateOfBirth": "date_of_birth", "PlaceOfBirth": "place_of_birth",
        "PhoneNumber": "phone_number", "Email": "email", "Status": "status_code",
        "IsScholarship": "is_scholarship", "MajorId": "major_id", "CreatedAt": "created_at",
    })[["student_key", "student_id", "batch", "year_level", "first_name", "last_name",
        "full_name", "first_name_kh", "last_name_kh", "full_name_kh", "gender",
        "date_of_birth", "age", "place_of_birth", "phone_number", "email",
        "status_code", "status_label", "shift_label", "is_scholarship",
        "major_id", "major_name", "created_at"]]


def build_dim_teacher(teacher: pd.DataFrame) -> pd.DataFrame:
    if teacher.empty: return pd.DataFrame()
    df = teacher[teacher["DeletedAt"].isna()].copy()
    
    for col in ["Title", "FirstNameInKhmer", "LastNameInKhmer", "Room", "OfficeDay", "OfficeTime", "TeachingRate"]:
        if col not in df.columns:
            df[col] = None

    df["full_name"] = (
        df["Title"].fillna("").str.strip() + " " +
        df["FirstName"].fillna("").str.strip() + " " +
        df["LastName"].fillna("").str.strip()
    ).str.strip()
    df["is_active"] = df["Status"].astype(str).str.lower().eq("false")

    return df.rename(columns={
        "Id": "teacher_key", "Title": "title", "FirstName": "first_name",
        "LastName": "last_name", "FirstNameInKhmer": "first_name_kh",
        "LastNameInKhmer": "last_name_kh", "Gender": "gender",
        "StartDate": "start_date", "Qualification": "qualification",
        "Room": "room", "OfficeDay": "office_day", "OfficeTime": "office_time",
        "PhoneNumber": "phone_number", "Email": "email",
        "TeachingRate": "teaching_rate", "DepartmentId": "department_id",
    })[["teacher_key", "title", "first_name", "last_name", "full_name",
        "first_name_kh", "last_name_kh", "gender", "start_date", "qualification",
        "room", "office_day", "office_time", "phone_number", "email",
        "teaching_rate", "department_id", "is_active"]]


def build_dim_course(course: pd.DataFrame) -> pd.DataFrame:
    if course.empty: return pd.DataFrame()
    df = course[course["DeletedAt"].isna()].copy()
    
    for col in ["NameInKh", "Description", "Year"]:
        if col not in df.columns:
            df[col] = None
            
    return df.rename(columns={
        "Id": "course_key", "Code": "code", "Name": "name", "NameInKh": "name_kh",
        "Description": "description", "Credit": "credit", "DepartmentId": "department_id",
        "Semester": "semester_number", "Year": "year_level", "IsActive": "is_active",
    })[["course_key", "code", "name", "name_kh", "description", "credit",
        "department_id", "semester_number", "year_level", "is_active"]]


def build_dim_class(cls: pd.DataFrame, semester: pd.DataFrame) -> pd.DataFrame:
    if cls.empty: return pd.DataFrame()
    df = cls[cls["DeletedAt"].isna()].copy()
    
    for col in ["Type", "Room", "Year"]:
        if col not in df.columns:
            df[col] = None

    if not semester.empty:
        sem_slim = semester[["Id", "AcademicYear", "Semester", "StartDate", "EndDate"]].rename(columns={
            "Id": "SemesterId", "AcademicYear": "academic_year",
            "Semester": "semester_number", "StartDate": "semester_start_date",
            "EndDate": "semester_end_date",
        })
        df = df.merge(sem_slim, on="SemesterId", how="left")
    else:
        for c in ["academic_year", "semester_number", "semester_start_date", "semester_end_date"]:
            df[c] = None

    return df.rename(columns={
        "Id": "class_key", "Name": "name", "Type": "type_code", "Room": "room",
        "SemesterId": "semester_id", "MajorId": "major_id",
        "Year": "year_level", "IsActive": "is_active",
    })[["class_key", "name", "type_code", "room", "semester_id", "academic_year",
        "semester_number", "semester_start_date", "semester_end_date",
        "major_id", "year_level", "is_active"]]


def build_dim_evaluation_question(evaluation: pd.DataFrame) -> pd.DataFrame:
    if evaluation.empty: return pd.DataFrame()
    df = evaluation[
        evaluation["DeletedAt"].isna() &
        evaluation["IsActive"].astype(str).str.lower().eq("true")
    ].copy()
    df["type_label"] = df["Type"].map({0: "Rating", 1: "Text"}).fillna("Unknown")
    return df.rename(columns={
        "Id": "evaluation_key", "No": "question_no", "Question": "question_text",
        "Type": "type_code", "DepartmentId": "department_id", "IsActive": "is_active",
    })[["evaluation_key", "question_no", "question_text", "type_code", "type_label",
        "department_id", "is_active"]]


def build_dim_user(user: pd.DataFrame) -> pd.DataFrame:
    if user.empty: return pd.DataFrame()
    df = user[user["DeletedAt"].isna()].copy()
    df["user_type_label"] = df["UserType"].map(USER_TYPE).fillna("Unknown")
    
    if "Photo" not in df.columns:
        df["Photo"] = None
        
    return df.rename(columns={
        "Id": "user_key", "Username": "username", "UserType": "user_type_code",
        "AccountId": "account_id", "Photo": "photo", "CreatedAt": "created_at",
    })[["user_key", "username", "user_type_code", "user_type_label",
        "account_id", "photo", "created_at"]]


def _parse_attendances(att_str):
    if pd.isna(att_str) or str(att_str).strip() == "":
        return 0, 0, 0, 0
    tokens = [t.strip() for t in str(att_str).split(",")]
    present = sum(1 for t in tokens if t == "1")
    late = sum(1 for t in tokens if t.upper() == "L")
    absent = sum(1 for t in tokens if t.upper() == "A")
    return present, late, absent, len(tokens)


def build_fact_enrollment(
    enroll: pd.DataFrame,
    schedule: pd.DataFrame,
    cls: pd.DataFrame,
    semester: pd.DataFrame,
) -> pd.DataFrame:
    if enroll.empty: return pd.DataFrame()
    
    if not schedule.empty:
        sched = schedule[["Id", "CourseId", "TeacherId", "ClassId"]].rename(columns={
            "Id": "ScheduleId", "CourseId": "course_key",
            "TeacherId": "teacher_key", "ClassId": "ClassId_sched",
        })
    else:
        sched = pd.DataFrame(columns=["ScheduleId", "course_key", "teacher_key", "ClassId_sched"])
        
    if not cls.empty:
        cls_slim = cls[["Id", "SemesterId"]].rename(columns={"Id": "ClassId_sched"})
    else:
        cls_slim = pd.DataFrame(columns=["ClassId_sched", "SemesterId"])
        
    if not semester.empty:
        sem_slim = semester[["Id", "StartDate"]].rename(columns={
            "Id": "SemesterId", "StartDate": "semester_start_date",
        })
    else:
        sem_slim = pd.DataFrame(columns=["SemesterId", "semester_start_date"])

    df = enroll.merge(sched, on="ScheduleId", how="left")
    df = df.merge(cls_slim, on="ClassId_sched", how="left")
    df = df.merge(sem_slim, on="SemesterId", how="left")

    parsed = df["Attendances"].apply(
        lambda x: pd.Series(_parse_attendances(x),
                             index=["attendance_present", "attendance_late",
                                    "attendance_absent", "attendance_total_sessions"])
    )
    df = pd.concat([df, parsed], axis=1)
    df["attendance_rate_pct"] = (
        df["attendance_present"] /
        df["attendance_total_sessions"].replace(0, pd.NA) * 100
    ).round(2)

    score_cols = ["ScoreAttendance", "ScoreResearch", "ScoreQuiz", "ScoreMidterm", "ScoreFinal"]
    for sc in score_cols:
        if sc not in df.columns:
            df[sc] = 0

    df["total_score"] = df[score_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    df["gpa_points"] = df["LetterGrade"].map(LETTER_GPA)
    df["enrollment_date_key"] = pd.to_datetime(df["semester_start_date"], errors="coerce").dt.date

    # class_key from sched → ClassId_sched, rename for output
    df = df.rename(columns={"ClassId_sched": "class_key"})

    if "Note" not in df.columns:
        df["Note"] = None

    return df.rename(columns={
        "Id": "enrollment_key", "StudentId": "student_key", "ScheduleId": "schedule_key",
        "SemesterId": "semester_id", "ScoreAttendance": "score_attendance",
        "ScoreResearch": "score_research", "ScoreQuiz": "score_quiz",
        "ScoreMidterm": "score_midterm", "ScoreFinal": "score_final",
        "LetterGrade": "letter_grade", "Note": "note",
    })[["enrollment_key", "student_key", "schedule_key", "course_key", "teacher_key",
        "class_key", "semester_id", "enrollment_date_key", "score_attendance",
        "score_research", "score_quiz", "score_midterm", "score_final", "total_score",
        "letter_grade", "gpa_points", "attendance_present", "attendance_late",
        "attendance_absent", "attendance_total_sessions", "attendance_rate_pct", "note"]]


def build_fact_attendance(
    attendance: pd.DataFrame,
    sched_times: pd.DataFrame,
    schedule: pd.DataFrame,
    user: pd.DataFrame,
) -> pd.DataFrame:
    if attendance.empty: return pd.DataFrame()
    
    if not sched_times.empty:
        st = sched_times[["Id", "ScheduleId", "Day"]].rename(columns={"Id": "ScheduleTimesId"})
    else:
        st = pd.DataFrame(columns=["ScheduleTimesId", "ScheduleId", "Day"])
        
    if not schedule.empty:
        sched = schedule[["Id", "CourseId", "TeacherId", "ClassId"]].rename(columns={
            "Id": "ScheduleId", "CourseId": "course_key",
            "TeacherId": "teacher_key", "ClassId": "class_key",
        })
    else:
        sched = pd.DataFrame(columns=["ScheduleId", "course_key", "teacher_key", "class_key"])
        
    if not user.empty:
        # User.AccountId maps to Student.Id for student users
        user_slim = user[["Id", "AccountId"]].rename(columns={
            "Id": "UserId", "AccountId": "student_key",
        })
    else:
        user_slim = pd.DataFrame(columns=["UserId", "student_key"])

    df = attendance.merge(st, on="ScheduleTimesId", how="left", suffixes=("", "_st"))
    
    # If ScheduleId is in attendance and also in sched_times (st), we should use attendance's ScheduleId or coalesce.
    if "ScheduleId" in df.columns and "ScheduleId_st" in df.columns:
        df["ScheduleId"] = df["ScheduleId"].fillna(df["ScheduleId_st"])
        df.drop(columns=["ScheduleId_st"], inplace=True)
        
    df = df.merge(sched, on="ScheduleId", how="left")
    df = df.merge(user_slim, on="UserId", how="left")

    df["CheckInAt"] = pd.to_datetime(df["CheckInAt"], errors="coerce", utc=True)
    df["CheckOutAt"] = pd.to_datetime(df["CheckOutAt"], errors="coerce", utc=True)
    df["duration_hours"] = (
        (df["CheckOutAt"] - df["CheckInAt"]).dt.total_seconds() / 3600
    ).round(2)
    df["check_in_date_key"] = df["CheckInAt"].dt.date
    df["check_in_time"] = df["CheckInAt"].dt.strftime("%H:%M:%S")
    df["check_out_time"] = df["CheckOutAt"].dt.strftime("%H:%M:%S")

    df["CheckInStatus"] = pd.to_numeric(df["CheckInStatus"], errors="coerce")
    df["CheckOutStatus"] = pd.to_numeric(df["CheckOutStatus"], errors="coerce")
    df["check_in_status_label"] = df["CheckInStatus"].map(CHECKIN_STATUS).fillna("Unknown")
    df["check_out_status_label"] = df["CheckOutStatus"].map(CHECKOUT_STATUS).fillna("Unknown")
    
    if "Day" not in df.columns: df["Day"] = None
    df["day_of_week"] = df["Day"]
    df["day_name"] = df["Day"].map(DAY_NAME).fillna("Unknown")
    
    if "Reason" not in df.columns: df["Reason"] = None

    # Drop GPS and raw timestamp columns
    return df.rename(columns={
        "Id": "attendance_key", "UserId": "user_key",
        "ScheduleTimesId": "schedule_time_key", "ScheduleId": "schedule_key",
        "CheckInStatus": "check_in_status_code", "CheckOutStatus": "check_out_status_code",
        "Reason": "reason",
    })[["attendance_key", "student_key", "user_key", "schedule_time_key", "schedule_key",
        "course_key", "teacher_key", "class_key", "check_in_date_key", "check_in_time",
        "check_out_time", "check_in_status_code", "check_in_status_label",
        "check_out_status_code", "check_out_status_label", "duration_hours",
        "reason", "day_of_week", "day_name"]]


def build_fact_grade(
    score: pd.DataFrame,
    score_sem: pd.DataFrame,
    semester: pd.DataFrame,
) -> pd.DataFrame:
    if score_sem.empty: return pd.DataFrame()
    
    if not semester.empty:
        sem_slim = semester[["Id", "StartDate"]].rename(columns={
            "Id": "SemesterId", "StartDate": "semester_start_date",
        })
    else:
        sem_slim = pd.DataFrame(columns=["SemesterId", "semester_start_date"])
        
    if not score.empty:
        score_slim = score[["Id", "StudentId", "TotalCredit"]].rename(columns={"Id": "ScoreId"})
    else:
        score_slim = pd.DataFrame(columns=["ScoreId", "StudentId", "TotalCredit"])

    df = score_sem.merge(score_slim, on="ScoreId", how="left")
    df = df.merge(sem_slim, on="SemesterId", how="left")

    df["credit_completion_rate"] = (
        df["Credit"] / df["TotalCredit"].replace(0, pd.NA) * 100
    ).round(2)
    df["semester_date_key"] = pd.to_datetime(df["semester_start_date"], errors="coerce").dt.date
    
    if "Remarks" not in df.columns: df["Remarks"] = None

    return df.rename(columns={
        "Id": "grade_key", "StudentId": "student_key", "SemesterId": "semester_id",
        "Gpa": "gpa", "TotalCredit": "total_credit", "Credit": "earned_credit",
        "Remarks": "remarks",
    })[["grade_key", "student_key", "semester_id", "semester_date_key",
        "gpa", "total_credit", "earned_credit", "credit_completion_rate", "remarks"]]


def build_fact_evaluation_rating(
    eval_rate: pd.DataFrame,
    enroll: pd.DataFrame,
    schedule: pd.DataFrame,
    cls: pd.DataFrame,
    semester: pd.DataFrame,
) -> pd.DataFrame:
    if eval_rate.empty: return pd.DataFrame()
    
    if not enroll.empty:
        enroll_slim = enroll[["Id", "StudentId", "ScheduleId"]].rename(columns={
            "Id": "EnrollId", "StudentId": "student_key",
        })
    else:
        enroll_slim = pd.DataFrame(columns=["EnrollId", "student_key", "ScheduleId"])
        
    if not schedule.empty:
        sched = schedule[["Id", "TeacherId", "CourseId", "ClassId"]].rename(columns={
            "Id": "ScheduleId", "TeacherId": "teacher_key", "CourseId": "course_key",
        })
    else:
        sched = pd.DataFrame(columns=["ScheduleId", "teacher_key", "course_key", "ClassId"])
        
    if not cls.empty:
        cls_slim = cls[["Id", "SemesterId"]].rename(columns={"Id": "ClassId"})
    else:
        cls_slim = pd.DataFrame(columns=["ClassId", "SemesterId"])
        
    if not semester.empty:
        sem_slim = semester[["Id", "StartDate"]].rename(columns={
            "Id": "SemesterId", "StartDate": "eval_start_date",
        })
    else:
        sem_slim = pd.DataFrame(columns=["SemesterId", "eval_start_date"])

    df = eval_rate.merge(enroll_slim, on="EnrollId", how="left")
    
    if "ScheduleId_x" in df.columns and "ScheduleId_y" in df.columns:
        df["ScheduleId"] = df["ScheduleId_x"].fillna(df["ScheduleId_y"])
        
    df = df.merge(sched, on="ScheduleId", how="left")
    df = df.merge(cls_slim, on="ClassId", how="left")
    df = df.merge(sem_slim, on="SemesterId", how="left")

    df["eval_date_key"] = pd.to_datetime(df["eval_start_date"], errors="coerce").dt.date
    df["eval_type_label"] = df["Type"].map(EVAL_TYPE).fillna("Unknown")
    df["Rate"] = pd.to_numeric(df["Rate"], errors="coerce")

    return df.rename(columns={
        "Id": "eval_rating_key", "EnrollId": "enrollment_key",
        "EvaluationId": "evaluation_key", "Rate": "rate", "Type": "eval_type_code",
    })[["eval_rating_key", "enrollment_key", "student_key", "teacher_key",
        "course_key", "evaluation_key", "eval_date_key", "rate",
        "eval_type_code", "eval_type_label"]]


def build_fact_evaluation_text(
    eval_text: pd.DataFrame,
    enroll: pd.DataFrame,
    schedule: pd.DataFrame,
) -> pd.DataFrame:
    if eval_text.empty: return pd.DataFrame()
    
    if not enroll.empty:
        enroll_slim = enroll[["Id", "StudentId", "ScheduleId"]].rename(columns={
            "Id": "EnrollId", "StudentId": "student_key",
        })
    else:
        enroll_slim = pd.DataFrame(columns=["EnrollId", "student_key", "ScheduleId"])
        
    if not schedule.empty:
        sched = schedule[["Id", "TeacherId"]].rename(columns={
            "Id": "ScheduleId", "TeacherId": "teacher_key",
        })
    else:
        sched = pd.DataFrame(columns=["ScheduleId", "teacher_key"])

    df = eval_text.merge(enroll_slim, on="EnrollId", how="left")
    df = df.merge(sched, on="ScheduleId", how="left")
    df["eval_type_label"] = df["Type"].map(EVAL_TYPE).fillna("Unknown")

    return df.rename(columns={
        "Id": "eval_text_key", "EnrollId": "enrollment_key",
        "EvaluationId": "evaluation_key", "Text": "response_text", "Type": "eval_type_code",
    })[["eval_text_key", "enrollment_key", "student_key", "teacher_key",
        "evaluation_key", "response_text", "eval_type_code", "eval_type_label"]]


def build_fact_permission_request(permission: pd.DataFrame, user: pd.DataFrame) -> pd.DataFrame:
    if permission.empty: return pd.DataFrame()
    
    if not user.empty:
        user_slim = user[["Id", "AccountId"]].rename(columns={
            "Id": "UserId", "AccountId": "student_key",
        })
    else:
        user_slim = pd.DataFrame(columns=["UserId", "student_key"])
        
    df = permission.merge(user_slim, on="UserId", how="left")
    
    if "Attachment" not in df.columns: df["Attachment"] = None
    
    return df.rename(columns={
        "Id": "permission_key", "UserId": "user_key",
        "Reason": "reason", "Attachment": "attachment_url",
    })[["permission_key", "user_key", "student_key", "reason", "attachment_url"]]