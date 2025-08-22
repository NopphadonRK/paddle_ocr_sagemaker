#!/bin/bash
# Quick SageMaker Training Launcher
# สำหรับเข้าถึง Jupyter Notebook บน SageMaker อย่างรวดเร็ว

# ข้อมูลการตั้งค่า
INSTANCE_NAME="paddle-ocr-training"
REGION="ap-southeast-1"

echo "🚀 Quick SageMaker Access"
echo "========================="

# ตรวจสอบสถานะ instance
echo "🔍 Checking instance status..."

STATUS=$(aws sagemaker describe-notebook-instance \
    --notebook-instance-name "$INSTANCE_NAME" \
    --region "$REGION" \
    --query 'NotebookInstanceStatus' \
    --output text 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ Cannot access SageMaker instance"
    echo "💡 Please check your AWS credentials and permissions"
    exit 1
fi

echo "📊 Instance Status: $STATUS"

case "$STATUS" in
    "InService")
        echo "✅ Instance is ready!"
        
        # ดึง Jupyter URL
        URL=$(aws sagemaker describe-notebook-instance \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION" \
            --query 'Url' \
            --output text)
        
        echo ""
        echo "🎯 Ready to start training!"
        echo "🔗 Jupyter URL: https://$URL"
        echo ""
        echo "📋 Next Steps:"
        echo "1. Click the URL above"
        echo "2. Open 'paddle_ocr_sagemaker_training.ipynb'"
        echo "3. Run cells sequentially starting from Cell 1"
        echo ""
        echo "💡 Pro tip: Save your work frequently!"
        
        # เปิด URL ใน browser (macOS)
        if command -v open >/dev/null 2>&1; then
            echo "🌐 Opening in browser..."
            open "https://$URL"
        fi
        ;;
        
    "Stopped")
        echo "⚠️  Instance is stopped. Starting now..."
        
        aws sagemaker start-notebook-instance \
            --notebook-instance-name "$INSTANCE_NAME" \
            --region "$REGION"
        
        if [ $? -eq 0 ]; then
            echo "✅ Start command sent"
            echo "⏳ Waiting for instance to be ready (this may take 2-3 minutes)..."
            
            # รอให้ instance เป็น InService
            aws sagemaker wait notebook-instance-in-service \
                --notebook-instance-name "$INSTANCE_NAME" \
                --region "$REGION"
            
            if [ $? -eq 0 ]; then
                echo "✅ Instance is now ready!"
                
                # ดึง URL และเปิด
                URL=$(aws sagemaker describe-notebook-instance \
                    --notebook-instance-name "$INSTANCE_NAME" \
                    --region "$REGION" \
                    --query 'Url' \
                    --output text)
                
                echo "🔗 Jupyter URL: https://$URL"
                
                if command -v open >/dev/null 2>&1; then
                    echo "🌐 Opening in browser..."
                    open "https://$URL"
                fi
            else
                echo "❌ Timeout waiting for instance to start"
                echo "💡 Please try again in a few minutes"
            fi
        else
            echo "❌ Failed to start instance"
        fi
        ;;
        
    "Pending"|"Starting")
        echo "⏳ Instance is starting up..."
        echo "💡 Please wait a few minutes and try again"
        ;;
        
    "Stopping")
        echo "⚠️  Instance is shutting down"
        echo "💡 Please wait for it to stop, then try again"
        ;;
        
    *)
        echo "⚠️  Instance status: $STATUS"
        echo "💡 Please check AWS Console for more details"
        ;;
esac

echo ""
echo "🛠️  Other useful commands:"
echo "  ./sagemaker_status.sh all    - Full system check"
echo "  ./sagemaker_status.sh stop   - Stop instance (save costs)"
echo "  ./training_monitor.sh        - Monitor training progress"
