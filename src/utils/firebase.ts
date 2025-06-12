import { initializeApp, getApps, getApp } from 'firebase/app';
import { getStorage } from 'firebase/storage';
import { getFirestore } from 'firebase/firestore';

// For production deployment, we need to use hardcoded values since environment variables
// aren't properly available in the static export
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyDZBmO78YYOKFOLQP8f3AiQS1JHC4OMkXY",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "findmycar-347ec.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "findmycar-347ec",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "findmycar-347ec.appspot.com",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "744301257853",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:744301257853:web:7e37cd5186a4cea36cd10b",
};

// Initialize Firebase safely
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const firestore = getFirestore(app);
const storage = getStorage(app);

// Optional: Warn if using placeholder credentials
if (!firebaseConfig.apiKey || firebaseConfig.apiKey.includes('demo')) {
  console.warn("⚠️ Firebase is using demo/placeholder credentials. For full functionality, set up environment variables in .env.local");
}

export { app, storage, firestore };
