#!/bin/bash
# Quick Setup Script for AWS Training
# รันสคริปต์นี้เพื่อเตรียมพร้อมสำหรับการเทรน

echo "🚀 PaddleOCR AWS Training Setup"
echo "================================"

# 1. Load environment variables
echo "📋 Loading AWS credentials..."
if [ -f ".env" ]; then
    source .env
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found!"
    exit 1
fi

# 2. Test AWS connection
echo ""
echo "🔍 Testing AWS connection..."
python test_aws_connection.py

if [ $? -eq 0 ]; then
    echo "✅ AWS connection successful"
else
    echo "❌ AWS connection failed"
    exit 1
fi

# 3. Install additional dependencies if needed
echo ""
echo "📦 Checking dependencies..."
source venv/bin/activate
pip install boto3 sagemaker --quiet

# 4. Upload data to S3
echo ""
echo "📤 Ready to upload data to S3..."
echo "Run: cd data_preparation && python scripts/upload_to_s3.py"
echo ""

# 5. Start training
echo "🎯 Ready to start training!"
echo "Run: jupyter notebook paddle_ocr_recognition_training.ipynb"
echo ""

echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. cd data_preparation"
echo "2. python scripts/upload_to_s3.py"
echo "3. jupyter notebook ../paddle_ocr_recognition_training.ipynb"
