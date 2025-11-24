#!/bin/bash

# Create output directory with proper permissions
mkdir -p dastardly-output
chmod 777 dastardly-output

# Run docker-compose
docker-compose up

# Show the report location
echo ""
echo "DAST scan complete!"
echo "Report location: ./dastardly-output/dastardly-report.xml"
