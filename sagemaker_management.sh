#!/bin/bash
# ======================================
# SageMaker Management Script
# สำหรับจัดการ SageMaker Instance และ Training
# ======================================

# Configuration
INSTANCE_NAME="paddle-ocr-training"
INSTANCE_TYPE="ml.g4dn.xlarge"
ACCOUNT_ID="484468818942"
ROLE_NAME="AmazonSageMaker-ExecutionRole-20250729T154576"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
S3_BUCKET="sagemaker-ocr-train-bucket"
REGION="ap-southeast-1"
NOTEBOOK_FILE="paddle_ocr_sagemaker_training.ipynb"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}🔍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function: Check instance status
check_instance_status() {
    print_status "Checking SageMaker instance status..."
    
    STATUS=$(aws sagemaker describe-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION" \
        --query 'NotebookInstanceStatus' \
        --output text 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "📊 Instance Status: $STATUS"
        
        if [ "$STATUS" = "InService" ]; then
            print_success "Instance is ready for training!"
            
            # Get Jupyter URL
            URL=$(aws sagemaker describe-notebook-instance \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION" \
                --query 'Url' \
                --output text)
            
            echo -e "${GREEN}🔗 Jupyter URL: https://$URL${NC}"
            return 0
        elif [ "$STATUS" = "Pending" ]; then
            print_warning "Instance is starting up..."
            return 1
        elif [ "$STATUS" = "Stopped" ]; then
            print_warning "Instance is stopped. Use 'start' command to start it."
            return 1
        else
            print_warning "Instance status: $STATUS"
            return 1
        fi
    else
        print_error "Failed to get instance status. Check instance name and region."
        return 1
    fi
}

# Function: Start instance
start_instance() {
    print_status "Starting SageMaker instance..."
    
    aws sagemaker start-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        print_success "Start command sent successfully"
        print_status "Waiting for instance to be ready..."
        
        aws sagemaker wait notebook-instance-in-service \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION"
        
        if [ $? -eq 0 ]; then
            print_success "Instance is now ready!"
            check_instance_status
        else
            print_error "Timeout waiting for instance to start"
        fi
    else
        print_error "Failed to start instance"
    fi
}

# Function: Stop instance
stop_instance() {
    print_warning "Stopping SageMaker instance to save costs..."
    
    aws sagemaker stop-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        print_success "Stop command sent successfully"
        print_status "Waiting for instance to stop..."
        
        aws sagemaker wait notebook-instance-stopped \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION"
        
        if [ $? -eq 0 ]; then
            print_success "Instance stopped successfully"
        else
            print_warning "Timeout waiting for instance to stop"
        fi
    else
        print_error "Failed to stop instance"
    fi
}

# Function: Check S3 data
check_s3_data() {
    print_status "Checking S3 training data..."
    
    # Check if bucket exists
    aws s3 ls "s3://$S3_BUCKET" --region "$REGION" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        print_error "Cannot access S3 bucket: $S3_BUCKET"
        return 1
    fi
    
    print_success "S3 bucket accessible: $S3_BUCKET"
    
    # Check important files
    echo "📋 Checking important files:"
    
    files=(
        "recognition-data/annotations/train_annotation.txt"
        "recognition-data/annotations/val_annotation.txt"
        "recognition-data/metadata/character_dict.txt"
        "recognition-data/metadata/dataset_info.json"
    )
    
    for file in "${files[@]}"; do
        aws s3 ls "s3://$S3_BUCKET/$file" --region "$REGION" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            size=$(aws s3 ls "s3://$S3_BUCKET/$file" --region "$REGION" --human-readable | awk '{print $3 " " $4}')
            echo -e "  ${GREEN}✅ $file ($size)${NC}"
        else
            echo -e "  ${RED}❌ $file - missing${NC}"
        fi
    done
    
    # Count images
    train_count=$(aws s3 ls "s3://$S3_BUCKET/recognition-data/images/train/" --region "$REGION" --recursive | wc -l)
    val_count=$(aws s3 ls "s3://$S3_BUCKET/recognition-data/images/val/" --region "$REGION" --recursive | wc -l)
    
    echo "📊 Dataset Summary:"
    echo "   Training images: $train_count"
    echo "   Validation images: $val_count"
}

# Function: Open Jupyter
open_jupyter() {
    if check_instance_status > /dev/null 2>&1; then
        URL=$(aws sagemaker describe-notebook-instance \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION" \
            --query 'Url' \
            --output text)
        
        FULL_URL="https://$URL"
        print_success "Opening Jupyter in browser..."
        echo -e "${BLUE}🔗 URL: $FULL_URL${NC}"
        
        # Try to open in browser (macOS)
        open "$FULL_URL" 2>/dev/null || echo "Please open this URL in your browser: $FULL_URL"
    else
        print_error "Instance is not ready. Please start it first."
    fi
}

# Function: Monitor training progress
monitor_training() {
    print_status "Monitoring training progress..."
    echo "📊 This will check S3 for new training outputs every 30 seconds"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    while true; do
        # Check for training outputs
        training_outputs=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive 2>/dev/null | wc -l)
        
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] Training outputs in S3: $training_outputs files"
        
        # Check for latest model
        latest_model=$(aws s3 ls "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive | grep -E "(latest|best)" | tail -1)
        if [ -n "$latest_model" ]; then
            echo "  📁 Latest model: $(echo $latest_model | awk '{print $4}')"
        fi
        
        sleep 30
    done
}

# Function: Download results
download_results() {
    print_status "Downloading training results from S3..."
    
    local_dir="./training_results_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$local_dir"
    
    echo "📥 Downloading to: $local_dir"
    
    aws s3 sync "s3://$S3_BUCKET/training-results/" "$local_dir/" --region "$REGION"
    
    if [ $? -eq 0 ]; then
        print_success "Results downloaded successfully!"
        echo "📁 Local directory: $local_dir"
        
        # Show summary
        echo "📊 Downloaded files:"
        find "$local_dir" -type f | head -10
        total_files=$(find "$local_dir" -type f | wc -l)
        echo "   ... and $((total_files - 10)) more files" 
    else
        print_error "Failed to download results"
    fi
}

# Function: Clean up
cleanup() {
    print_warning "⚠️  CLEANUP WARNING ⚠️"
    echo "This will:"
    echo "1. Stop the SageMaker instance"
    echo "2. Optionally delete the instance"
    echo "3. Optionally delete S3 training data"
    echo ""
    
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Stop instance
        stop_instance
        
        # Ask about deletion
        echo ""
        read -p "Delete the SageMaker instance? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Deleting SageMaker instance..."
            aws sagemaker delete-notebook-instance \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION"
            
            if [ $? -eq 0 ]; then
                print_success "Instance deletion initiated"
            else
                print_error "Failed to delete instance"
            fi
        fi
        
        # Ask about S3 cleanup
        echo ""
        read -p "Delete S3 training data? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Deleting S3 data..."
            aws s3 rm "s3://$S3_BUCKET/recognition-data/" --region "$REGION" --recursive
            aws s3 rm "s3://$S3_BUCKET/training-results/" --region "$REGION" --recursive
            
            print_success "S3 cleanup completed"
        fi
    else
        echo "Cleanup cancelled"
    fi
}

# Function: Show usage
show_usage() {
    echo "🚀 SageMaker Management Script"
    echo "=============================="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status     - Check instance status and get Jupyter URL"
    echo "  start      - Start the SageMaker instance"
    echo "  stop       - Stop the SageMaker instance"
    echo "  jupyter    - Open Jupyter notebook in browser"
    echo "  check-data - Check S3 training data"
    echo "  monitor    - Monitor training progress"
    echo "  download   - Download training results from S3"
    echo "  cleanup    - Stop/delete instance and clean up resources"
    echo "  help       - Show this help message"
    echo ""
    echo "Configuration:"
    echo "  Instance: $INSTANCE_NAME ($INSTANCE_TYPE)"
    echo "  S3 Bucket: $S3_BUCKET"
    echo "  Region: $REGION"
    echo ""
    echo "Examples:"
    echo "  $0 status          # Check current status"
    echo "  $0 jupyter         # Open Jupyter notebook"
    echo "  $0 monitor         # Monitor training progress"
    echo "  $0 stop            # Stop instance to save costs"
}

# Main script logic
case "${1:-help}" in
    "status")
        check_instance_status
        ;;
    "start")
        start_instance
        ;;
    "stop")
        stop_instance
        ;;
    "jupyter")
        open_jupyter
        ;;
    "check-data")
        check_s3_data
        ;;
    "monitor")
        monitor_training
        ;;
    "download")
        download_results
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
