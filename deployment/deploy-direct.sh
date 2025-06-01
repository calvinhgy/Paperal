#!/bin/bash

# 直接部署脚本，跳过原始脚本的所有交互

# 设置变量
STACK_NAME="paperal-test"
REGION="us-east-1"
ENV="test"
KEY_PAIR_NAME="test"
DB_PASSWORD="Paperal123"

echo "Starting direct deployment of Paperal..."
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Environment: $ENV"
echo "Key Pair: $KEY_PAIR_NAME"

# 直接调用AWS CLI创建CloudFormation堆栈
echo "Deploying CloudFormation stack..."
aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file:///home/ec2-user/hgy/Paperal/deployment/paperal-cloudformation.yaml \
    --parameters \
        ParameterKey=KeyName,ParameterValue=$KEY_PAIR_NAME \
        ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD \
        ParameterKey=EnvironmentName,ParameterValue=$ENV \
    --capabilities CAPABILITY_IAM \
    --region $REGION

echo "CloudFormation stack creation initiated."
echo "Waiting for stack creation to complete. This may take 15-20 minutes..."

# 等待堆栈创建完成
aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "Stack creation completed successfully!"
    
    # 获取输出
    echo "Retrieving deployment information..."
    BACKEND_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='BackendURL'].OutputValue" --output text)
    FRONTEND_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='FrontendURL'].OutputValue" --output text)
    FRONTEND_BUCKET=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" --output text)
    
    echo "Deployment completed successfully!"
    echo "Backend URL: $BACKEND_URL"
    echo "Frontend URL: $FRONTEND_URL"
    
    # 部署前端的说明
    echo "Next steps:"
    echo "1. Build the frontend application:"
    echo "   cd Paperal/src/frontend"
    echo "   npm install"
    echo "   npm run build"
    echo ""
    echo "2. Upload the frontend build to S3:"
    echo "   aws s3 sync build/ s3://$FRONTEND_BUCKET"
    echo ""
    echo "3. Your application will be available at: $FRONTEND_URL"
    
    # 更新EC2实例上的.env文件，添加Claude API配置
    echo "Updating .env file with Claude API configuration..."
    INSTANCE_ID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=${ENV}-paperal-backend" --query "Reservations[0].Instances[0].InstanceId" --output text --region $REGION)
    
    # 等待EC2实例状态检查通过
    echo "Waiting for EC2 instance to be ready..."
    aws ec2 wait instance-status-ok --instance-ids $INSTANCE_ID --region $REGION
    
    # 使用SSM发送命令更新.env文件
    aws ssm send-command \
        --instance-ids "$INSTANCE_ID" \
        --document-name "AWS-RunShellScript" \
        --parameters commands=["
            echo 'CLAUDE_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0' >> /home/ec2-user/Paperal/src/backend/.env
            systemctl restart paperal.service
        "] \
        --region $REGION
    
    echo "Claude API configuration updated."
else
    echo "Stack creation failed. Check the AWS CloudFormation console for details."
    exit 1
fi
