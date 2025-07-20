// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAb2sSCDl9d73lh6crCfZ2bpQ_P9fatUB0",
  authDomain: "findmycar-347ec.firebaseapp.com",
  projectId: "findmycar-347ec",
  storageBucket: "findmycar-347ec.firebasestorage.app",
  messagingSenderId: "1031395498953",
  appId: "1:1031395498953:web:cf8bedd1cca4dda83b2618"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export default app;