/**
 * Simple Firebase Storage test
 * This script tests only the Firebase Storage connection with minimal dependencies
 */

const { initializeApp } = require('firebase/app');
const { getStorage, ref, uploadString, getDownloadURL } = require('firebase/storage');

// Simple test function
async function testStorage() {
  try {
    console.log('Starting simple Firebase Storage test...');
    
    // Firebase configuration - USE YOUR ACTUAL VALUES HERE
    const firebaseConfig = {
      apiKey: "YOUR_ACTUAL_API_KEY", // Replace with your actual API key
      authDomain: "findmycar-347ec.firebaseapp.com",
      projectId: "findmycar-347ec",
      storageBucket: "findmycar-347ec.appspot.com", 
      messagingSenderId: "1031395498953",
      appId: "YOUR_ACTUAL_APP_ID" // Replace with your actual App ID
    };
    
    console.log('Initializing Firebase with config:', JSON.stringify(firebaseConfig, null, 2));
    
    // Initialize Firebase
    const app = initializeApp(firebaseConfig);
    console.log('Firebase initialized successfully');
    
    // Initialize Storage
    const storage = getStorage(app);
    console.log('Storage initialized with bucket:', storage.app.options.storageBucket);
    
    // Create a reference
    const testRef = ref(storage, 'test-simple.txt');
    console.log('Created reference to:', testRef._location.path_);
    
    // Upload a simple string
    console.log('Uploading test string...');
    const snapshot = await uploadString(testRef, 'Hello, Firebase Storage!');
    console.log('Upload successful:', snapshot.metadata.name);
    
    // Get the download URL
    const url = await getDownloadURL(testRef);
    console.log('Download URL:', url);
    
    console.log('Test completed successfully!');
    return true;
  } catch (error) {
    console.error('Error in storage test:', error);
    
    // Check for specific error types
    if (error.code === 'storage/unknown' && error.status_ === 404) {
      console.error('\nStorage 404 Error: This typically means one of the following:');
      console.error('1. Firebase Storage is not enabled for your project');
      console.error('2. Your Firebase configuration (API key, App ID) is incorrect');
      console.error('3. Your storage bucket does not exist or is misconfigured');
      
      console.error('\nTo fix this:');
      console.error('1. Go to Firebase Console > Storage and ensure it\'s enabled');
      console.error('2. Double-check your API key and App ID in the Firebase Console');
      console.error('3. Verify your storage bucket name matches what\'s in the Firebase Console');
    }
    
    return false;
  }
}

// Run the test
testStorage().then(success => {
  if (success) {
    console.log('\nSuccess! Your Firebase Storage is working correctly.');
  } else {
    console.error('\nTest failed. Please fix the issues above and try again.');
  }
});
