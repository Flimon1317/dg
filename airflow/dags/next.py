import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(seconds=10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('next', default_args=default_args, schedule_interval="@daily")

# op = DummyOperator(task_id='dummy', dag=dag)
t1 = BashOperator(task_id='loop_etl',bash_command='cd ~/Documents/dg && python manage.py loop_etl',dag=dag)

t2 = BashOperator(task_id='sleep',depends_on_past=False,bash_command='sleep 5',dag=dag)

t2.set_upstream(t1)
