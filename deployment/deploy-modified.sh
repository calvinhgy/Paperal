#!/bin/bash

# 修改后的部署脚本，移除交互式确认

# 复制原始脚本的内容
cp /home/ec2-user/hgy/Paperal/deployment/deploy-paperal.sh /home/ec2-user/hgy/Paperal/deployment/deploy-paperal-temp.sh

# 移除交互式确认部分
sed -i '/read -p "Do you want to continue? (y\/n)" -n 1 -r/,/fi/d' /home/ec2-user/hgy/Paperal/deployment/deploy-paperal-temp.sh

# 执行修改后的脚本
cd /home/ec2-user/hgy/Paperal/deployment
chmod +x deploy-paperal-temp.sh
./deploy-paperal-temp.sh --key-pair test --db-password Paperal123 --env test --stack-name paperal-test

# 清理临时文件
rm -f /home/ec2-user/hgy/Paperal/deployment/deploy-paperal-temp.sh
