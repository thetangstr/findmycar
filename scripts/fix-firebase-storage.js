/**
 * Script to check and fix Firebase Storage issues
 * 
 * This script will:
 * 1. Verify Firebase Storage is properly configured
 * 2. Upload demo images to Firebase Storage
 * 3. Update Firestore with image URLs
 */

const path = require('path'); // Moved path import to the top
const envPath = path.resolve(__dirname, '../.env.local');
console.log(`[DEBUG] Attempting to load .env file from: ${envPath}`);
require('dotenv').config({ path: envPath }); // Load .env.local from project root

// DEBUGGING: Log critical environment variables
console.log('[DEBUG] NEXT_PUBLIC_FIREBASE_API_KEY from env:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY);
console.log('[DEBUG] NEXT_PUBLIC_FIREBASE_APP_ID from env:', process.env.NEXT_PUBLIC_FIREBASE_APP_ID);

const { initializeApp } = require('firebase/app');
const { getFirestore, collection, getDocs, doc, updateDoc } = require('firebase/firestore');
const { getStorage, ref, uploadBytes, getDownloadURL } = require('firebase/storage');
const axios = require('axios');
const fs = require('fs');
// const path = require('path'); // Removed duplicate declaration

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
};

// Validate Firebase configuration
if (!firebaseConfig.apiKey || firebaseConfig.apiKey.includes('xxxxx') || !firebaseConfig.appId || firebaseConfig.appId.includes('xxxxx')) {
  console.error('ERROR: Firebase API Key or App ID is missing, invalid, or still a placeholder in environment variables.');
  console.error('Please ensure your .env.local file in the project root is correctly set up with NEXT_PUBLIC_FIREBASE_API_KEY, NEXT_PUBLIC_FIREBASE_APP_ID, and other Firebase config values.');
  process.exit(1);
}

console.log('Using Firebase configuration from environment variables:');
console.log('- Project ID:', firebaseConfig.projectId);
console.log('- Storage Bucket:', firebaseConfig.storageBucket);

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Explicitly set the storage bucket to ensure correct reference
const storage = getStorage(app, `gs://${firebaseConfig.storageBucket}`);
const firestore = getFirestore(app);

// Log initialization details
console.log('Firebase app initialized with:');
console.log('- Project ID:', app.options.projectId);
console.log('- Storage Bucket:', app.options.storageBucket);

// Demo vehicle images from Unsplash
const demoVehicles = [
  {
    id: 'ford-mustang',
    make: 'Ford',
    model: 'Mustang',
    year: 2022,
    images: [
      'https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?q=80&w=1000',
      'https://images.unsplash.com/photo-1597007030739-6d2e7172ce2e?q=80&w=1000',
      'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?q=80&w=1000'
    ]
  },
  {
    id: 'tesla-model3',
    make: 'Tesla',
    model: 'Model 3',
    year: 2023,
    images: [
      'https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=1000',
      'https://images.unsplash.com/photo-1551826152-d7c8a974c0de?q=80&w=1000',
      'https://images.unsplash.com/photo-1617704548623-340376564e68?q=80&w=1000'
    ]
  },
  {
    id: 'bmw-m4',
    make: 'BMW',
    model: 'M4',
    year: 2022,
    images: [
      'https://images.unsplash.com/photo-1580273916550-e323be2ae537?q=80&w=1000',
      'https://images.unsplash.com/photo-1556189250-72ba954cfc2b?q=80&w=1000',
      'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=1000'
    ]
  }
];

// Main function
async function main() {
  console.log('Starting Firebase Storage fix script...');
  
  try {
    // 1. Test Firebase Storage connection
    console.log('Testing Firebase Storage connection...');
    const testRef = ref(storage, 'test.txt');
    const testBuffer = Buffer.from('Test file for Firebase Storage');
    
    try {
      console.log('Attempting to upload test file to:', testRef._location.path_);
      console.log('Using storage bucket:', storage.app.options.storageBucket);
      await uploadBytes(testRef, testBuffer);
      const downloadURL = await getDownloadURL(testRef);
      console.log('Firebase Storage is working! Test file URL:', downloadURL);
    } catch (error) {
      console.error('Error testing Firebase Storage:', error);
      console.error('Error details:', JSON.stringify(error, null, 2));
      console.error('Storage bucket:', storage.app.options.storageBucket);
      console.error('Firebase project ID:', app.options.projectId);
      console.log('\nPlease follow these steps to enable Firebase Storage:');
      console.log('1. Go to the Firebase Console: https://console.firebase.google.com/');
      console.log('2. Select your project: findmycar-347ec');
      console.log('3. In the left sidebar, click on "Storage"');
      console.log('4. Click "Get Started" to enable Firebase Storage');
      console.log('5. Select a location for your Storage bucket');
      console.log('6. Accept the default security rules or use the ones in storage.rules');
      console.log('7. Click "Done" to complete the setup');
      console.log('\nAfter enabling Firebase Storage, run this script again.');
      return;
    }
    
    // 2. Upload demo images to Firebase Storage
    console.log('\nUploading demo images to Firebase Storage...');
    
    for (const vehicle of demoVehicles) {
      console.log(`\nProcessing ${vehicle.make} ${vehicle.model}...`);
      const storageUrls = [];
      
      for (let i = 0; i < vehicle.images.length; i++) {
        const imageUrl = vehicle.images[i];
        console.log(`Downloading image ${i+1}...`);
        
        try {
          // Download image
          const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
          const buffer = Buffer.from(response.data, 'binary');
          
          // Generate filename
          const filename = `${vehicle.id}_${i}.jpg`;
          
          // Upload to Firebase Storage
          console.log(`Uploading image ${i+1} to Firebase Storage...`);
          const storageRef = ref(storage, `vehicles/${vehicle.id}/${filename}`);
          await uploadBytes(storageRef, buffer);
          
          // Get download URL
          const downloadURL = await getDownloadURL(storageRef);
          storageUrls.push(downloadURL);
          
          console.log(`Image ${i+1} uploaded successfully!`);
        } catch (error) {
          console.error(`Error processing image ${i+1}:`, error);
        }
      }
      
      // 3. Update Firestore with image URLs
      if (storageUrls.length > 0) {
        console.log(`Updating Firestore with ${storageUrls.length} image URLs...`);
        
        try {
          // Check if vehicle exists in Firestore
          const vehiclesCollection = collection(firestore, 'vehicles');
          const querySnapshot = await getDocs(vehiclesCollection);
          
          let vehicleDocId = null;
          querySnapshot.forEach((doc) => {
            const data = doc.data();
            if (data.id === vehicle.id || 
                (data.make === vehicle.make && 
                 data.model === vehicle.model && 
                 data.year === vehicle.year)) {
              vehicleDocId = doc.id;
            }
          });
          
          if (vehicleDocId) {
            // Update existing vehicle
            await updateDoc(doc(firestore, 'vehicles', vehicleDocId), {
              images: storageUrls,
              imageUrl: storageUrls[0],
              updatedAt: new Date().toISOString()
            });
            console.log(`Updated vehicle ${vehicle.id} in Firestore`);
          } else {
            console.log(`Vehicle ${vehicle.id} not found in Firestore. Creating a demo JSON file...`);
            
            // Create a demo JSON file
            const demoData = {
              id: vehicle.id,
              make: vehicle.make,
              model: vehicle.model,
              year: vehicle.year,
              price: Math.floor(Math.random() * 50000) + 20000,
              mileage: Math.floor(Math.random() * 50000),
              exteriorColor: ['Black', 'White', 'Silver', 'Red', 'Blue'][Math.floor(Math.random() * 5)],
              interiorColor: ['Black', 'Tan', 'Gray'][Math.floor(Math.random() * 3)],
              fuelType: ['Gasoline', 'Diesel', 'Electric', 'Hybrid'][Math.floor(Math.random() * 4)],
              transmission: ['Automatic', 'Manual'][Math.floor(Math.random() * 2)],
              engine: ['2.0L I4', '3.0L V6', '5.0L V8', 'Electric'][Math.floor(Math.random() * 4)],
              vin: 'DEMO' + Math.random().toString(36).substring(2, 10).toUpperCase(),
              description: `This ${vehicle.year} ${vehicle.make} ${vehicle.model} is in excellent condition with low mileage and a clean history.`,
              features: [
                'Bluetooth', 'Navigation', 'Leather Seats', 'Sunroof', 'Backup Camera',
                'Heated Seats', 'Apple CarPlay', 'Android Auto', 'Keyless Entry'
              ],
              images: storageUrls,
              imageUrl: storageUrls[0],
              location: 'Demo Location',
              dealer: 'Demo Dealer',
              listingDate: new Date().toISOString(),
              source: 'demo',
              url: '#'
            };
            
            const outputFile = path.join(__dirname, `${vehicle.id}.json`);
            fs.writeFileSync(outputFile, JSON.stringify(demoData, null, 2));
            console.log(`Created demo JSON file: ${outputFile}`);
          }
        } catch (error) {
          console.error(`Error updating Firestore:`, error);
        }
      }
    }
    
    console.log('\nFirebase Storage fix script completed successfully!');
  } catch (error) {
    console.error('Error in Firebase Storage fix script:', error);
  }
}

// Run the script
main();
