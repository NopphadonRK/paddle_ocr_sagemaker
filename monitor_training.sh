#!/bin/bash
# ======================================
# Training Progress Monitor
# ติดตาม progress การเทรนแบบ real-time
# ======================================

S3_BUCKET="sagemaker-ocr-train-bucket"
REGION="ap-southeast-1"
CHECK_INTERVAL=30  # seconds

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}📊 PaddleOCR Training Progress Monitor${NC}"
echo "======================================"
echo "Checking every $CHECK_INTERVAL seconds"
echo "Press Ctrl+C to stop"
echo ""

# Initialize counters
iteration=0
last_model_count=0
last_log_count=0

while true; do
    iteration=$((iteration + 1))
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${BLUE}[Check #$iteration - $timestamp]${NC}"
    
    # Check S3 training outputs
    echo "🔍 Checking S3 training outputs..."
    
    # Count model files
    model_count=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive 2>/dev/null | grep -E "\.(pdparams|pdopt|pdmodel)" | wc -l)
    
    # Count log files
    log_count=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive 2>/dev/null | grep -E "\.(log|json|txt)" | wc -l)
    
    # Count all files
    total_files=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive 2>/dev/null | wc -l)
    
    echo "📁 Training outputs: $total_files files total"
    echo "   🎯 Models: $model_count files"
    echo "   📄 Logs: $log_count files"
    
    # Check for changes
    if [ $model_count -gt $last_model_count ]; then
        echo -e "${GREEN}🎉 New model checkpoint detected!${NC}"
        
        # Show latest model
        latest_model=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive | grep -E "\.(pdparams)" | tail -1 | awk '{print $4}')
        if [ -n "$latest_model" ]; then
            echo "   📁 Latest: $latest_model"
        fi
    fi
    
    if [ $log_count -gt $last_log_count ]; then
        echo -e "${GREEN}📝 New logs available${NC}"
    fi
    
    # Check latest training summary
    summary_file=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive | grep "training_summary.json" | tail -1 | awk '{print $4}')
    if [ -n "$summary_file" ]; then
        echo "📊 Latest summary: $summary_file"
        
        # Try to get basic info from summary
        temp_summary="/tmp/training_summary_temp.json"
        aws s3 cp "s3://$S3_BUCKET/$summary_file" "$temp_summary" --region "$REGION" --quiet 2>/dev/null
        
        if [ -f "$temp_summary" ]; then
            algorithm=$(cat "$temp_summary" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('training_info', {}).get('algorithm', 'Unknown'))" 2>/dev/null)
            epochs=$(cat "$temp_summary" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('training_info', {}).get('epochs', 'Unknown'))" 2>/dev/null)
            duration=$(cat "$temp_summary" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('training_info', {}).get('duration', 'Unknown'))" 2>/dev/null)
            
            if [ "$algorithm" != "Unknown" ]; then
                echo "   🤖 Algorithm: $algorithm"
                echo "   🔄 Epochs: $epochs"
                echo "   ⏱️  Duration: $duration"
            fi
            
            rm -f "$temp_summary"
        fi
    fi
    
    # Show recent activity
    echo "🕐 Recent activity:"
    recent_files=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive | tail -3)
    if [ -n "$recent_files" ]; then
        echo "$recent_files" | while read -r line; do
            if [ -n "$line" ]; then
                file_date=$(echo "$line" | awk '{print $1 " " $2}')
                file_name=$(echo "$line" | awk '{print $4}' | sed 's/.*\///')
                echo "   📄 $file_date - $file_name"
            fi
        done
    else
        echo -e "${YELLOW}   ⚠️  No training outputs yet${NC}"
    fi
    
    # Update counters
    last_model_count=$model_count
    last_log_count=$log_count
    
    echo ""
    
    # Training completion check
    if [ $total_files -gt 0 ]; then
        # Check for completion indicators
        completion_indicators=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive | grep -E "(training_summary|final|completed)" | wc -l)
        
        if [ $completion_indicators -gt 0 ]; then
            echo -e "${GREEN}🎉 Training appears to be completed!${NC}"
            echo "📋 Run './sagemaker_management.sh download' to get results"
            break
        fi
    fi
    
    # Wait for next check
    echo "⏳ Waiting $CHECK_INTERVAL seconds for next check..."
    sleep $CHECK_INTERVAL
    echo ""
done
