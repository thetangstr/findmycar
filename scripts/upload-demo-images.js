// This script downloads demo car images from the internet and uploads them to Firebase Storage
const fs = require('fs');
const path = require('path');
const https = require('https');
const { initializeApp } = require('firebase/app');
const { getStorage, ref, uploadBytes, getDownloadURL } = require('firebase/storage');
const { getFirestore, collection, addDoc, setDoc, doc } = require('firebase/firestore');

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDJEX-fLWA-XxxxxxxxxxxxxxxxxxxX",
  authDomain: "findmycar-347ec.firebaseapp.com",
  projectId: "findmycar-347ec",
  storageBucket: "findmycar-347ec.appspot.com",
  messagingSenderId: "1031395498953",
  appId: "1:1031395498953:web:xxxxxxxxxxxxxxxx"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const storage = getStorage(app);
const firestore = getFirestore(app);

// Car image URLs - high quality, free-to-use images from reputable sources
const carImages = [
  {
    id: 'porsche-911',
    make: 'Porsche',
    model: '911',
    year: 1995,
    price: 120000,
    mileage: 45000,
    exteriorColor: 'Silver',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Manual',
    engine: '3.6L Flat-6',
    vin: 'WP0AA29975S710001',
    description: 'Classic Porsche 911 in excellent condition. Well maintained with service records.',
    imageUrl: 'https://images.unsplash.com/photo-1580274455191-1c62238fa333?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1580274455191-1c62238fa333?q=80&w=2000',
      'https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=2000',
      'https://images.unsplash.com/photo-1611821064430-0d40291d0f0b?q=80&w=2000'
    ]
  },
  {
    id: 'corvette',
    make: 'Chevrolet',
    model: 'Corvette',
    year: 1963,
    price: 150000,
    mileage: 35000,
    exteriorColor: 'Red',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Manual',
    engine: '5.7L V8',
    vin: '30837S100001',
    description: 'Iconic American sports car in pristine condition. A true collector\'s item.',
    imageUrl: 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=2000',
      'https://images.unsplash.com/photo-1591293836027-e05b48473b67?q=80&w=2000',
      'https://images.unsplash.com/photo-1577495508326-19a1b3cf65b9?q=80&w=2000'
    ]
  },
  {
    id: 'lamborghini',
    make: 'Lamborghini',
    model: 'Aventador',
    year: 2020,
    price: 450000,
    mileage: 5000,
    exteriorColor: 'Yellow',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '6.5L V12',
    vin: 'ZHWUT4ZF7LLA12345',
    description: 'Stunning Lamborghini Aventador with low mileage. A true supercar experience.',
    imageUrl: 'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?q=80&w=2000',
      'https://images.unsplash.com/photo-1519245160502-b9558a5cf7af?q=80&w=2000',
      'https://images.unsplash.com/photo-1511919884226-fd3cad34687c?q=80&w=2000'
    ]
  },
  {
    id: 'tesla-model3',
    make: 'Tesla',
    model: 'Model 3',
    year: 2022,
    price: 45000,
    mileage: 10000,
    exteriorColor: 'White',
    interiorColor: 'Black',
    fuelType: 'Electric',
    transmission: 'Automatic',
    engine: 'Electric',
    vin: '5YJ3E1EA1MF123456',
    description: 'Modern electric sedan with autopilot capabilities and long range battery.',
    imageUrl: 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=2000',
      'https://images.unsplash.com/photo-1551826152-d7c8a974c0c9?q=80&w=2000',
      'https://images.unsplash.com/photo-1561580125-028ee3bd62eb?q=80&w=2000'
    ]
  },
  {
    id: 'bmw-3series',
    make: 'BMW',
    model: '3 Series',
    year: 2021,
    price: 42000,
    mileage: 15000,
    exteriorColor: 'Blue',
    interiorColor: 'Beige',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo I4',
    vin: 'WBA5R1C50LFH12345',
    description: 'Luxury sports sedan with premium features and excellent handling.',
    imageUrl: 'https://images.unsplash.com/photo-1556189250-72ba954cfc2b?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1556189250-72ba954cfc2b?q=80&w=2000',
      'https://images.unsplash.com/photo-1543796076-c4a7069e2bf5?q=80&w=2000',
      'https://images.unsplash.com/photo-1523983388277-336a66bf9bcd?q=80&w=2000'
    ]
  },
  {
    id: 'ford-f150',
    make: 'Ford',
    model: 'F-150',
    year: 2020,
    price: 38000,
    mileage: 25000,
    exteriorColor: 'Black',
    interiorColor: 'Gray',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '3.5L EcoBoost V6',
    vin: '1FTEW1E53LFA12345',
    description: 'Powerful and capable pickup truck with towing package and off-road capabilities.',
    imageUrl: 'https://images.unsplash.com/photo-1605893477799-b99e3b8b93fe?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1605893477799-b99e3b8b93fe?q=80&w=2000',
      'https://images.unsplash.com/photo-1609710219611-33446ea1f2bc?q=80&w=2000',
      'https://images.unsplash.com/photo-1583267746897-2cf415887172?q=80&w=2000'
    ]
  },
  {
    id: 'honda-accord',
    make: 'Honda',
    model: 'Accord',
    year: 2021,
    price: 28000,
    mileage: 18000,
    exteriorColor: 'Silver',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '1.5L Turbo I4',
    vin: '1HGCV1F34MA123456',
    description: 'Reliable and efficient sedan with modern tech features and comfortable ride.',
    imageUrl: 'https://images.unsplash.com/photo-1629897048514-3dd7414efc45?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1629897048514-3dd7414efc45?q=80&w=2000',
      'https://images.unsplash.com/photo-1631880383152-a67eac9d7e24?q=80&w=2000',
      'https://images.unsplash.com/photo-1590510696698-6a5d8d53c27a?q=80&w=2000'
    ]
  },
  {
    id: 'toyota-camry',
    make: 'Toyota',
    model: 'Camry',
    year: 2022,
    price: 30000,
    mileage: 12000,
    exteriorColor: 'Red',
    interiorColor: 'Beige',
    fuelType: 'Hybrid',
    transmission: 'Automatic',
    engine: '2.5L I4 Hybrid',
    vin: '4T1BZ1HK5NU123456',
    description: 'Fuel-efficient hybrid sedan with Toyota Safety Sense and spacious interior.',
    imageUrl: 'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?q=80&w=2000',
      'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?q=80&w=2000',
      'https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?q=80&w=2000'
    ]
  },
  {
    id: 'audi-q5',
    make: 'Audi',
    model: 'Q5',
    year: 2021,
    price: 48000,
    mileage: 20000,
    exteriorColor: 'Gray',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.0L Turbo I4',
    vin: 'WA1BNAFY5M2123456',
    description: 'Luxury compact SUV with Quattro all-wheel drive and premium interior.',
    imageUrl: 'https://images.unsplash.com/photo-1606664913048-8386e1f8c8a5?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1606664913048-8386e1f8c8a5?q=80&w=2000',
      'https://images.unsplash.com/photo-1606664913048-8386e1f8c8a5?q=80&w=2000',
      'https://images.unsplash.com/photo-1606664913048-8386e1f8c8a5?q=80&w=2000'
    ]
  },
  {
    id: 'hyundai-tucson',
    make: 'Hyundai',
    model: 'Tucson',
    year: 2022,
    price: 32000,
    mileage: 8000,
    exteriorColor: 'Green',
    interiorColor: 'Gray',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '2.5L I4',
    vin: 'KM8JBCA19NU123456',
    description: 'Modern compact SUV with distinctive styling and comprehensive warranty.',
    imageUrl: 'https://images.unsplash.com/photo-1633708725803-bc0ef4c3f05c?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1633708725803-bc0ef4c3f05c?q=80&w=2000',
      'https://images.unsplash.com/photo-1633708725803-bc0ef4c3f05c?q=80&w=2000',
      'https://images.unsplash.com/photo-1633708725803-bc0ef4c3f05c?q=80&w=2000'
    ]
  },
  {
    id: 'chevy-equinox',
    make: 'Chevrolet',
    model: 'Equinox',
    year: 2021,
    price: 29000,
    mileage: 22000,
    exteriorColor: 'Blue',
    interiorColor: 'Black',
    fuelType: 'Gasoline',
    transmission: 'Automatic',
    engine: '1.5L Turbo I4',
    vin: '2GNAXUEV5M6123456',
    description: 'Practical and affordable compact SUV with good fuel economy and tech features.',
    imageUrl: 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2000',
    images: [
      'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2000',
      'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2000',
      'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=2000'
    ]
  }
];

// Function to download an image from a URL
const downloadImage = (url, filepath) => {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(filepath);
    https.get(url, response => {
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', err => {
      fs.unlink(filepath, () => {}); // Delete the file if there was an error
      reject(err);
    });
  });
};

// Function to upload an image to Firebase Storage
const uploadImageToStorage = async (filepath, filename, vehicleId) => {
  try {
    const fileBuffer = fs.readFileSync(filepath);
    const storageRef = ref(storage, `vehicles/${vehicleId}/${filename}`);
    await uploadBytes(storageRef, fileBuffer);
    const downloadURL = await getDownloadURL(storageRef);
    return downloadURL;
  } catch (error) {
    console.error(`Error uploading ${filename}:`, error);
    throw error;
  }
};

// Function to store vehicle data in Firestore
const storeVehicleInFirestore = async (vehicle, imageUrls) => {
  try {
    // Store the main vehicle data
    const vehicleRef = doc(firestore, 'vehicles', vehicle.id);
    await setDoc(vehicleRef, {
      ...vehicle,
      imageUrl: imageUrls[0], // Main image
      images: imageUrls,      // All images
      updatedAt: new Date().toISOString()
    });
    
    console.log(`Vehicle ${vehicle.id} stored in Firestore`);
    return vehicleRef.id;
  } catch (error) {
    console.error(`Error storing vehicle ${vehicle.id}:`, error);
    throw error;
  }
};

// Main function to process all cars
const processAllCars = async () => {
  // Create temp directory if it doesn't exist
  const tempDir = path.join(__dirname, 'temp');
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir);
  }
  
  for (const car of carImages) {
    console.log(`Processing ${car.make} ${car.model}...`);
    const imageUrls = [];
    
    // Process each image for the car
    for (let i = 0; i < car.images.length; i++) {
      const imageUrl = car.images[i];
      const filename = `${car.id}_${i}.jpg`;
      const filepath = path.join(tempDir, filename);
      
      try {
        // Download the image
        console.log(`Downloading image ${i+1} for ${car.id}...`);
        await downloadImage(imageUrl, filepath);
        
        // Upload to Firebase Storage
        console.log(`Uploading image ${i+1} for ${car.id} to Firebase Storage...`);
        const uploadedUrl = await uploadImageToStorage(filepath, filename, car.id);
        imageUrls.push(uploadedUrl);
        
        // Clean up the temp file
        fs.unlinkSync(filepath);
      } catch (error) {
        console.error(`Error processing image ${i+1} for ${car.id}:`, error);
      }
    }
    
    if (imageUrls.length > 0) {
      // Store the vehicle data with image URLs in Firestore
      await storeVehicleInFirestore(car, imageUrls);
    }
  }
  
  console.log('All cars processed successfully!');
};

// Run the script
processAllCars().catch(error => {
  console.error('Error processing cars:', error);
});
