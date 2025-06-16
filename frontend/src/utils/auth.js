import { auth } from "../firestoreSetUp/firebaseSetup";

/**
 * Get the currently authenticated user
 * @returns {Object|null} The current user object or null if not authenticated
 */
export const getCurrentUser = () => {
  return auth.currentUser;
};

/**
 * Check if a user is authenticated
 * @returns {boolean} True if user is authenticated, false otherwise
 */
export const isAuthenticated = () => {
  return !!auth.currentUser;
};

/**
 * Get the user's authentication token
 * @returns {Promise<string|null>} The user's ID token or null if not authenticated
 */
export const getUserToken = async () => {
  if (!auth.currentUser) return null;
  try {
    return await auth.currentUser.getIdToken();
  } catch (error) {
    console.error("Error getting user token:", error);
    return null;
  }
}; 