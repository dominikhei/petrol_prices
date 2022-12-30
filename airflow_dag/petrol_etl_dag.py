from airflow import DAG
from datetime import datetime
from datetime import timedelta
from airflow.operators.docker_operator import DockerOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022,12,27),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'petrol_prices',
    default_args=default_args,
    description='',
    schedule_interval=None,
)

load = DockerOperator(
    task_id='run_loading_container',
    image='application-pythonapp',
    api_version='auto',
    auto_remove=True,
    docker_url="unix://var/run/docker.sock",
    network_mode="bridge",
    dag=dag
)

load
