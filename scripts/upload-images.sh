#!/bin/bash

# Script to run the Firebase image upload script

echo "Setting up Firebase Storage for vehicle images..."

# Check if Firebase Storage is enabled
echo "Enabling Firebase Storage if not already enabled..."
firebase --project=findmycar-347ec deploy --only storage

# Run the image upload script
echo "Uploading vehicle images to Firebase Storage..."
node scripts/upload-demo-images.js

echo "Image upload process completed!"
