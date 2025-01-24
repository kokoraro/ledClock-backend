#!/bin/bash

# This script runs as a cron job every 5 minutes
# It pulls the latest code from the git repository and restarts the related services

# Store the current commit hash
old_hash=$(git -C ~/LED_Clock rev-parse HEAD)

# Pull the latest code from the git repository
git pull -C ~/LED_Clock

# Store the new commit hash
new_hash=$(git -C ~/LED_Clock rev-parse HEAD)

# If there were changes, restart the services
if [ "$old_hash" != "$new_hash" ]; then
    sudo systemctl restart led_local.service
    sudo systemctl restart led_server.service
fi