from airflow.operators.bash import BashOperator
from airflow import DAG
from airflow.utils.dates import days_ago

args = {
    "project_id": "weather-data-pipeline",
}

dag = DAG(
    "simple_weather_pipeline",
    default_args=args,
    schedule_interval="@once",
    start_date=days_ago(1 ),
    description="Simple weather data processing pipeline",
    is_paused_upon_creation=False,
)

# Task 1: Generate Data
generate_data = BashOperator(
    task_id="generate_data",
    bash_command="echo 'Generating weather data...'",
    dag=dag,
)

# Task 2: Process Data
process_data = BashOperator(
    task_id="process_data",
    bash_command="echo 'Processing weather data...'",
    dag=dag,
)

# Task 3: Visualize Data
visualize_data = BashOperator(
    task_id="visualize_data",
    bash_command="echo 'Visualizing weather data...'",
    dag=dag,
)

# Set task dependencies
generate_data >> process_data >> visualize_data
