# 03-visualize-data-simple.py
import os
import sys
import datetime

print("Installing required packages...")
os.system("pip install --quiet boto3 pandas matplotlib seaborn")
print("Packages installed")

# Now import the packages
import boto3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

# Define configuration directly in the script
print("Setting up configuration...")
ELYRA_RUN_NAME = os.getenv("ELYRA_RUN_NAME", datetime.datetime.now().strftime("weather-dataprocessing-%Y%m%d%H%M"))
RUN_ID = ELYRA_RUN_NAME
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio.minio-system.svc.cluster.local:9000")
MINIO_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "minio")
MINIO_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "elyra-airflow")
RAW_DATA_FILE = f"{RUN_ID}/raw_weather_data.csv"
PROCESSED_DATA_FILE = f"{RUN_ID}/processed_weather_data.csv"
TEMP_PLOT_FILE = f"{RUN_ID}/temperature_plot.png"
PRECIP_HUMID_PLOT_FILE = f"{RUN_ID}/precipitation_humidity_plot.png"
HTML_REPORT_FILE = f"{RUN_ID}/weather_report.html"
LOCAL_DATA_DIR = "data"

print(f"Configuration set:")
print(f"- Run ID: {RUN_ID}")
print(f"- MinIO endpoint: {MINIO_ENDPOINT}")
print(f"- MinIO bucket: {MINIO_BUCKET}")
print(f"- Processed data file: {PROCESSED_DATA_FILE}")
print(f"- Output files: {TEMP_PLOT_FILE}, {PRECIP_HUMID_PLOT_FILE}, {HTML_REPORT_FILE}")

# Set style
plt.style.use('ggplot')
sns.set_palette("Set2")

def get_s3_client():
    """Create and return MinIO/S3 client"""
    return boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'
    )

def read_processed_data():
    """Read processed data from MinIO"""
    s3_client = get_s3_client()
    print(f"Reading {PROCESSED_DATA_FILE} from MinIO bucket {MINIO_BUCKET}")
    
    try:
        response = s3_client.get_object(
            Bucket=MINIO_BUCKET,
            Key=PROCESSED_DATA_FILE
        )
        
        content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        df['date'] = pd.to_datetime(df['date'])
        
        print(f"Successfully loaded {len(df)} days of processed weather data")
        return df
    except Exception as e:
        print(f"Error reading processed data from MinIO: {e}")
        print("Listing available files to debug:")
        try:
            response = s3_client.list_objects_v2(
                Bucket=MINIO_BUCKET,
                Prefix=RUN_ID
            )
            if 'Contents' in response:
                for obj in response['Contents']:
                    print(f" - {obj['Key']}")
            else:
                print(f"No files found with run ID: {RUN_ID}")
        except Exception as e2:
            print(f"Error listing bucket contents: {e2}")
        
        raise e

def create_temperature_plot(df):
    """Create temperature visualization"""
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['max_temp'], 'r-', label='Max Temp (°C)')
    plt.plot(df['date'], df['avg_temp'], 'g-', label='Avg Temp (°C)')
    plt.plot(df['date'], df['min_temp'], 'b-', label='Min Temp (°C)')
    plt.fill_between(df['date'], df['min_temp'], df['max_temp'], alpha=0.2, color='gray')
    plt.title('Daily Temperature Range', fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Save locally
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    local_path = os.path.join(LOCAL_DATA_DIR, os.path.basename(TEMP_PLOT_FILE))
    plt.savefig(local_path)
    print(f"Saved temperature plot to {local_path}")
    
    return local_path

def create_precipitation_humidity_plot(df):
    """Create precipitation and humidity visualization"""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Precipitation (mm)', color=color)
    ax1.bar(df['date'], df['total_rain'], color=color, alpha=0.7, width=0.8)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Humidity (%)', color=color)
    ax2.plot(df['date'], df['avg_humidity'], color=color, linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Daily Precipitation and Average Humidity', fontsize=16)
    plt.grid(False)
    fig.tight_layout()
    
    # Save locally
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    local_path = os.path.join(LOCAL_DATA_DIR, os.path.basename(PRECIP_HUMID_PLOT_FILE))
    plt.savefig(local_path)
    print(f"Saved precipitation/humidity plot to {local_path}")
    
    return local_path

def create_html_report(temp_plot_path, precip_plot_path):
    """Create HTML report with plots"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Data Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            .plot {{ margin: 20px 0; text-align: center; }}
            .plot img {{ max-width: 100%; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>Weather Data Analysis Report</h1>
        <p>Report generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p>Run ID: {RUN_ID}</p>
        
        <div class="plot">
            <h2>Temperature Trends</h2>
            <img src="{os.path.basename(TEMP_PLOT_FILE)}" alt="Temperature Plot">
        </div>
        
        <div class="plot">
            <h2>Precipitation and Humidity</h2>
            <img src="{os.path.basename(PRECIP_HUMID_PLOT_FILE)}" alt="Precipitation and Humidity Plot">
        </div>
    </body>
    </html>
    """
    
    # Save locally
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    local_path = os.path.join(LOCAL_DATA_DIR, os.path.basename(HTML_REPORT_FILE))
    with open(local_path, 'w') as f:
        f.write(html_content)
    print(f"Saved HTML report to {local_path}")
    
    return local_path, html_content

def upload_plots_to_minio(temp_plot_path, precip_plot_path, html_report_path, html_content):
    """Upload plots and HTML report to MinIO"""
    s3_client = get_s3_client()
    
    # Upload temperature plot
    with open(temp_plot_path, 'rb') as file:
        s3_client.put_object(
            Bucket=MINIO_BUCKET,
            Key=TEMP_PLOT_FILE,
            Body=file,
            ContentType='image/png'
        )
    print(f"Uploaded temperature plot to MinIO at {TEMP_PLOT_FILE}")
    
    # Upload precipitation/humidity plot
    with open(precip_plot_path, 'rb') as file:
        s3_client.put_object(
            Bucket=MINIO_BUCKET,
            Key=PRECIP_HUMID_PLOT_FILE,
            Body=file,
            ContentType='image/png'
        )
    print(f"Uploaded precipitation/humidity plot to MinIO at {PRECIP_HUMID_PLOT_FILE}")
    
    # Upload HTML report
    s3_client.put_object(
        Bucket=MINIO_BUCKET,
        Key=HTML_REPORT_FILE,
        Body=html_content,
        ContentType='text/html'
    )
    print(f"Uploaded HTML report to MinIO at {HTML_REPORT_FILE}")

def main():
    """Main function for visualization"""
    print(f"Starting data visualization with Run ID: {RUN_ID}")
    try:
        df = read_processed_data()
        temp_plot_path = create_temperature_plot(df)
        precip_plot_path = create_precipitation_humidity_plot(df)
        html_report_path, html_content = create_html_report(temp_plot_path, precip_plot_path)
        upload_plots_to_minio(temp_plot_path, precip_plot_path, html_report_path, html_content)
        print("Visualization complete")
        print(f"All results stored in MinIO bucket {MINIO_BUCKET} under prefix {RUN_ID}/")
    except Exception as e:
        print(f"ERROR in data visualization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()