import { storage, firestore } from '@/utils/firebase';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { collection, addDoc, getDocs, query, where, doc, setDoc, getDoc } from 'firebase/firestore';
import { Vehicle } from '@/types';

// Collection names
const VEHICLES_COLLECTION = 'vehicles';
const IMAGES_COLLECTION = 'vehicle_images';

/**
 * Upload an image to Firebase Storage
 * @param file Image file to upload
 * @param vehicleId ID of the vehicle
 * @returns URL of the uploaded image
 */
export const uploadVehicleImage = async (file: File, vehicleId: string): Promise<string> => {
  try {
    const storageRef = ref(storage, `vehicles/${vehicleId}/${file.name}`);
    await uploadBytes(storageRef, file);
    const downloadURL = await getDownloadURL(storageRef);
    
    // Store the image reference in Firestore
    await addDoc(collection(firestore, IMAGES_COLLECTION), {
      vehicleId,
      imageUrl: downloadURL,
      fileName: file.name,
      uploadedAt: new Date().toISOString()
    });
    
    return downloadURL;
  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
};

/**
 * Get all images for a vehicle
 * @param vehicleId ID of the vehicle
 * @returns Array of image URLs
 */
export const getVehicleImages = async (vehicleId: string): Promise<string[]> => {
  try {
    const imagesQuery = query(
      collection(firestore, IMAGES_COLLECTION),
      where('vehicleId', '==', vehicleId)
    );
    
    const querySnapshot = await getDocs(imagesQuery);
    const images: string[] = [];
    
    querySnapshot.forEach((doc) => {
      const data = doc.data();
      images.push(data.imageUrl);
    });
    
    return images;
  } catch (error) {
    console.error('Error getting vehicle images:', error);
    return [];
  }
};

/**
 * Store a vehicle in Firestore
 * @param vehicle Vehicle data
 * @param imageUrl Main image URL
 * @returns ID of the stored vehicle
 */
export const storeVehicle = async (vehicle: Vehicle, imageUrl: string): Promise<string> => {
  try {
    // Check if vehicle already exists
    const vehiclesQuery = query(
      collection(firestore, VEHICLES_COLLECTION),
      where('id', '==', vehicle.id)
    );
    
    const querySnapshot = await getDocs(vehiclesQuery);
    
    if (!querySnapshot.empty) {
      // Update existing vehicle
      const docId = querySnapshot.docs[0].id;
      await setDoc(doc(firestore, VEHICLES_COLLECTION, docId), {
        ...vehicle,
        imageUrl,
        updatedAt: new Date().toISOString()
      });
      return docId;
    } else {
      // Add new vehicle
      const docRef = await addDoc(collection(firestore, VEHICLES_COLLECTION), {
        ...vehicle,
        imageUrl,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
      return docRef.id;
    }
  } catch (error) {
    console.error('Error storing vehicle:', error);
    throw error;
  }
};

/**
 * Get all vehicles from Firestore
 * @returns Array of vehicles with image URLs
 */
export const getFirestoreVehicles = async (): Promise<Vehicle[]> => {
  // If Firebase is not initialized, return empty array
  if (!firestore) {
    return [];
  }

  try {
    const querySnapshot = await getDocs(collection(firestore, VEHICLES_COLLECTION));
    const vehicles: Vehicle[] = [];
    
    querySnapshot.forEach((doc) => {
      const data = doc.data() as Vehicle;
      vehicles.push(data);
    });
    
    return vehicles;
  } catch (error) {
    console.error('Error getting vehicles:', error);
    return [];
  }
};

/**
 * Get a vehicle by ID from Firestore
 * @param id Vehicle ID
 * @returns Vehicle data or null if not found
 */
export const getFirestoreVehicleById = async (id: string): Promise<Vehicle | null> => {
  // If Firebase is not initialized, return null
  if (!firestore) {
    return null;
  }

  try {
    const vehiclesQuery = query(
      collection(firestore, VEHICLES_COLLECTION),
      where('id', '==', id)
    );
    
    const querySnapshot = await getDocs(vehiclesQuery);
    
    if (querySnapshot.empty) {
      return null;
    }
    
    return querySnapshot.docs[0].data() as Vehicle;
  } catch (error) {
    console.error('Error getting vehicle by ID:', error);
    return null;
  }
};
