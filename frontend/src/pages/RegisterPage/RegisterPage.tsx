import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../../services/authService';
import './RegisterPage.scss';

export const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim() || !confirmPassword.trim()) {
      setError('Будь ласка, заповніть всі поля.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Паролі не співпадають.');
      return;
    }

    try {
      setIsLoading(true);
      await registerUser({ email, password });
      navigate('/login');
    } catch (registerError) {
      const message =
        registerError instanceof Error
          ? registerError.message
          : 'Не вдалося зареєструватися.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="register section">
      <div className="register__card">
        <h1 className="register__title">Реєстрація</h1>
        <p className="register__subtitle">
          Створіть акаунт, щоб зберегти обрані послуги та отримати доступ до
          бонусів.
        </p>

        <form className="register__form" onSubmit={handleSubmit}>
          <label className="register__label">
            Email
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="register__input"
              placeholder="example@mail.com"
              required
            />
          </label>

          <label className="register__label">
            Пароль
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="register__input"
              placeholder="Ваш пароль"
              required
            />
          </label>

          <label className="register__label">
            Підтвердження паролю
            <input
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              className="register__input"
              placeholder="Підтвердіть пароль"
              required
            />
          </label>

          {error && <p className="register__error">{error}</p>}

          <button
            type="submit"
            className="register__button"
            disabled={isLoading}
          >
            {isLoading ? 'Реєстрація...' : 'Зареєструватися'}
          </button>
        </form>
      </div>
    </section>
  );
};
