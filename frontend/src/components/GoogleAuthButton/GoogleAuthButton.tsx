import { useCallback, useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { sendGoogleTokenToBackend } from '../../services/authService';
import './GoogleAuthButton.scss';

export const GoogleAuthButton = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSuccess = useCallback(async (credentialResponse: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const idToken = credentialResponse.credential;

      // Send token to backend
      const response = await sendGoogleTokenToBackend(idToken);

      console.log('Authentication successful:', response);

      // You can redirect or update app state here
      window.location.reload();
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Authentication failed';
      setError(errorMessage);
      console.error('Authentication error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleError = useCallback(() => {
    setError('Login Failed');
    console.error('Google login error');
  }, []);

  return (
    <div className="google-auth-button">
      {error && <p className="google-auth-button__error">{error}</p>}
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={handleError}
        theme="outline"
        size="large"
        shape="pill"
        text="signin_with"
      />
      {isLoading && (
        <p className="google-auth-button__loading">Authenticating...</p>
      )}
    </div>
  );
};
