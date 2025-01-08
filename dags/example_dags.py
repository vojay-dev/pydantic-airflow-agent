import pendulum
from airflow.decorators import dag
from airflow.operators.smooth import SmoothOperator

start_date = pendulum.datetime(2024, 12, 1, tz="UTC")

@dag(schedule='@daily', start_date=start_date, description='Aggregate payment data, also used in internal newsletter')
def payment_report():
    SmoothOperator(task_id='some_task')

@dag(schedule='@daily', start_date=start_date, description='Data source for the CRM system')
def customer_profile():
    SmoothOperator(task_id='some_task')

payment_report()
customer_profile()
