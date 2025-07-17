/**
 * Script to update Firebase configuration files
 * 
 * This script will update your Firebase configuration files with the values you provide.
 * Run this script with your actual Firebase configuration values.
 */

const fs = require('fs');
const path = require('path');

// Your actual Firebase configuration values
// REPLACE THESE with your actual values from the Firebase Console
const FIREBASE_API_KEY = "YOUR_ACTUAL_API_KEY"; // Replace with your actual API key
const FIREBASE_AUTH_DOMAIN = "findmycar-347ec.firebaseapp.com";
const FIREBASE_PROJECT_ID = "findmycar-347ec";
const FIREBASE_STORAGE_BUCKET = "findmycar-347ec.appspot.com";
const FIREBASE_MESSAGING_SENDER_ID = "1031395498953";
const FIREBASE_APP_ID = "YOUR_ACTUAL_APP_ID"; // Replace with your actual App ID

// Files to update
const FILES_TO_UPDATE = [
  {
    path: path.join(__dirname, 'firebase-config.js'),
    pattern: /apiKey: ".*?"/,
    replacement: `apiKey: "${FIREBASE_API_KEY}"`
  },
  {
    path: path.join(__dirname, 'firebase-config.js'),
    pattern: /appId: ".*?"/,
    replacement: `appId: "${FIREBASE_APP_ID}"`
  },
  {
    path: path.join(__dirname, '../src/utils/firebase.ts'),
    pattern: /apiKey: ".*?"/,
    replacement: `apiKey: "${FIREBASE_API_KEY}"`
  },
  {
    path: path.join(__dirname, '../src/utils/firebase.ts'),
    pattern: /appId: ".*?"/,
    replacement: `appId: "${FIREBASE_APP_ID}"`
  }
];

// Update the files
FILES_TO_UPDATE.forEach(file => {
  if (!fs.existsSync(file.path)) {
    console.log(`File not found: ${file.path}`);
    return;
  }

  let content = fs.readFileSync(file.path, 'utf8');
  content = content.replace(file.pattern, file.replacement);
  fs.writeFileSync(file.path, content);
  console.log(`Updated ${file.path}`);
});

console.log('\nFirebase configuration files updated successfully!');
console.log('Now you can run the fix-firebase-storage.js script to upload images to Firebase Storage.');
