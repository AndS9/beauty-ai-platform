import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import {
  loginUser,
  sendGoogleTokenToBackend,
} from '../../services/authService';
import './LoginPage.scss';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError('Будь ласка, заповніть всі поля.');
      return;
    }

    try {
      setIsLoading(true);
      await loginUser({ email, password });
      navigate('/');
      window.location.reload();
    } catch (loginError) {
      const message =
        loginError instanceof Error ? loginError.message : 'Не вдалося увійти.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setError(null);
    setIsLoading(true);

    try {
      const idToken = credentialResponse.credential;
      await sendGoogleTokenToBackend(idToken);
      navigate('/');
      window.location.reload();
    } catch (googleError) {
      const message =
        googleError instanceof Error
          ? googleError.message
          : 'Не вдалося увійти через Google.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError('Не вдалося увійти через Google. Спробуйте ще раз.');
  };

  return (
    <section className="login section">
      <div className="login__card">
        <h1 className="login__title">Увійти</h1>
        <p className="login__subtitle">
          Введіть свої облікові дані для доступу до особистого кабінету.
        </p>

        <form className="login__form" onSubmit={handleSubmit}>
          <label className="login__label">
            Email
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="login__input"
              placeholder="example@mail.com"
              required
            />
          </label>

          <label className="login__label">
            Пароль
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="login__input"
              placeholder="Ваш пароль"
              required
            />
          </label>

          {error && <p className="login__error">{error}</p>}

          <button type="submit" className="login__button" disabled={isLoading}>
            {isLoading ? 'Увійти...' : 'Увійти'}
          </button>
        </form>

        <div className="login__separator">
          <span />
          <p>або</p>
          <span />
        </div>

        <div className="login__google">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            theme="outline"
            size="large"
            shape="pill"
            text="signin_with"
          />
        </div>
      </div>
    </section>
  );
};
