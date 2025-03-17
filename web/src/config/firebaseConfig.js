import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Initialize Firebase Configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app, "roll-and-score");

async function signIn() {
  try {
    await signInWithEmailAndPassword(auth,
      import.meta.env.VITE_FIREBASE_USER_EMAIL,
      import.meta.env.VITE_FIREBASE_USER_PASSWORD
    )
    console.log("Authenticated");
  } catch (error) {
    console.error("Error authenticating:", error);
  }
}

export { auth, db, signIn }
