#!/bin/bash

# Set up log file
LOG_FILE="/tmp/dag-processor.log"
echo "Starting Airflow 3.0 post-processing script at $(date)" > $LOG_FILE

# Create the output directory with proper permissions
mkdir -p /opt/airflow/dags/elyra_generated
chmod 777 /opt/airflow/dags/elyra_generated

# Set the Airflow namespace to use
AIRFLOW_NAMESPACE="${AIRFLOW_NAMESPACE:-airflow-new}"
echo "$(date) - Using Airflow namespace: $AIRFLOW_NAMESPACE" >> $LOG_FILE

# Function to process a directory using the Python script
process_directory() {
  local dir="$1"
  echo "$(date) - Checking directory: $dir" >> $LOG_FILE
  
  if [ -d "$dir" ]; then
    echo "Directory exists: $dir" >> $LOG_FILE
    
    # Run the Python compatibility checker
    python3 /elyra-config/compatibility_checker.py "$dir" --namespace "$AIRFLOW_NAMESPACE" --recursive >> $LOG_FILE 2>&1
    
    echo "$(date) - Processed directory: $dir" >> $LOG_FILE
  else
    echo "Directory does not exist: $dir" >> $LOG_FILE
  fi
}

# Function to find git repos
find_git_repos() {
  echo "$(date) - Searching for git repos" >> $LOG_FILE
  find / -name .git -type d 2>/dev/null | while read gitdir; do
    echo "Found git repo: $gitdir" >> $LOG_FILE
    if [ -d "$gitdir/../tests/dags" ]; then
      echo "Found tests/dags directory in repo: $gitdir/../tests/dags" >> $LOG_FILE
      process_directory "$gitdir/../tests/dags"
    fi
  done
}

# Main loop
while true; do
  echo "$(date) - Starting check cycle" >> $LOG_FILE
  
  # Check important directories
  process_directory "/opt/airflow/dags"
  process_directory "/opt/airflow/dags/elyra_generated"
  process_directory "/opt/airflow/dags/repo/tests/dags"
  
  # Find git repos and check their dags directories
  find_git_repos
  
  # Sleep before next check
  echo "$(date) - Finished check cycle, sleeping for 60 seconds" >> $LOG_FILE
  sleep 60
done