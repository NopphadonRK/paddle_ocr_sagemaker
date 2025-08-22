#!/bin/bash
# Training Progress Monitor
# สำหรับติดตามความคืบหน้าการเทรนโมเดล

# ข้อมูลการตั้งค่า
S3_BUCKET="sagemaker-ocr-train-bucket"
REGION="ap-southeast-1"
INSTANCE_NAME="paddle-ocr-training"

echo "📊 PaddleOCR Training Monitor"
echo "============================="

# ฟังก์ชันตรวจสอบ training logs ใน S3
check_training_logs() {
    echo "📄 Checking training logs..."
    
    # หา training runs ล่าสุด
    RECENT_RUNS=$(aws s3 ls s3://$S3_BUCKET/training-results/ --region $REGION | tail -5)
    
    if [ -n "$RECENT_RUNS" ]; then
        echo "✅ Recent training runs:"
        echo "$RECENT_RUNS"
        echo ""
        
        # หา run ล่าสุด
        LATEST_RUN=$(aws s3 ls s3://$S3_BUCKET/training-results/ --region $REGION | tail -1 | awk '{print $2}')
        
        if [ -n "$LATEST_RUN" ]; then
            echo "🎯 Latest run: $LATEST_RUN"
            
            # ตรวจสอบโมเดลที่เทรนแล้ว
            echo "📦 Checking trained models..."
            aws s3 ls s3://$S3_BUCKET/training-results/${LATEST_RUN}models/ --region $REGION --recursive
            
            echo ""
            
            # ตรวจสอบ logs
            echo "📋 Checking logs..."
            aws s3 ls s3://$S3_BUCKET/training-results/${LATEST_RUN}logs/ --region $REGION --recursive
        fi
    else
        echo "⚠️  No training results found in S3"
        echo "💡 Training may still be in progress or not started yet"
    fi
}

# ฟังก์ชันตรวจสอบ instance status
check_instance_activity() {
    echo "🔍 Checking SageMaker instance activity..."
    
    STATUS=$(aws sagemaker describe-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION" \
        --query 'NotebookInstanceStatus' \
        --output text 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "📊 Instance Status: $STATUS"
        
        if [ "$STATUS" = "InService" ]; then
            # ดึงข้อมูลเพิ่มเติม
            INSTANCE_TYPE=$(aws sagemaker describe-notebook-instance \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION" \
                --query 'InstanceType' \
                --output text)
            
            CREATION_TIME=$(aws sagemaker describe-notebook-instance \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION" \
                --query 'CreationTime' \
                --output text)
            
            echo "💻 Instance Type: $INSTANCE_TYPE"
            echo "⏰ Created: $CREATION_TIME"
            echo "✅ Instance is active and ready for training"
        fi
    else
        echo "❌ Cannot access instance information"
    fi
}

# ฟังก์ชันดาวน์โหลดและแสดง training summary
show_latest_summary() {
    echo "📈 Latest Training Summary"
    echo "=========================="
    
    # หา summary file ล่าสุด
    LATEST_SUMMARY=$(aws s3 ls s3://$S3_BUCKET/training-results/ --recursive --region $REGION | grep "training_summary.json" | tail -1)
    
    if [ -n "$LATEST_SUMMARY" ]; then
        SUMMARY_KEY=$(echo "$LATEST_SUMMARY" | awk '{print $4}')
        echo "📄 Found summary: $SUMMARY_KEY"
        
        # ดาวน์โหลดและแสดง
        TEMP_FILE="/tmp/training_summary.json"
        aws s3 cp s3://$S3_BUCKET/$SUMMARY_KEY $TEMP_FILE --region $REGION --quiet
        
        if [ -f "$TEMP_FILE" ]; then
            echo ""
            echo "🎯 Training Information:"
            
            # แสดงข้อมูลสำคัญ
            if command -v jq >/dev/null 2>&1; then
                # ใช้ jq ถ้ามี
                echo "  📅 Timestamp: $(jq -r '.training_info.timestamp' $TEMP_FILE)"
                echo "  ⏱️  Duration: $(jq -r '.training_info.duration' $TEMP_FILE)"
                echo "  🤖 Algorithm: $(jq -r '.training_info.algorithm' $TEMP_FILE)"
                echo "  🏗️  Backbone: $(jq -r '.training_info.backbone' $TEMP_FILE)"
                echo "  🔄 Epochs: $(jq -r '.training_info.epochs' $TEMP_FILE)"
                echo "  📊 Batch Size: $(jq -r '.training_info.batch_size' $TEMP_FILE)"
                echo "  📈 Learning Rate: $(jq -r '.training_info.learning_rate' $TEMP_FILE)"
                echo ""
                echo "☁️  Results Location:"
                echo "  📦 Models: $(jq -r '.s3_locations.models' $TEMP_FILE)"
                echo "  ⚙️  Config: $(jq -r '.s3_locations.config' $TEMP_FILE)"
            else
                # แสดงแบบ raw ถ้าไม่มี jq
                echo "📄 Raw summary (install 'jq' for better formatting):"
                cat $TEMP_FILE | head -20
            fi
            
            rm -f $TEMP_FILE
        else
            echo "❌ Failed to download summary file"
        fi
    else
        echo "⚠️  No training summary found"
        echo "💡 Training may not be completed yet"
    fi
}

# ฟังก์ชันแสดงการใช้งาน S3
show_s3_usage() {
    echo "💾 S3 Storage Usage"
    echo "==================="
    
    # ตรวจสอบขนาดข้อมูลใน S3
    echo "📁 Bucket contents:"
    
    folders=("recognition-data" "training-results" "models" "checkpoints" "logs")
    
    for folder in "${folders[@]}"; do
        SIZE=$(aws s3 ls s3://$S3_BUCKET/$folder/ --recursive --summarize --region $REGION 2>/dev/null | grep "Total Size:" | awk '{print $3}')
        COUNT=$(aws s3 ls s3://$S3_BUCKET/$folder/ --recursive --summarize --region $REGION 2>/dev/null | grep "Total Objects:" | awk '{print $3}')
        
        if [ -n "$SIZE" ] && [ "$SIZE" != "0" ]; then
            SIZE_MB=$(echo "scale=2; $SIZE / 1024 / 1024" | bc -l 2>/dev/null || echo "unknown")
            echo "  📂 $folder/: $COUNT files, ${SIZE_MB}MB"
        else
            echo "  📂 $folder/: empty"
        fi
    done
}

# ฟังก์ชันแสดงคำแนะนำ
show_tips() {
    echo ""
    echo "💡 Training Tips & Commands"
    echo "=========================="
    echo ""
    echo "🎯 To start/access training:"
    echo "  ./quick_start_sagemaker.sh"
    echo ""
    echo "🔍 To check everything:"
    echo "  ./sagemaker_status.sh all"
    echo ""
    echo "⏹️  To stop instance (save costs):"
    echo "  ./sagemaker_status.sh stop"
    echo ""
    echo "📥 To download trained models:"
    echo "  aws s3 sync s3://$S3_BUCKET/training-results/run_TIMESTAMP/models/ ./downloaded_models/"
    echo ""
    echo "🧪 To test downloaded model:"
    echo "  cd PaddleOCR"
    echo "  python tools/infer_rec.py -c config.yml -o Global.checkpoints=./model_path"
}

# Main script logic
case "$1" in
    "logs")
        check_training_logs
        ;;
    "instance")
        check_instance_activity
        ;;
    "summary")
        show_latest_summary
        ;;
    "s3")
        show_s3_usage
        ;;
    "tips")
        show_tips
        ;;
    *)
        echo "🔍 Full Training Monitor Report"
        echo "==============================="
        echo ""
        
        check_instance_activity
        echo ""
        check_training_logs
        echo ""
        show_latest_summary
        echo ""
        show_s3_usage
        
        show_tips
        ;;
esac
