-- =====================================================
-- POWER BI DASHBOARD QUERIES
-- =====================================================

-- 1. Executive Summary KPIs
SELECT 
    (SELECT COUNT(*) FROM dim_student WHERE is_current = true) as total_students,
    (SELECT COUNT(*) FROM dim_teacher) as total_teachers,
    (SELECT COUNT(*) FROM dim_course) as total_courses,
    (SELECT ROUND(AVG(gpa)::numeric, 2) FROM fact_score 
     WHERE created_at >= NOW() - INTERVAL '30 days') as current_avg_gpa,
    (SELECT COUNT(*) FROM fact_attendance 
     WHERE date_sk = TO_CHAR(NOW(), 'YYYYMMDD')::int) as today_attendance;

-- 2. Student Enrollment Trend (Last 12 Months)
SELECT 
    d.year,
    d.month_name,
    COUNT(DISTINCT fe.student_sk) as enrolled_students,
    COUNT(DISTINCT fe.course_sk) as active_courses
FROM fact_enrollment fe
JOIN dim_date d ON fe.date_sk = d.date_id
WHERE d.full_date >= NOW() - INTERVAL '12 months'
GROUP BY d.year, d.month_name, d.month
ORDER BY d.year DESC, d.month DESC;

-- 3. GPA Distribution by Major
SELECT 
    ds.major_name,
    COUNT(*) as student_count,
    ROUND(AVG(fs.gpa)::numeric, 2) as avg_gpa,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fs.gpa)::numeric, 2) as median_gpa,
    COUNT(CASE WHEN fs.gpa >= 3.5 THEN 1 END) as honors_students,
    COUNT(CASE WHEN fs.gpa < 2.0 THEN 1 END) as at_risk_students
FROM fact_score fs
JOIN dim_student ds ON fs.student_sk = ds.student_sk
WHERE ds.is_current = true
GROUP BY ds.major_name
ORDER BY avg_gpa DESC;

-- 4. Attendance Rate by Department
SELECT 
    ds.department_name,
    d.month_name,
    COUNT(*) as total_sessions,
    SUM(CASE WHEN fa.is_absent = false THEN 1 ELSE 0 END) as present_count,
    ROUND(SUM(CASE WHEN fa.is_absent = false THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) as attendance_rate
FROM fact_attendance fa
JOIN dim_student ds ON fa.student_sk = ds.student_sk
JOIN dim_date d ON fa.date_sk = d.date_id
WHERE d.full_date >= NOW() - INTERVAL '6 months'
GROUP BY ds.department_name, d.month_name, d.month
ORDER BY attendance_rate DESC;

-- 5. Course Performance Ranking
SELECT 
    dc.code,
    dc.name,
    dc.department_name,
    COUNT(DISTINCT fe.student_sk) as enrolled,
    ROUND(AVG(fe.grade_point)::numeric, 2) as avg_grade,
    ROUND(AVG(fe.total_score)::numeric, 2) as avg_score,
    COUNT(CASE WHEN fe.grade_point >= 3.0 THEN 1 END) as passing_count,
    ROUND(COUNT(CASE WHEN fe.grade_point >= 3.0 THEN 1 END)::numeric / COUNT(*) * 100, 2) as pass_rate
FROM fact_enrollment fe
JOIN dim_course dc ON fe.course_sk = dc.course_sk
GROUP BY dc.code, dc.name, dc.department_name
HAVING COUNT(*) >= 10
ORDER BY avg_grade DESC
LIMIT 20;

-- 6. Teacher Performance Metrics
SELECT 
    dt.first_name,
    dt.last_name,
    dt.department_name,
    COUNT(DISTINCT fe.student_sk) as total_students,
    COUNT(DISTINCT fe.course_sk) as courses_taught,
    ROUND(AVG(fe.grade_point)::numeric, 2) as avg_student_gpa,
    ROUND(AVG(fe.total_score)::numeric, 2) as avg_course_score
FROM fact_enrollment fe
JOIN dim_teacher dt ON fe.teacher_sk = dt.teacher_sk
GROUP BY dt.first_name, dt.last_name, dt.department_name
ORDER BY avg_student_gpa DESC;

-- 7. Daily Activity Heatmap
SELECT 
    d.day_of_week,
    d.day_name,
    EXTRACT(HOUR FROM fa.check_in_time) as hour_of_day,
    COUNT(*) as check_in_count
FROM fact_attendance fa
JOIN dim_date d ON fa.date_sk = d.date_id
WHERE d.full_date >= NOW() - INTERVAL '30 days'
GROUP BY d.day_of_week, d.day_name, EXTRACT(HOUR FROM fa.check_in_time)
ORDER BY d.day_of_week, hour_of_day;

-- 8. Student Retention/Attrition Analysis
WITH student_activity AS (
    SELECT 
        student_sk,
        DATE_TRUNC('month', enroll_date) as activity_month,
        COUNT(*) as courses_taken
    FROM fact_enrollment
    WHERE enroll_date >= NOW() - INTERVAL '12 months'
    GROUP BY student_sk, DATE_TRUNC('month', enroll_date)
)
SELECT 
    activity_month,
    COUNT(DISTINCT student_sk) as active_students,
    LAG(COUNT(DISTINCT student_sk)) OVER (ORDER BY activity_month) as previous_month,
    ROUND((COUNT(DISTINCT student_sk) - LAG(COUNT(DISTINCT student_sk)) OVER (ORDER BY activity_month))::numeric / 
          LAG(COUNT(DISTINCT student_sk)) OVER (ORDER BY activity_month) * 100, 2) as growth_rate
FROM student_activity
GROUP BY activity_month
ORDER BY activity_month DESC;

-- 9. Scholarship Impact Analysis
SELECT 
    CASE WHEN is_scholarship THEN 'Scholarship' ELSE 'Non-Scholarship' END as student_type,
    COUNT(*) as student_count,
    ROUND(AVG(fs.gpa)::numeric, 2) as avg_gpa,
    ROUND(AVG(fe.grade_point)::numeric, 2) as avg_course_performance,
    AVG(fe.total_score) as avg_exam_score
FROM fact_enrollment fe
JOIN dim_student ds ON fe.student_sk = ds.student_sk
JOIN fact_score fs ON ds.student_sk = fs.student_sk
GROUP BY ds.is_scholarship;

-- 10. Real-time Dashboard Metrics
SELECT 
    'Total Students Today' as metric,
    COUNT(DISTINCT student_sk)::text as value
FROM fact_attendance
WHERE date_sk = TO_CHAR(NOW(), 'YYYYMMDD')::int
UNION ALL
SELECT 
    'Average GPA (Current Semester)' as metric,
    ROUND(AVG(gpa)::numeric, 2)::text as value
FROM fact_score fs
JOIN dim_semester ds ON fs.semester_sk = ds.semester_sk
WHERE ds.is_current = true
UNION ALL
SELECT 
    'Pending Evaluations' as metric,
    COUNT(*)::text as value
FROM fact_evaluation
WHERE date_sk <= TO_CHAR(NOW(), 'YYYYMMDD')::int
  AND rating IS NULL;