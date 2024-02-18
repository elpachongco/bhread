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
  rsync -avz -e "ssh -o StrictHostKeyChecking=no" --progress . $USERNAME@$TARGET_ADDRESS:~/bhread/
  ssh -t $USERNAME@$TARGET_ADDRESS "cd ~/bhread/; sudo docker compose --profile prod down; sudo docker compose --profile prod up --build -d; sudo docker compose --profile prod logs -n 25 -f"
  git checkout -
fi
