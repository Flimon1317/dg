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

dag = DAG('abhishek', default_args=default_args, schedule_interval="@hourly")

loop_etl_task = BashOperator(task_id='loop_etl_v1',bash_command='cd /home/abhishek/Documents/dg && python manage.py loop_etl >> /tmp/master_etl.log 2>&1',dag=dag)

loop_data_email_task = BashOperator(task_id='loop_data_email_v1', bash_command='cd /home/abhishek/Documents/dg && python manage.py loop_data_email',dag=dag)

training_data_email_task = BashOperator(task_id='training_data_email_v1', bash_command='cd /home/abhishek/Documents/dg && python manage.py training_data_email',dag=dag)

generate_csv_task = BashOperator(task_id='generate_csv_v1', bash_command='cd /home/abhishek/Documents/dg && python manage.py generate_csv',dag=dag)

# email_etl_status_task = BashOperator(task_id='email_etl_status_v1', bash_command='/home/ubuntu/.virtualenv/dg_production/bin/python /home/ubuntu/code/dg_git/scripts/test.py',dag=dag)


# t2 = BashOperator(task_id='sleep',depends_on_past=False,bash_command='sleep 5',dag=dag)

loop_data_email_task.set_upstream(loop_etl_task)
generate_csv_task.set_upstream(loop_etl_task)
# email_etl_status_task.set_upstream(loop_etl_task)
