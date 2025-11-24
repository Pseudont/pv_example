#!/bin/bash

# Create output directory (no permission changes needed with user mapping in docker-compose)
mkdir -p dastardly-output

# Export user and group IDs for docker-compose to use proper permissions
export UID=$(id -u)
export GID=$(id -g)

# Run docker-compose
docker-compose up

# Show the report location
echo ""
echo "DAST scan complete!"
echo "Report location: ./dastardly-output/dastardly-report.xml"
