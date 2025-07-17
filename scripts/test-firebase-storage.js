/**
 * Script to test Firebase Storage connection
 * This script will test the connection to Firebase Storage and provide detailed error information
 */

const { initializeApp } = require('firebase/app');
const { getStorage, ref, uploadBytes, getDownloadURL } = require('firebase/storage');

// Firebase configuration - REPLACE WITH YOUR ACTUAL VALUES
const firebaseConfig = {
  apiKey: "AIzaSyDJEX-fLWA-XxxxxxxxxxxxxxxxxxxX", // REPLACE with your actual API key
  authDomain: "findmycar-347ec.firebaseapp.com",
  projectId: "findmycar-347ec",
  storageBucket: "findmycar-347ec.appspot.com",
  messagingSenderId: "1031395498953",
  appId: "1:1031395498953:web:xxxxxxxxxxxxxxxx" // REPLACE with your actual App ID
};

console.log('Testing Firebase Storage connection with the following configuration:');
console.log(JSON.stringify(firebaseConfig, null, 2));

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Get a reference to Firebase Storage
const storage = getStorage(app);
console.log('Storage bucket:', storage.app.options.storageBucket);

// Test Firebase Storage connection
async function testStorage() {
  try {
    console.log('Creating test file reference...');
    const testRef = ref(storage, 'test.txt');
    console.log('Test file path:', testRef._location.path_);
    
    console.log('Uploading test file...');
    const testBuffer = Buffer.from('Test file for Firebase Storage');
    await uploadBytes(testRef, testBuffer);
    
    console.log('Getting download URL...');
    const downloadURL = await getDownloadURL(testRef);
    console.log('Success! Test file URL:', downloadURL);
    
    return true;
  } catch (error) {
    console.error('Error testing Firebase Storage:');
    console.error('- Error code:', error.code);
    console.error('- Error message:', error.message);
    
    if (error.code === 'storage/unknown' && error.status_ === 404) {
      console.error('\nPossible causes of 404 error:');
      console.error('1. Firebase Storage is not enabled for your project');
      console.error('2. The Firebase API key is incorrect or redacted');
      console.error('3. The Firebase App ID is incorrect or redacted');
      console.error('4. The storage bucket name is incorrect');
      
      console.error('\nAction steps:');
      console.error('1. Go to the Firebase Console: https://console.firebase.google.com/');
      console.error('2. Select your project: findmycar-347ec');
      console.error('3. In the left sidebar, click on "Storage"');
      console.error('4. Click "Get Started" to enable Firebase Storage if not already enabled');
      console.error('5. Update this script with your actual Firebase API key and App ID');
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
