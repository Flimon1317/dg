import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2017, 4, 23, 12),
    'email': ['system@digitalgreen.org'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('loop_email', default_args=default_args, schedule_interval="@daily")

loop_data_email_task = BashOperator(task_id='loop_data_email_v1', bash_command='cd /home/abhishek/Documents/dg && python manage.py loop_data_email',dag=dag)
