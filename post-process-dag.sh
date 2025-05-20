#!/bin/bash

# Set up log file
LOG_FILE="/tmp/dag-processor.log"
echo "Starting post-processing script at $(date)" > $LOG_FILE

# Create the output directory with proper permissions
mkdir -p /opt/airflow/dags/elyra_generated
chmod 777 /opt/airflow/dags/elyra_generated

# Function to process a DAG file
process_dag() {
  local dagfile="$1"
  local airflow_namespace="$2"
  echo "$(date) - Processing $dagfile" >> $LOG_FILE
  
  # Make a backup before any changes
  cp "$dagfile" "${dagfile}.bak"
  
  # Fix imports with more aggressive pattern matching
  sed -i 's/from airflow\.contrib\.operators\.kubernetes_pod_operator import KubernetesPodOperator/from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator/g' "$dagfile"
  sed -i 's/from airflow\.contrib\.kubernetes\.volume_mount import VolumeMount/from kubernetes.client.models import V1VolumeMount as VolumeMount/g' "$dagfile"
  sed -i 's/from airflow\.contrib\.kubernetes\.volume import Volume/from kubernetes.client.models import V1Volume as Volume/g' "$dagfile"
  sed -i 's/from airflow\.kubernetes\.secret import Secret/from airflow.providers.cncf.kubernetes.secret import Secret/g' "$dagfile"
  
  # Fix Schedule in Airflow 3.0 (schedule_interval -> schedule)
  sed -i 's/schedule_interval=/schedule=/g' "$dagfile"
  
  # Replace days_ago with pendulum datetime
  sed -i 's/from airflow\.utils\.dates import days_ago/import pendulum/g' "$dagfile"
  sed -i 's/start_date=days_ago(1)/start_date=pendulum.datetime(2025, 5, 19, tz="UTC")/g' "$dagfile"
  sed -i 's/start_date=days_ago([0-9])/start_date=pendulum.datetime(2025, 5, 19, tz="UTC")/g' "$dagfile"
  
  # Fix namespace to use the provided namespace 
  sed -i "s/namespace=\"airflow\"/namespace=\"${airflow_namespace}\"/g" "$dagfile"
  
  # Fix config_file - Python None vs string "None"
  sed -i 's/config_file="None"/config_file=None/g' "$dagfile"
  
  # Fix ELYRA_RUNTIME_ENV environment variable
  sed -i "s/\"ELYRA_RUNTIME_ENV\": \"airflow\"/\"ELYRA_RUNTIME_ENV\": \"${airflow_namespace}\"/g" "$dagfile"
  
  # Add a marker to show this was processed
  if ! grep -q "# PROCESSED_BY_SCRIPT" "$dagfile"; then
    sed -i '1s/^/# PROCESSED_BY_SCRIPT\n# Modified for Airflow 3.0 compatibility\n/' "$dagfile"
  fi
  
  echo "$(date) - Completed processing $dagfile" >> $LOG_FILE
  
  # Log the first few lines of the file after processing
  echo "First 10 lines of processed file:" >> $LOG_FILE
  head -n 10 "$dagfile" >> $LOG_FILE
}

# Check a directory for DAG files
check_directory() {
  local dir="$1"
  local airflow_namespace="${2:-airflow-new}"
  echo "$(date) - Checking directory: $dir (namespace: $airflow_namespace)" >> $LOG_FILE
  
  if [ -d "$dir" ]; then
    echo "Directory exists: $dir" >> $LOG_FILE
    find "$dir" -type f -name "*.py" 2>/dev/null | while read dagfile; do
      echo "Found file: $dagfile" >> $LOG_FILE
      if ! grep -q "# PROCESSED_BY_SCRIPT" "$dagfile"; then
        echo "$(date) - Processing new file: $dagfile" >> $LOG_FILE
        process_dag "$dagfile" "$airflow_namespace"
      else
        echo "$(date) - File already processed: $dagfile" >> $LOG_FILE
      fi
    done
  else
    echo "Directory does not exist: $dir" >> $LOG_FILE
  fi
}

# List all git repos to help debug
find_git_repos() {
  local airflow_namespace="${1:-airflow-new}"
  echo "$(date) - Searching for git repos" >> $LOG_FILE
  find / -name .git -type d 2>/dev/null | while read gitdir; do
    echo "Found git repo: $gitdir" >> $LOG_FILE
    if [ -d "$gitdir/../tests/dags" ]; then
      echo "Found tests/dags directory in repo: $gitdir/../tests/dags" >> $LOG_FILE
      check_directory "$gitdir/../tests/dags" "$airflow_namespace"
    fi
  done
}

# Set the Airflow namespace to use
AIRFLOW_NAMESPACE="${AIRFLOW_NAMESPACE:-airflow-new}"
echo "$(date) - Using Airflow namespace: $AIRFLOW_NAMESPACE" >> $LOG_FILE

# Main loop
while true; do
  echo "$(date) - Starting check cycle" >> $LOG_FILE
  
  # Check important directories
  check_directory "/opt/airflow/dags" "$AIRFLOW_NAMESPACE"
  check_directory "/opt/airflow/dags/elyra_generated" "$AIRFLOW_NAMESPACE"
  check_directory "/opt/airflow/dags/repo/tests/dags" "$AIRFLOW_NAMESPACE"
  
  # Find git repos and check their dags directories
  find_git_repos "$AIRFLOW_NAMESPACE"
  
  # Sleep before next check
  echo "$(date) - Finished check cycle, sleeping for 10 seconds" >> $LOG_FILE
  sleep 10
done