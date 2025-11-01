#!/bin/bash
# Script to restart Django container
docker-compose -f pedendencies/docker-compose.yml restart django
echo "Django container restarted successfully!"

