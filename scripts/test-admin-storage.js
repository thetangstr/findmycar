/**
 * Test Firebase Storage using Admin SDK
 * This approach bypasses the need for API keys
 */

const admin = require('firebase-admin');
const fs = require('fs');
const path = require('path');

// Initialize Firebase Admin with default credentials
// This will use the GOOGLE_APPLICATION_CREDENTIALS environment variable
// or the default service account if running on Google Cloud
try {
  admin.initializeApp({
    projectId: 'findmycar-347ec',
    storageBucket: 'findmycar-347ec.appspot.com'
  });

  console.log('Firebase Admin SDK initialized successfully');
  console.log('Project ID:', admin.app().options.projectId);
  console.log('Storage Bucket:', admin.app().options.storageBucket);
} catch (error) {
  console.error('Error initializing Firebase Admin SDK:', error);
  process.exit(1);
}

// Get a reference to the storage service
const bucket = admin.storage().bucket();

// Test function to check if Firebase Storage is enabled
async function testStorage() {
  try {
    console.log('\nTesting Firebase Storage...');
    
    // Create a test file
    const testFilePath = path.join(__dirname, 'test-file.txt');
    fs.writeFileSync(testFilePath, 'This is a test file for Firebase Storage');
    
    // Upload the test file
    console.log('Uploading test file...');
    await bucket.upload(testFilePath, {
      destination: 'test-file.txt',
      metadata: {
        contentType: 'text/plain',
      }
    });
    
    console.log('Test file uploaded successfully!');
    
    // Get the file
    console.log('Getting file metadata...');
    const [file] = await bucket.file('test-file.txt').get();
    console.log('File metadata:', file.metadata);
    
    // Generate a signed URL
    console.log('Generating signed URL...');
    const [url] = await bucket.file('test-file.txt').getSignedUrl({
      action: 'read',
      expires: Date.now() + 1000 * 60 * 60, // 1 hour
    });
    
    console.log('Signed URL:', url);
    
    // Clean up
    fs.unlinkSync(testFilePath);
    
    return true;
  } catch (error) {
    console.error('Error testing Firebase Storage:', error);
    
    if (error.code === 404 || (error.code === 'storage/unknown' && error.status_ === 404)) {
      console.error('\nFirebase Storage is not enabled for this project.');
      console.error('Please follow these steps:');
      console.error('1. Go to the Firebase Console: https://console.firebase.google.com/');
      console.error('2. Select your project: findmycar-347ec');
      console.error('3. In the left sidebar, click on "Storage"');
      console.error('4. Click "Get Started" to enable Firebase Storage');
      console.error('5. Select a location for your Storage bucket');
      console.error('6. Accept the default security rules or use the ones in storage.rules');
      console.error('7. Click "Done" to complete the setup');
    } else if (error.code === 403) {
      console.error('\nPermission denied. Your service account may not have the required permissions.');
      console.error('Please make sure your service account has the Storage Admin role.');
    }
    
    return false;
  }
}

// Run the test
testStorage().then(success => {
  if (success) {
    console.log('\nFirebase Storage is working correctly!');
  } else {
    console.error('\nFirebase Storage test failed. Please fix the issues above and try again.');
  }
});
