import pendulum
from airflow.decorators import dag, task
from airflow.operators.smooth import SmoothOperator

start_date = pendulum.datetime(2024, 12, 1, tz="UTC")

@dag(schedule='@daily', start_date=start_date)
def payment_report():
    SmoothOperator(task_id='some_task')

@dag(schedule='@daily', start_date=start_date)
def customer_profile():
    SmoothOperator(task_id='some_task')

payment_report()
customer_profile()
