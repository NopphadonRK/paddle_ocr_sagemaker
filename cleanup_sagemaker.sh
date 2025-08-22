#!/bin/bash
# SageMaker Cleanup Script
# สำหรับจัดการและล้างข้อมูลเมื่อเสร็จสิ้นการใช้งาน

# ข้อมูลการตั้งค่า
INSTANCE_NAME="paddle-ocr-training"
REGION="ap-southeast-1"
S3_BUCKET="sagemaker-ocr-train-bucket"

echo "🧹 SageMaker Cleanup & Cost Management"
echo "======================================"

# ฟังก์ชันแสดงต้นทุนปัจจุบัน
show_current_costs() {
    echo "💰 Current Cost Information"
    echo "=========================="
    
    # ตรวจสอบสถานะ instance
    STATUS=$(aws sagemaker describe-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION" \
        --query 'NotebookInstanceStatus' \
        --output text 2>/dev/null)
    
    INSTANCE_TYPE=$(aws sagemaker describe-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION" \
        --query 'InstanceType' \
        --output text 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "📊 Instance: $INSTANCE_NAME ($INSTANCE_TYPE)"
        echo "📈 Status: $STATUS"
        
        # คำนวณต้นทุนประมาณ (ml.g4dn.xlarge ≈ $0.736/hour)
        if [ "$INSTANCE_TYPE" = "ml.g4dn.xlarge" ]; then
            echo "💵 Estimated cost: ~$0.736/hour when running"
            
            if [ "$STATUS" = "InService" ]; then
                echo "⚠️  Instance is currently RUNNING and incurring charges"
                
                # คำนวณเวลาที่รัน
                CREATION_TIME=$(aws sagemaker describe-notebook-instance \
                    --notebook-instance-name "$INSTANCE_NAME" \
                    --region "$REGION" \
                    --query 'CreationTime' \
                    --output text)
                
                echo "⏰ Created: $CREATION_TIME"
            else
                echo "✅ Instance is $STATUS - no compute charges"
            fi
        fi
    fi
    
    # ตรวจสอบขนาด S3
    echo ""
    echo "💾 S3 Storage Usage:"
    
    TOTAL_SIZE=$(aws s3 ls s3://$S3_BUCKET --recursive --summarize --region $REGION 2>/dev/null | grep "Total Size:" | awk '{print $3}')
    TOTAL_OBJECTS=$(aws s3 ls s3://$S3_BUCKET --recursive --summarize --region $REGION 2>/dev/null | grep "Total Objects:" | awk '{print $3}')
    
    if [ -n "$TOTAL_SIZE" ] && [ "$TOTAL_SIZE" != "0" ]; then
        SIZE_GB=$(echo "scale=3; $TOTAL_SIZE / 1024 / 1024 / 1024" | bc -l 2>/dev/null || echo "unknown")
        STORAGE_COST=$(echo "scale=4; $SIZE_GB * 0.023" | bc -l 2>/dev/null || echo "unknown")
        echo "📦 Total: $TOTAL_OBJECTS objects, ${SIZE_GB}GB"
        echo "💰 Estimated S3 cost: ~$${STORAGE_COST}/month"
    else
        echo "📦 S3 bucket is empty"
    fi
}

# ฟังก์ชันหยุด instance
stop_instance() {
    echo "⏹️  Stopping SageMaker Instance"
    echo "============================="
    
    STATUS=$(aws sagemaker describe-notebook-instance \
        --notebook-instance-name "$INSTANCE_NAME" \
        --region "$REGION" \
        --query 'NotebookInstanceStatus' \
        --output text 2>/dev/null)
    
    if [ "$STATUS" = "InService" ]; then
        echo "⚠️  Stopping instance to save costs..."
        
        aws sagemaker stop-notebook-instance \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION"
        
        if [ $? -eq 0 ]; then
            echo "✅ Stop command sent successfully"
            echo "⏳ Instance will stop in 1-2 minutes"
            echo "💰 This will stop compute charges"
            echo ""
            echo "💡 To restart later: ./quick_start_sagemaker.sh"
        else
            echo "❌ Failed to stop instance"
        fi
    elif [ "$STATUS" = "Stopped" ]; then
        echo "✅ Instance is already stopped"
    else
        echo "⚠️  Instance status: $STATUS"
        echo "💡 Can only stop instances that are InService"
    fi
}

# ฟังก์ชันดาวน์โหลด results
download_results() {
    echo "📥 Download Training Results"
    echo "==========================="
    
    # สร้างโฟลเดอร์สำหรับดาวน์โหลด
    DOWNLOAD_DIR="./downloaded_results"
    mkdir -p "$DOWNLOAD_DIR"
    
    echo "📁 Download directory: $DOWNLOAD_DIR"
    
    # ดาวน์โหลด training results
    echo "📦 Downloading latest training results..."
    
    LATEST_RUN=$(aws s3 ls s3://$S3_BUCKET/training-results/ --region $REGION | tail -1 | awk '{print $2}')
    
    if [ -n "$LATEST_RUN" ]; then
        echo "🎯 Latest run: $LATEST_RUN"
        
        # ดาวน์โหลดโมเดล
        echo "📦 Downloading models..."
        aws s3 sync s3://$S3_BUCKET/training-results/${LATEST_RUN}models/ "$DOWNLOAD_DIR/models/" --region $REGION
        
        # ดาวน์โหลด config
        echo "⚙️  Downloading configuration..."
        aws s3 sync s3://$S3_BUCKET/training-results/${LATEST_RUN}config/ "$DOWNLOAD_DIR/config/" --region $REGION
        
        # ดาวน์โหลด summary
        echo "📄 Downloading summary..."
        aws s3 cp s3://$S3_BUCKET/training-results/${LATEST_RUN}training_summary.json "$DOWNLOAD_DIR/" --region $REGION
        
        echo ""
        echo "✅ Download completed!"
        echo "📁 Results saved in: $DOWNLOAD_DIR"
        echo ""
        echo "📋 Contents:"
        ls -la "$DOWNLOAD_DIR"
        
        if [ -d "$DOWNLOAD_DIR/models" ]; then
            echo ""
            echo "🤖 Model files:"
            ls -la "$DOWNLOAD_DIR/models/"
        fi
        
    else
        echo "❌ No training results found to download"
    fi
}

# ฟังก์ชันลบ instance
delete_instance() {
    echo "⚠️  DELETE SageMaker Instance"
    echo "============================"
    echo ""
    echo "🚨 WARNING: This will permanently delete the instance!"
    echo "📋 Before deleting, make sure you have:"
    echo "   ✅ Downloaded all important results"
    echo "   ✅ Saved any custom notebooks"
    echo "   ✅ Backed up any configurations"
    echo ""
    
    read -p "❓ Are you sure you want to DELETE the instance? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" = "yes" ]; then
        echo "🗑️  Deleting instance..."
        
        # หยุด instance ก่อน (ถ้าจำเป็น)
        STATUS=$(aws sagemaker describe-notebook-instance \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION" \
            --query 'NotebookInstanceStatus' \
            --output text 2>/dev/null)
        
        if [ "$STATUS" = "InService" ]; then
            echo "⏹️  Stopping instance first..."
            aws sagemaker stop-notebook-instance \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION"
            
            echo "⏳ Waiting for instance to stop..."
            aws sagemaker wait notebook-instance-stopped \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION"
        fi
        
        # ลบ instance
        aws sagemaker delete-notebook-instance \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION"
        
        if [ $? -eq 0 ]; then
            echo "✅ Delete command sent"
            echo "⏳ Instance will be deleted in a few minutes"
            echo "💰 All compute charges will stop"
        else
            echo "❌ Failed to delete instance"
        fi
    else
        echo "🚫 Delete cancelled"
    fi
}

# ฟังก์ชันล้าง S3 (อย่างระมัดระวัง)
clean_s3() {
    echo "🧹 S3 Storage Cleanup"
    echo "===================="
    echo ""
    echo "⚠️  Select what to clean:"
    echo ""
    echo "1. Temporary files only (safe)"
    echo "2. Old training results (keep latest 3)"
    echo "3. All training results (⚠️  DANGEROUS)"
    echo "4. Cancel"
    echo ""
    
    read -p "❓ Enter your choice (1-4): " CHOICE
    
    case $CHOICE in
        1)
            echo "🧹 Cleaning temporary files..."
            # ลบไฟล์ temporary และ cache
            aws s3 rm s3://$S3_BUCKET/temp/ --recursive --region $REGION 2>/dev/null || true
            aws s3 rm s3://$S3_BUCKET/cache/ --recursive --region $REGION 2>/dev/null || true
            echo "✅ Temporary files cleaned"
            ;;
        2)
            echo "📦 Cleaning old training results (keeping latest 3)..."
            # ดึงรายการ training results และลบของเก่า
            OLD_RUNS=$(aws s3 ls s3://$S3_BUCKET/training-results/ --region $REGION | head -n -3 | awk '{print $2}')
            
            if [ -n "$OLD_RUNS" ]; then
                for run in $OLD_RUNS; do
                    echo "🗑️  Removing old run: $run"
                    aws s3 rm s3://$S3_BUCKET/training-results/$run --recursive --region $REGION
                done
                echo "✅ Old training results cleaned"
            else
                echo "💡 No old results to clean"
            fi
            ;;
        3)
            echo "🚨 WARNING: This will delete ALL training results!"
            read -p "❓ Type 'DELETE ALL' to confirm: " CONFIRM
            
            if [ "$CONFIRM" = "DELETE ALL" ]; then
                echo "🗑️  Deleting all training results..."
                aws s3 rm s3://$S3_BUCKET/training-results/ --recursive --region $REGION
                aws s3 rm s3://$S3_BUCKET/models/ --recursive --region $REGION
                aws s3 rm s3://$S3_BUCKET/checkpoints/ --recursive --region $REGION
                aws s3 rm s3://$S3_BUCKET/logs/ --recursive --region $REGION
                echo "✅ All training data deleted"
            else
                echo "🚫 Cleanup cancelled"
            fi
            ;;
        *)
            echo "🚫 Cleanup cancelled"
            ;;
    esac
}

# ฟังก์ชันแสดงการใช้งาน
show_usage() {
    echo "📋 Cleanup Options:"
    echo "  $0 costs     - Show current costs"
    echo "  $0 stop      - Stop instance (save money)"
    echo "  $0 download  - Download training results"
    echo "  $0 delete    - Delete instance (permanent)"
    echo "  $0 s3        - Clean S3 storage"
    echo "  $0 all       - Show costs and stop instance"
}

# Main script logic
case "$1" in
    "costs")
        show_current_costs
        ;;
    "stop")
        stop_instance
        ;;
    "download")
        download_results
        ;;
    "delete")
        delete_instance
        ;;
    "s3")
        clean_s3
        ;;
    "all")
        show_current_costs
        echo ""
        stop_instance
        ;;
    *)
        show_usage
        ;;
esac
