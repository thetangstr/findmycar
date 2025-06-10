const fs = require('fs');
const path = require('path');
const https = require('https');

// Create the placeholders directory if it doesn't exist
const placeholdersDir = path.join(__dirname, '../public/placeholders');
if (!fs.existsSync(placeholdersDir)) {
  console.log('Creating placeholders directory');
  fs.mkdirSync(placeholdersDir, { recursive: true });
}

// Array of free placeholder car images from placeholder.com
// These are just colored blocks with car text - no actual car images to avoid copyright issues
const placeholderUrls = [
  { url: 'https://via.placeholder.com/800x600/3498db/FFFFFF?text=Car+Placeholder+1', filename: 'car1.jpg' },
  { url: 'https://via.placeholder.com/800x600/e74c3c/FFFFFF?text=Car+Placeholder+2', filename: 'car2.jpg' },
  { url: 'https://via.placeholder.com/800x600/2ecc71/FFFFFF?text=Car+Placeholder+3', filename: 'car3.jpg' },
  { url: 'https://via.placeholder.com/800x600/f39c12/FFFFFF?text=Car+Placeholder+4', filename: 'car4.jpg' },
  { url: 'https://via.placeholder.com/800x600/9b59b6/FFFFFF?text=Car+Placeholder+5', filename: 'car5.jpg' },
  { url: 'https://via.placeholder.com/800x600/1abc9c/FFFFFF?text=Car+Placeholder+6', filename: 'car6.jpg' },
  { url: 'https://via.placeholder.com/800x600/34495e/FFFFFF?text=Car+Placeholder+7', filename: 'car7.jpg' },
  { url: 'https://via.placeholder.com/800x600/e67e22/FFFFFF?text=Car+Placeholder+8', filename: 'car8.jpg' },
  { url: 'https://via.placeholder.com/800x600/95a5a6/FFFFFF?text=Car+Placeholder+9', filename: 'car9.jpg' },
  { url: 'https://via.placeholder.com/800x600/16a085/FFFFFF?text=Car+Placeholder+10', filename: 'car10.jpg' },
  { url: 'https://via.placeholder.com/800x600/d35400/FFFFFF?text=Car+Placeholder+11', filename: 'car11.jpg' },
  { url: 'https://via.placeholder.com/800x600/27ae60/FFFFFF?text=Car+Placeholder+12', filename: 'car12.jpg' },
  { url: 'https://via.placeholder.com/800x600/2980b9/FFFFFF?text=Car+Placeholder+13', filename: 'car13.jpg' },
  { url: 'https://via.placeholder.com/800x600/8e44ad/FFFFFF?text=Car+Placeholder+14', filename: 'car14.jpg' },
  { url: 'https://via.placeholder.com/800x600/c0392b/FFFFFF?text=Car+Placeholder+15', filename: 'car15.jpg' },
  { url: 'https://via.placeholder.com/800x600/7f8c8d/FFFFFF?text=Car+Placeholder+16', filename: 'car16.jpg' },
];

// Actually, since we've been having DNS resolution errors with placeholder.com,
// let's create our own placeholder images using Node.js to avoid network dependencies
const createLocalPlaceholder = (index, callback) => {
  const colors = [
    '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
    '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#16a085',
    '#d35400', '#27ae60', '#2980b9', '#8e44ad', '#c0392b', '#7f8c8d'
  ];
  
  const filepath = path.join(placeholdersDir, `car${index}.jpg`);
  
  // Create a very simple HTML that has a colored div with text
  const html = `
    <html>
      <head>
        <style>
          body { margin: 0; padding: 0; }
          .placeholder {
            width: 800px;
            height: 600px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: ${colors[(index - 1) % colors.length]};
            color: white;
            font-family: Arial, sans-serif;
            font-size: 24px;
            text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="placeholder">
          Car Placeholder ${index}<br>
          <span style="font-size: 16px;">(Local image - no DNS resolution needed)</span>
        </div>
      </body>
    </html>
  `;

  // Write the HTML to a file
  fs.writeFileSync(filepath, html);
  console.log(`Created local placeholder: ${filepath}`);
  callback();
}

console.log('Creating local placeholder images...');
let completed = 0;

for (let i = 1; i <= 16; i++) {
  createLocalPlaceholder(i, () => {
    completed++;
    if (completed === 16) {
      console.log('All placeholder images created!');
      console.log('Please rebuild the app with "npm run build" and deploy again to see the placeholders');
    }
  });
}
