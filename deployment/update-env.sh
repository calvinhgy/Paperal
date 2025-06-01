#!/bin/bash

# 这个脚本用于更新EC2实例上的.env文件，添加Claude API配置

# 获取EC2实例ID
INSTANCE_ID=$(aws cloudformation describe-stacks --stack-name paperal-test --query "Stacks[0].Outputs[?OutputKey=='BackendURL'].OutputValue" --output text | cut -d'/' -f3 | cut -d':' -f1 | cut -d'.' -f1)

# 使用SSM发送命令更新.env文件
aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters commands=["
        echo 'CLAUDE_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0' >> /home/ec2-user/Paperal/src/backend/.env
        systemctl restart paperal.service
    "] \
    --output text
