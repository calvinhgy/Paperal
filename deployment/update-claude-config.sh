#!/bin/bash

# 更新EC2实例上的.env文件，添加Claude API配置

# 获取EC2实例ID
INSTANCE_ID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=test-paperal-backend" --query "Reservations[0].Instances[0].InstanceId" --output text --region us-east-1)

echo "Instance ID: $INSTANCE_ID"

# 使用SSM发送命令更新.env文件
aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters '{"commands":["echo \"CLAUDE_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0\" >> /home/ec2-user/Paperal/src/backend/.env", "systemctl restart paperal.service"]}' \
    --region us-east-1
