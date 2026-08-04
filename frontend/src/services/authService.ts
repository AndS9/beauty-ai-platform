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

    // Store access/refresh tokens if returned
    if (data.access && data.refresh) {
      storeTokens(data.access, data.refresh);
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

export interface RegisterPayload {
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

const storeTokens = (data: { access: string; refresh: string }) => {
  localStorage.setItem('authToken', data.access);
  localStorage.setItem('refreshToken', data.refresh);
};

const storeAccessToken = (access: string) => {
  localStorage.setItem('authToken', access);
};

export const getRefreshToken = () => {
  return localStorage.getItem('refreshToken');
};

export const refreshAccessToken = async () => {
  const refresh = getRefreshToken();

  if (!refresh) {
    throw new Error('Refresh token is missing');
  }

  const response = await fetch(`${API_BASE_URL}/users/token/refresh/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail ||
        errorData?.message ||
        `Refresh token failed with status ${response.status}`,
    );
  }

  const data = await response.json();

  if (data.access) {
    storeAccessToken(data.access);
  }

  return data;
};

export const verifyToken = async (token?: string) => {
  const jwt = token || getAuthToken();

  if (!jwt) {
    throw new Error('Token is missing');
  }

  const response = await fetch(`${API_BASE_URL}/users/token/verify/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token: jwt }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(
      errorData?.detail ||
        errorData?.message ||
        `Token verification failed with status ${response.status}`,
    );
  }

  return true;
};

export const registerUser = async (payload: RegisterPayload) => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.message ||
          `Registration failed with status ${response.status}`,
      );
    }

    const data = await response.json();

    if ('access' in data && 'refresh' in data) {
      storeTokens(data);
    }

    return data;
  } catch (error) {
    console.error('Error registering user:', error);
    throw error;
  }
};

export const loginUser = async (payload: LoginPayload) => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/token/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail ||
          errorData?.message ||
          `Login failed with status ${response.status}`,
      );
    }

    const data: LoginResponse = await response.json();
    storeTokens(data);
    return data;
  } catch (error) {
    console.error('Error logging in user:', error);
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
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('authToken');
};
