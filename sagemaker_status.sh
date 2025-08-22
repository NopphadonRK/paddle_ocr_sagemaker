#!/bin/bash
# SageMaker Instance Status & Management Script
# สำหรับตรวจสอบและจัดการ SageMaker instance

# ข้อมูลการตั้งค่า
INSTANCE_NAME="paddle-ocr-training"
REGION="ap-southeast-1"
S3_BUCKET="sagemaker-ocr-train-bucket"
ACCOUNT_ID="484468818942"

echo "🚀 SageMaker Instance Management"
echo "=================================="
echo "📝 Instance: $INSTANCE_NAME"
echo "🌍 Region: $REGION"
echo "📁 S3 Bucket: $S3_BUCKET"
echo ""

# ฟังก์ชันตรวจสอบสถานะ
check_instance_status() {
    echo "🔍 Checking instance status..."
    
    STATUS=$(aws sagemaker describe-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION" \
        --query 'NotebookInstanceStatus' \
        --output text 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "✅ Instance Status: $STATUS"
        
        if [ "$STATUS" = "InService" ]; then
            # แสดง URL สำหรับเข้า Jupyter
            URL=$(aws sagemaker describe-notebook-instance \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION" \
                --query 'Url' \
                --output text)
            echo "🔗 Jupyter URL: https://$URL"
            echo ""
            echo "💡 Ready for training!"
            return 0
        elif [ "$STATUS" = "Stopped" ]; then
            echo "⚠️  Instance is stopped. Starting..."
            start_instance
            return 1
        else
            echo "⏳ Instance is $STATUS. Please wait..."
            return 1
        fi
    else
        echo "❌ Instance not found or access denied"
        return 1
    fi
}

# ฟังก์ชันเปิด instance
start_instance() {
    echo "🔄 Starting instance..."
    aws sagemaker start-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        echo "✅ Start command sent. Waiting for instance..."
        wait_for_service
    else
        echo "❌ Failed to start instance"
    fi
}

# ฟังก์ชันปิด instance
stop_instance() {
    echo "⏹️  Stopping instance..."
    aws sagemaker stop-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        echo "✅ Stop command sent"
    else
        echo "❌ Failed to stop instance"
    fi
}

# ฟังก์ชันรอให้ instance เป็น InService
wait_for_service() {
    echo "⏳ Waiting for instance to be InService..."
    
    aws sagemaker wait notebook-instance-in-service \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        echo "✅ Instance is now InService!"
        check_instance_status
    else
        echo "❌ Timeout waiting for instance"
    fi
}

# ฟังก์ชันตรวจสอบ S3
check_s3_data() {
    echo "🔍 Checking S3 training data..."
    
    # ตรวจสอบข้อมูลใน S3
    OBJECT_COUNT=$(aws s3 ls s3://$S3_BUCKET/recognition-data/ --recursive --region $REGION | wc -l)
    
    if [ $OBJECT_COUNT -gt 0 ]; then
        echo "✅ Found $OBJECT_COUNT objects in S3"
        echo "📁 Data location: s3://$S3_BUCKET/recognition-data/"
        
        # ตรวจสอบไฟล์สำคัญ
        echo ""
        echo "🔍 Checking important files:"
        
        important_files=(
            "recognition-data/annotations/train_annotation.txt"
            "recognition-data/annotations/val_annotation.txt"
            "recognition-data/metadata/character_dict.txt"
            "recognition-data/metadata/dataset_info.json"
        )
        
        for file in "${important_files[@]}"; do
            if aws s3 ls s3://$S3_BUCKET/$file --region $REGION >/dev/null 2>&1; then
                echo "  ✅ $file"
            else
                echo "  ❌ $file - missing"
            fi
        done
    else
        echo "⚠️  No training data found in S3"
        echo "💡 Please upload data first using: aws s3 sync data_preparation/output/recognition_dataset/ s3://$S3_BUCKET/recognition-data/"
    fi
}

# ฟังก์ชันแสดงการใช้งาน
show_usage() {
    echo "📋 Usage:"
    echo "  $0 status    - Check instance status"
    echo "  $0 start     - Start instance"
    echo "  $0 stop      - Stop instance"
    echo "  $0 wait      - Wait for instance to be ready"
    echo "  $0 s3        - Check S3 training data"
    echo "  $0 url       - Get Jupyter URL"
    echo "  $0 all       - Check everything"
}

# ฟังก์ชันดึง URL
get_jupyter_url() {
    URL=$(aws sagemaker describe-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION" \
        --query 'Url' \
        --output text 2>/dev/null)
    
    if [ $? -eq 0 ] && [ "$URL" != "None" ]; then
        echo "🔗 Jupyter URL: https://$URL"
        echo ""
        echo "💡 Click the URL above to open Jupyter notebook"
    else
        echo "❌ Cannot get URL. Instance may not be running."
    fi
}

# ฟังก์ชันตรวจสอบทุกอย่าง
check_all() {
    echo "🔍 Complete System Check"
    echo "========================"
    
    # 1. ตรวจสอบ AWS credentials
    echo "1️⃣ Checking AWS credentials..."
    if aws sts get-caller-identity --region $REGION >/dev/null 2>&1; then
        ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)
        echo "✅ AWS credentials valid (Account: $ACCOUNT)"
    else
        echo "❌ AWS credentials invalid"
        return 1
    fi
    
    echo ""
    
    # 2. ตรวจสอบ instance
    echo "2️⃣ Checking SageMaker instance..."
    check_instance_status
    
    echo ""
    
    # 3. ตรวจสอบ S3
    echo "3️⃣ Checking S3 data..."
    check_s3_data
    
    echo ""
    echo "🎯 System check completed!"
}

# Main script logic
case "$1" in
    "status")
        check_instance_status
        ;;
    "start")
        start_instance
        ;;
    "stop")
        stop_instance
        ;;
    "wait")
        wait_for_service
        ;;
    "s3")
        check_s3_data
        ;;
    "url")
        get_jupyter_url
        ;;
    "all")
        check_all
        ;;
    *)
        show_usage
        ;;
esac
