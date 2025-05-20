# 02-process-data-simple.py
import os
import sys
import datetime

print("Installing required packages...")
os.system("pip install --quiet boto3 pandas")
print("Packages installed")

# Now import the packages
import boto3
import pandas as pd
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
LOCAL_DATA_DIR = "data"

print(f"Configuration set:")
print(f"- Run ID: {RUN_ID}")
print(f"- MinIO endpoint: {MINIO_ENDPOINT}")
print(f"- Raw data file: {RAW_DATA_FILE}")
print(f"- Processed data file: {PROCESSED_DATA_FILE}")

def get_s3_client():
    """Create and return MinIO/S3 client"""
    return boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'
    )

def read_data_from_minio():
    """Read raw data from MinIO"""
    s3_client = get_s3_client()
    print(f"Reading {RAW_DATA_FILE} from MinIO bucket {MINIO_BUCKET}")
    
    try:
        response = s3_client.get_object(
            Bucket=MINIO_BUCKET,
            Key=RAW_DATA_FILE
        )
        
        content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        print(f"Successfully loaded {len(df)} rows from MinIO")
        return df
    except Exception as e:
        print(f"Error reading data from MinIO: {e}")
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
                print("No files found with this run ID")
        except Exception as e2:
            print(f"Error listing bucket contents: {e2}")
        
        raise e

def process_weather_data(df):
    """Process the weather data to calculate daily statistics"""
    print("Processing weather data...")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate daily statistics
    daily_stats = df.groupby(df['date'].dt.date).agg({
        'temperature': ['mean', 'min', 'max'],
        'humidity': ['mean', 'min', 'max'],
        'wind_speed': ['mean', 'max'],
        'precipitation': 'sum'
    }).reset_index()
    
    # Flatten column names
    daily_stats.columns = [
        'date', 'avg_temp', 'min_temp', 'max_temp', 
        'avg_humidity', 'min_humidity', 'max_humidity', 
        'avg_wind', 'max_wind', 'total_rain'
    ]
    
    # Round to one decimal place
    numeric_cols = daily_stats.columns.drop('date')
    daily_stats[numeric_cols] = daily_stats[numeric_cols].round(1)
    
    print(f"Processed data to {len(daily_stats)} daily records")
    return daily_stats

def save_processed_data(df):
    """Save processed data to MinIO"""
    # Save locally if needed
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    local_path = os.path.join(LOCAL_DATA_DIR, os.path.basename(PROCESSED_DATA_FILE))
    df.to_csv(local_path, index=False)
    print(f"Saved processed data locally to {local_path}")
    
    # Save to MinIO
    s3_client = get_s3_client()
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    s3_client.put_object(
        Bucket=MINIO_BUCKET,
        Key=PROCESSED_DATA_FILE,
        Body=csv_buffer.getvalue()
    )
    print(f"Successfully saved processed data to {PROCESSED_DATA_FILE}")

def main():
    """Main function to process data"""
    print(f"Starting data processing with Run ID: {RUN_ID}")
    try:
        raw_data = read_data_from_minio()
        processed_data = process_weather_data(raw_data)
        save_processed_data(processed_data)
        print("Data processing complete")
    except Exception as e:
        print(f"ERROR in data processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()