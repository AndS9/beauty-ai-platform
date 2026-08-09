import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../../services/authService';
import './RegisterPage.scss';

export const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (
      !email.trim() ||
      !password.trim() ||
      !confirmPassword.trim() ||
      !firstName.trim() ||
      !lastName.trim() ||
      !phone.trim()
    ) {
      setError('Будь ласка, заповніть всі поля.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Паролі не співпадають.');
      return;
    }

    try {
      setIsLoading(true);
      const data = await registerUser({
        email,
        password,
        password1: password,
        password2: confirmPassword,
        password_confirmation: confirmPassword,
        first_name: firstName,
        last_name: lastName,
        phone,
        phone_number: phone,
      });

      if (data?.access && data?.refresh) {
        navigate('/');
        window.location.reload();
      } else {
        navigate('/');
      }
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
            Ім'я
            <input
              type="text"
              value={firstName}
              onChange={e => setFirstName(e.target.value)}
              className="register__input"
              placeholder="Ваше ім'я"
              required
            />
          </label>

          <label className="register__label">
            Прізвище
            <input
              type="text"
              value={lastName}
              onChange={e => setLastName(e.target.value)}
              className="register__input"
              placeholder="Ваше прізвище"
              required
            />
          </label>

          <label className="register__label">
            Телефон
            <input
              type="tel"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              className="register__input"
              placeholder="+380..."
              required
            />
          </label>

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
