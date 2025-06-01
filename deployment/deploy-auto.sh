#!/bin/bash

# 自动部署脚本，自动确认部署

cd /home/ec2-user/hgy/Paperal/deployment

# 使用expect自动回答提示
expect << EOF
spawn ./deploy-paperal.sh --key-pair test --db-password Paperal123! --env test --stack-name paperal-test
expect "Do you want to continue? (y/n)"
send "y\r"
expect eof
EOF
