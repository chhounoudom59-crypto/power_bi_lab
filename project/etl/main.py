import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extract import Extractor
import etl.transform as transform
from etl.load import Loader
from etl.config import SOURCE_DB, STAGING_DB, WAREHOUSE_DB
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting ETL Pipeline...")
        
        # Initialize components
        extractor = Extractor(SOURCE_DB, STAGING_DB)
        loader = Loader(WAREHOUSE_DB)
        
        logger.info("Extracting raw tables...")
        df_student = extractor.extract_table('Student')
        df_major = extractor.extract_table('Major')
        df_teacher = extractor.extract_table('Teacher')
        df_course = extractor.extract_table('Course')
        df_class = extractor.extract_table('Class')
        df_semester = extractor.extract_table('Semester')
        df_evaluation = extractor.extract_table('Evaluation')
        df_user = extractor.extract_table('User')
        
        df_enroll = extractor.extract_table('Enroll')
        df_schedule = extractor.extract_table('Schedule')
        df_attendance = extractor.extract_table('Attendance')
        df_sched_times = extractor.extract_table('ScheduleTimes')
        
        df_score = extractor.extract_table('Score')
        df_score_sem = extractor.extract_table('ScoreSemester')
        
        df_eval_rate = extractor.extract_table('EvaluationRating')
        df_eval_text = extractor.extract_table('EvaluationText')
        df_permission = extractor.extract_table('PermissionRequest')
        
        logger.info("Building and loading dimensions...")
        date_df = transform.build_dim_date()
        loader.load_table(date_df, 'dim_date')

        dim_student = transform.build_dim_student(df_student, df_major)
        loader.load_table(dim_student, 'dim_student')

        dim_teacher = transform.build_dim_teacher(df_teacher)
        loader.load_table(dim_teacher, 'dim_teacher')

        dim_course = transform.build_dim_course(df_course)
        loader.load_table(dim_course, 'dim_course')

        dim_class = transform.build_dim_class(df_class, df_semester)
        loader.load_table(dim_class, 'dim_class')

        dim_evaluation_question = transform.build_dim_evaluation_question(df_evaluation)
        loader.load_table(dim_evaluation_question, 'dim_evaluation_question')

        dim_user = transform.build_dim_user(df_user)
        loader.load_table(dim_user, 'dim_user')

        logger.info("Building and loading facts...")
        fact_enrollment = transform.build_fact_enrollment(df_enroll, df_schedule, df_class, df_semester)
        loader.load_table(fact_enrollment, 'fact_enrollment')

        fact_attendance = transform.build_fact_attendance(df_attendance, df_sched_times, df_schedule, df_user)
        loader.load_table(fact_attendance, 'fact_attendance')

        fact_grade = transform.build_fact_grade(df_score, df_score_sem, df_semester)
        loader.load_table(fact_grade, 'fact_grade')

        fact_evaluation_rating = transform.build_fact_evaluation_rating(df_eval_rate, df_enroll, df_schedule, df_class, df_semester)
        loader.load_table(fact_evaluation_rating, 'fact_evaluation_rating')

        fact_evaluation_text = transform.build_fact_evaluation_text(df_eval_text, df_enroll, df_schedule)
        loader.load_table(fact_evaluation_text, 'fact_evaluation_text')

        fact_permission_request = transform.build_fact_permission_request(df_permission, df_user)
        loader.load_table(fact_permission_request, 'fact_permission_request')
        
        logger.info("ETL Pipeline completed successfully!")
        print("ETL SUCCESS - Warehouse updated!")
        
    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")
        print(f" ETL FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()