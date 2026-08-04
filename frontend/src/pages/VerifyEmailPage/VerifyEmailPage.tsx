import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './VerifyEmailPage.scss';

export const VerifyEmailPage = () => {
  const { uidb64, token } = useParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>(
    'loading',
  );
  const [message, setMessage] = useState('Підтвердження email...');
  const navigate = useNavigate();

  useEffect(() => {
    const verifyEmail = async () => {
      if (!uidb64 || !token) {
        setStatus('error');
        setMessage('Неправильне посилання для підтвердження.');
        return;
      }

      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:5000/api'}/users/verify-email/${uidb64}/${token}/`,
          {
            method: 'GET',
          },
        );

        if (!response.ok) {
          throw new Error('Підтвердження не вдалося.');
        }

        setStatus('success');
        setMessage('Email успішно підтверджено. Ви можете увійти.');
      } catch (error) {
        setStatus('error');
        setMessage(
          error instanceof Error
            ? error.message
            : 'Помилка під час підтвердження email.',
        );
      }
    };

    verifyEmail();
  }, [uidb64, token]);

  return (
    <section className="verify-email section">
      <div className="verify-email__card">
        <h1 className="verify-email__title">Підтвердження пошти</h1>
        <p className="verify-email__message">{message}</p>
        <button
          type="button"
          className="verify-email__button"
          onClick={() => navigate('/login')}
        >
          Перейти до входу
        </button>
      </div>
    </section>
  );
};
