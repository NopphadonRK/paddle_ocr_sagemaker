#!/bin/bash
# ======================================
# Quick SageMaker Training Launcher
# เปิด Jupyter และเตรียมเริ่ม Training
# ======================================

set -e

# Configuration (from your setup)
INSTANCE_NAME="paddle-ocr-training"
S3_BUCKET="sagemaker-ocr-train-bucket"
REGION="ap-southeast-1"
NOTEBOOK_FILE="paddle_ocr_sagemaker_training.ipynb"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick SageMaker Training Launcher${NC}"
echo "===================================="

# 1. Check instance status
echo "🔍 Checking SageMaker instance..."
STATUS=$(aws sagemaker describe-notebook-instance \
    --notebook-instance-name "$INSTANCE_NAME" \
    --region "$REGION" \
    --query 'NotebookInstanceStatus' \
    --output text)

if [ "$STATUS" != "InService" ]; then
    echo -e "${YELLOW}⚠️  Instance is $STATUS. Please start it first.${NC}"
    echo "Run: ./sagemaker_management.sh start"
    exit 1
fi

echo -e "${GREEN}✅ Instance is ready!${NC}"

# 2. Check S3 data
echo ""
echo "🔍 Checking S3 training data..."
aws s3 ls "s3://$S3_BUCKET/recognition-data/annotations/train_annotation.txt" --region "$REGION" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Training data is ready in S3${NC}"
else
    echo -e "${YELLOW}⚠️  Training data not found in S3${NC}"
    echo "Please check: s3://$S3_BUCKET/recognition-data/"
fi

# 3. Get Jupyter URL
echo ""
echo "🔗 Getting Jupyter URL..."
URL=$(aws sagemaker describe-notebook-instance \
    --notebook-instance-name "$INSTANCE_NAME" \
    --region "$REGION" \
    --query 'Url' \
    --output text)

FULL_URL="https://$URL"

# 4. Display instructions
echo ""
echo -e "${GREEN}🎯 Ready to Start Training!${NC}"
echo "=========================="
echo ""
echo "📋 Training Instructions:"
echo "1. 🔗 Jupyter URL: $FULL_URL"
echo "2. 📝 Open notebook: $NOTEBOOK_FILE"
echo "3. 🏃 Run cells 1-8 sequentially"
echo ""
echo "📊 Expected Training Flow:"
echo "   Cell 1: Environment setup (2-3 min)"
echo "   Cell 2: AWS configuration (30 sec)"
echo "   Cell 3: PaddleOCR setup (1-2 min)"
echo "   Cell 4: Download data (2-5 min)"
echo "   Cell 5: Create config (30 sec)"
echo "   Cell 6: Start training (30-60 min)"
echo "   Cell 7: Test model (2-3 min)"
echo "   Cell 8: Upload results (2-5 min)"
echo ""
echo "💰 Instance Cost: ~$1.00/hour (ml.g4dn.xlarge)"
echo "⏱️  Estimated total time: 45-75 minutes"
echo ""

# 5. Open browser
read -p "🌐 Open Jupyter in browser now? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "📋 Manual access: $FULL_URL"
else
    echo "🌐 Opening browser..."
    open "$FULL_URL" 2>/dev/null || {
        echo "Cannot open browser automatically."
        echo "Please open: $FULL_URL"
    }
fi

echo ""
echo -e "${BLUE}📊 Monitoring Commands:${NC}"
echo "  Monitor progress:    ./sagemaker_management.sh monitor"
echo "  Check status:        ./sagemaker_management.sh status"
echo "  Download results:    ./sagemaker_management.sh download"
echo "  Stop instance:       ./sagemaker_management.sh stop"

echo ""
echo -e "${GREEN}🎉 Happy Training!${NC}"
