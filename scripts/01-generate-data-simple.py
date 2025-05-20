# 01-generate-data-simple.py
import os
import sys
import datetime

print("Installing required packages...")
os.system("pip install --quiet boto3 pandas numpy")
print("Packages installed")

# Now import the packages
import boto3
import pandas as pd
import numpy as np
from io import StringIO

# Define configuration directly in the script (no import needed)
print("Setting up configuration...")
ELYRA_RUN_NAME = os.getenv("ELYRA_RUN_NAME", datetime.datetime.now().strftime("weather-dataprocessing-%Y%m%d%H%M"))
RUN_ID = ELYRA_RUN_NAME
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio.minio-system.svc.cluster.local:9000")
MINIO_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "minio")
MINIO_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "elyra-airflow")
RAW_DATA_FILE = f"{RUN_ID}/raw_weather_data.csv"
LOCAL_DATA_DIR = "data"

print(f"Configuration set:")
print(f"- Run ID: {RUN_ID}")
print(f"- MinIO endpoint: {MINIO_ENDPOINT}")
print(f"- MinIO bucket: {MINIO_BUCKET}")
print(f"- Raw data file: {RAW_DATA_FILE}")

# Test MinIO connection
def test_minio_connection():
    """Test MinIO connection and bucket access"""
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name='us-east-1'
        )
        
        # Test listing buckets
        response = s3_client.list_buckets()
        print(f"MinIO connection successful. Available buckets:")
        for bucket in response['Buckets']:
            print(f"- {bucket['Name']}")
            
        # Test specified bucket
        try:
            s3_client.head_bucket(Bucket=MINIO_BUCKET)
            print(f"Bucket '{MINIO_BUCKET}' exists and is accessible.")
        except Exception as e:
            print(f"Error accessing bucket '{MINIO_BUCKET}': {e}")
            
        return True
    except Exception as e:
        print(f"MinIO connection test failed: {e}")
        return False

def generate_weather_data():
    """Generate synthetic weather data"""
    print("Generating synthetic weather data...")
    
    # Create date range for the past month
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')
    
    # Generate data with reproducible seed
    np.random.seed(42)
    temperatures = np.random.normal(loc=22, scale=5, size=len(dates))
    temperatures = [round(max(min(t, 35), -5), 1) for t in temperatures]
    
    humidities = np.random.normal(loc=60, scale=15, size=len(dates))
    humidities = [round(max(min(h, 100), 20), 1) for h in humidities]
    
    wind_speeds = np.random.lognormal(mean=1.5, sigma=0.5, size=len(dates))
    wind_speeds = [round(min(w, 100), 1) for w in wind_speeds]
    
    precipitation = np.zeros(len(dates))
    rain_mask = np.random.random(len(dates)) < 0.2
    precipitation[rain_mask] = np.random.exponential(scale=5, size=sum(rain_mask))
    precipitation = [round(p, 1) for p in precipitation]
    
    # Create dataframe
    weather_data = pd.DataFrame({
        'date': dates,
        'temperature': temperatures,
        'humidity': humidities,
        'wind_speed': wind_speeds,
        'precipitation': precipitation
    })
    
    print(f"Generated {len(weather_data)} rows of weather data")
    return weather_data

def save_data_to_minio(df):
    """Save dataframe to MinIO"""
    # Save locally for debugging if needed
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    local_path = os.path.join(LOCAL_DATA_DIR, os.path.basename(RAW_DATA_FILE))
    df.to_csv(local_path, index=False)
    print(f"Saved data locally to {local_path}")
    
    # Save to MinIO
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'
    )
    
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    s3_client.put_object(
        Bucket=MINIO_BUCKET,
        Key=RAW_DATA_FILE,
        Body=csv_buffer.getvalue()
    )
    print(f"Successfully saved {RAW_DATA_FILE} to MinIO bucket {MINIO_BUCKET}")

def main():
    """Main function to generate and save data"""
    print(f"Starting data generation process with Run ID: {RUN_ID}")
    try:
        # Test MinIO connection first
        if not test_minio_connection():
            print("MinIO connection failed, exiting.")
            sys.exit(1)
            
        weather_data = generate_weather_data()
        save_data_to_minio(weather_data)
        print(f"Data generation complete. Run ID: {RUN_ID}")
    except Exception as e:
        print(f"ERROR in data generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()