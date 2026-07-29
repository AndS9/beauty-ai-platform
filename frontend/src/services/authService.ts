// Google OAuth service for handling authentication

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export interface GoogleAuthResponse {
  access_token?: string;
  token_type?: string;
  expires_in?: number;
  scope?: string;
  error?: string;
}

export interface AuthTokenPayload {
  id_token: string;
}

/**
 * Send Google ID token to backend for authentication
 */
export const sendGoogleTokenToBackend = async (idToken: string) => {
  try {
    const payload: AuthTokenPayload = {
      id_token: idToken,
    };

    const response = await fetch(`${API_BASE_URL}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Authentication failed');
    }

    const data = await response.json();

    // Store authentication token if provided
    if (data.token) {
      localStorage.setItem('authToken', data.token);
    }

    // Store user info if provided
    if (data.user) {
      localStorage.setItem('user', JSON.stringify(data.user));
    }

    return data;
  } catch (error) {
    console.error('Error sending token to backend:', error);
    throw error;
  }
};

/**
 * Get stored authentication token
 */
export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

/**
 * Get stored user info
 */
export const getUserInfo = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Logout and clear stored data
 */
export const logout = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('authToken');
};
