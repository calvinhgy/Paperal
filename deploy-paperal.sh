#!/bin/bash

# Paperal AWS Deployment Script
# This script deploys the Paperal application to AWS using CloudFormation

set -e

# Configuration
STACK_NAME="paperal"
REGION="us-east-1"  # Change to your preferred region
ENV="dev"           # dev, staging, or prod
KEY_PAIR_NAME=""    # Your EC2 key pair name
DB_PASSWORD=""      # Password for PostgreSQL database

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS credentials are not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --region)
            REGION="$2"
            shift 2
            ;;
        --env)
            ENV="$2"
            shift 2
            ;;
        --key-pair)
            KEY_PAIR_NAME="$2"
            shift 2
            ;;
        --db-password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        --stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Validate inputs
if [ -z "$KEY_PAIR_NAME" ]; then
    echo -e "${RED}Error: EC2 key pair name is required.${NC}"
    echo "Usage: $0 --key-pair YOUR_KEY_PAIR_NAME --db-password YOUR_DB_PASSWORD [--region REGION] [--env ENV] [--stack-name STACK_NAME]"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}Error: Database password is required.${NC}"
    echo "Usage: $0 --key-pair YOUR_KEY_PAIR_NAME --db-password YOUR_DB_PASSWORD [--region REGION] [--env ENV] [--stack-name STACK_NAME]"
    exit 1
fi

# Confirm deployment
echo -e "${YELLOW}You are about to deploy Paperal to AWS with the following configuration:${NC}"
echo "  Stack Name: $STACK_NAME"
echo "  Region: $REGION"
echo "  Environment: $ENV"
echo "  Key Pair: $KEY_PAIR_NAME"
echo -e "${YELLOW}This will create multiple AWS resources and may incur charges to your AWS account.${NC}"
read -p "Do you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting deployment...${NC}"

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file://paperal-cloudformation.yaml \
    --parameters \
        ParameterKey=KeyName,ParameterValue=$KEY_PAIR_NAME \
        ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD \
        ParameterKey=EnvironmentName,ParameterValue=$ENV \
    --capabilities CAPABILITY_IAM \
    --region $REGION

echo -e "${GREEN}CloudFormation stack creation initiated.${NC}"
echo "Waiting for stack creation to complete. This may take 15-20 minutes..."

# Wait for stack creation to complete
aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME \
    --region $REGION

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Stack creation completed successfully!${NC}"
    
    # Get outputs
    echo "Retrieving deployment information..."
    BACKEND_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='BackendURL'].OutputValue" --output text)
    FRONTEND_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='FrontendURL'].OutputValue" --output text)
    FRONTEND_BUCKET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" --output text)
    
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo "Backend URL: $BACKEND_URL"
    echo "Frontend URL: $FRONTEND_URL"
    
    # Instructions for deploying the frontend
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Build the frontend application:"
    echo "   cd Paperal/src/frontend"
    echo "   npm install"
    echo "   npm run build"
    echo ""
    echo "2. Upload the frontend build to S3:"
    echo "   aws s3 sync build/ s3://$FRONTEND_BUCKET"
    echo ""
    echo "3. Your application will be available at: $FRONTEND_URL"
else
    echo -e "${RED}Stack creation failed. Check the AWS CloudFormation console for details.${NC}"
    exit 1
fi
