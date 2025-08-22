#!/bin/bash
# Load AWS credentials from aws-config.json
# ใช้สำหรับโหลด AWS credentials ก่อนรัน scripts อื่นๆ

CONFIG_FILE="aws-config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ $CONFIG_FILE not found!"
    echo "💡 Please make sure aws-config.json exists in the current directory"
    exit 1
fi

# ตรวจสอบว่ามี jq หรือไม่
if ! command -v jq >/dev/null 2>&1; then
    echo "📦 Installing jq for JSON parsing..."
    # สำหรับ macOS
    if command -v brew >/dev/null 2>&1; then
        brew install jq
    else
        echo "❌ Please install jq: brew install jq"
        exit 1
    fi
fi

# โหลด credentials จาก JSON
echo "🔐 Loading AWS credentials from $CONFIG_FILE..."

AWS_ACCESS_KEY_ID=$(jq -r '.credentials.aws_access_key_id' $CONFIG_FILE)
AWS_SECRET_ACCESS_KEY=$(jq -r '.credentials.aws_secret_access_key' $CONFIG_FILE)
AWS_SESSION_TOKEN=$(jq -r '.credentials.aws_session_token' $CONFIG_FILE)
AWS_DEFAULT_REGION=$(jq -r '.aws_settings.region' $CONFIG_FILE)

# ตรวจสอบว่าได้ข้อมูลครบหรือไม่
if [ "$AWS_ACCESS_KEY_ID" = "null" ] || [ "$AWS_SECRET_ACCESS_KEY" = "null" ]; then
    echo "❌ Invalid credentials in $CONFIG_FILE"
    exit 1
fi

# Export environment variables
export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
export AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN"
export AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION"

echo "✅ AWS credentials loaded successfully"
echo "🌍 Region: $AWS_DEFAULT_REGION"

# ทดสอบ credentials
echo "🔍 Testing AWS connection..."
if aws sts get-caller-identity >/dev/null 2>&1; then
    ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)
    echo "✅ Connected to AWS Account: $ACCOUNT"
else
    echo "❌ AWS connection failed"
    echo "💡 Please check your credentials in $CONFIG_FILE"
    exit 1
fi

# รันคำสั่งที่ส่งมาเป็น argument
if [ $# -gt 0 ]; then
    echo ""
    echo "🚀 Running: $@"
    echo "===================="
    exec "$@"
fi
