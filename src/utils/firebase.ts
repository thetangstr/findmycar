import { initializeApp } from 'firebase/app';
import { getStorage } from 'firebase/storage';
import { getFirestore } from 'firebase/firestore';

// Check if we have real Firebase credentials
const hasRealFirebaseCredentials = 
  process.env.NEXT_PUBLIC_FIREBASE_API_KEY && 
  !process.env.NEXT_PUBLIC_FIREBASE_API_KEY.includes('demo') &&
  process.env.NEXT_PUBLIC_FIREBASE_APP_ID &&
  !process.env.NEXT_PUBLIC_FIREBASE_APP_ID.includes('demo');

// Firebase configuration - only use real config if we have proper credentials
const firebaseConfig = hasRealFirebaseCredentials ? {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
} : null;

// Only initialize Firebase if we have real credentials
let app: any = null;
let storage: any = null;
let firestore: any = null;

if (firebaseConfig) {
  app = initializeApp(firebaseConfig);
  storage = getStorage(app);
  firestore = getFirestore(app);
} else if (process.env.NODE_ENV === 'development') {
  console.warn("⚠️  Firebase not initialized - using demo configuration. For full functionality, set up environment variables in .env.local");
}

export { app, storage, firestore };
