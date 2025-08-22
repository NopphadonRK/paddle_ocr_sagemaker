# AWS Configuration Guide

## 🔐 Security Notice
**⚠️ IMPORTANT**: Files `aws-config.json` และ `.env` contain sensitive AWS credentials และถูกเพิ่มใน `.gitignore` แล้ว

**DO NOT commit these files to git!**

## 📋 Configuration Files

### 1. `aws-config.json`
Complete AWS configuration including:
- AWS credentials (temporary session token)
- S3 bucket settings
- SageMaker configuration
- Training paths

### 2. `.env`
Environment variables for easy sourcing:
```bash
source .env
```

## 🚀 Usage

### Load Environment Variables
```bash
# Method 1: Source .env file
source .env

# Method 2: Load from aws-config.json (requires jq)
export AWS_ACCESS_KEY_ID=$(cat aws-config.json | jq -r '.credentials.aws_access_key_id')
export AWS_SECRET_ACCESS_KEY=$(cat aws-config.json | jq -r '.credentials.aws_secret_access_key')
export AWS_SESSION_TOKEN=$(cat aws-config.json | jq -r '.credentials.aws_session_token')
export AWS_DEFAULT_REGION=$(cat aws-config.json | jq -r '.aws_settings.region')
```

### Test AWS Connection
```bash
# Load environment
source .env

# Test AWS access
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://sagemaker-ocr-train-bucket
```

## 📝 Current Configuration

- **Bucket**: `sagemaker-ocr-train-bucket`
- **Region**: `ap-southeast-1`
- **Instance**: `ml.g4dn.xlarge`
- **Profile**: `484468818942_AIEngineer`

## ⏰ Session Token Expiry

**Session tokens expire periodically** (usually 1-12 hours)

If you get authentication errors:
1. Generate new credentials from AWS Console
2. Update `aws-config.json` and `.env`
3. Re-source the environment: `source .env`

## 🔄 Next Steps

1. **Test connection**: `source .env && aws sts get-caller-identity`
2. **Create S3 bucket**: See setup scripts
3. **Upload data**: Run data preparation scripts
4. **Start training**: Open Jupyter notebook

## 🛡️ Security Best Practices

- ✅ Files are in `.gitignore`
- ✅ Use session tokens (temporary)
- ✅ Rotate credentials regularly
- ❌ Never commit credentials to git
- ❌ Never share credentials in plain text
