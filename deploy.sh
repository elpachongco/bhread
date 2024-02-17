#!/bin/bash

# Script for deployment. Assumes you have SSH properly set up
USERNAME=`cat vps_username.txt`
TARGET_ADDRESS=`cat vps_ip.txt`
DEPLOY_BRANCH="main"

echo "Deploying branch -- ${DEPLOY_BRANCH} --> to ${USERNAME}@${TARGET_ADDRESS}"
read -p "Are you sure? (y/n)" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  git checkout $DEPLOY_BRANCH
  # rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress . $USERNAME@$TARGET_ADDRESS:~/bhread/
  ssh -t $USERNAME@$TARGET_ADDRESS "cd ~/bhread/; sudo docker compose build web_prod djangoq_prod; sudo docker compose up --no-deps -d web_prod djangoq_prod"
  git checkout -
fi
