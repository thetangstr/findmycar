#!/bin/bash

# Create the images directory if it doesn't exist
mkdir -p /Users/edward/Desktop/Projects/Findmycar2/public/images/cars

# Download sports car images
curl -L "https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/porsche-911.jpg
curl -L "https://images.pexels.com/photos/8996680/pexels-photo-8996680.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/corvette.jpg
curl -L "https://images.pexels.com/photos/3752169/pexels-photo-3752169.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/lamborghini.jpg

# Download other car images
curl -L "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/toyota-camry.jpg
curl -L "https://images.pexels.com/photos/892522/pexels-photo-892522.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/honda-accord.jpg
curl -L "https://images.pexels.com/photos/12206396/pexels-photo-12206396.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/tesla-model3.jpg
curl -L "https://images.pexels.com/photos/2676096/pexels-photo-2676096.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/ford-f150.jpg
curl -L "https://images.pexels.com/photos/100656/pexels-photo-100656.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/bmw-3series.jpg
curl -L "https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/chevy-equinox.jpg
curl -L "https://images.pexels.com/photos/210019/pexels-photo-210019.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/hyundai-tucson.jpg
curl -L "https://images.pexels.com/photos/1035108/pexels-photo-1035108.jpeg?auto=compress&cs=tinysrgb&w=800" -o /Users/edward/Desktop/Projects/Findmycar2/public/images/cars/audi-q5.jpg

echo "All images downloaded successfully!"
