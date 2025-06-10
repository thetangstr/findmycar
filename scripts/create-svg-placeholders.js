const fs = require('fs');
const path = require('path');

// Create the placeholders directory if it doesn't exist
const placeholdersDir = path.join(__dirname, '../public/placeholders');
if (!fs.existsSync(placeholdersDir)) {
  console.log('Creating placeholders directory');
  fs.mkdirSync(placeholdersDir, { recursive: true });
}

// Array of colors for different placeholders
const colors = [
  '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
  '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085',
  '#d35400', '#27ae60', '#2980b9', '#8e44ad', '#c0392b', '#7f8c8d'
];

// Car make labels for the placeholders
const carLabels = [
  'Porsche', 'BMW', 'Mercedes', 'Audi', 'Volkswagen',
  'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Dodge',
  'Sedan', 'SUV', 'Truck', 'Sports Car', 'Luxury Car', 'Vehicle'
];

// Create SVG files
console.log('Creating SVG placeholder images...');
for (let i = 1; i <= 16; i++) {
  const color = colors[(i - 1) % colors.length];
  const label = carLabels[(i - 1) % carLabels.length];
  
  // Create an SVG with the car make and a simple car silhouette
  const svgContent = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="${color}" />
  <text x="400" y="250" font-family="Arial" font-size="40" text-anchor="middle" fill="white">${label}</text>
  <text x="400" y="300" font-family="Arial" font-size="24" text-anchor="middle" fill="white">Placeholder</text>
  
  <!-- Simple car silhouette -->
  <g transform="translate(300, 350) scale(0.8)">
    <!-- Car body -->
    <path d="M30,80 L30,100 L270,100 L270,80 L240,40 L60,40 Z" fill="white" opacity="0.8" />
    <!-- Wheels -->
    <circle cx="80" cy="100" r="20" fill="white" opacity="0.8" />
    <circle cx="220" cy="100" r="20" fill="white" opacity="0.8" />
    <!-- Windows -->
    <path d="M80,40 L100,70 L200,70 L220,40 Z" fill="white" opacity="0.6" />
  </g>
</svg>`;
  
  const filepath = path.join(placeholdersDir, `car${i}.svg`);
  fs.writeFileSync(filepath, svgContent);
  console.log(`Created SVG placeholder: ${filepath}`);
}

console.log('All placeholder images created!');
console.log('Please rebuild the app with "npm run build" and deploy again to see the placeholders');
