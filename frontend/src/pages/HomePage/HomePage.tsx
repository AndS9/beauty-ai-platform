import { useState } from 'react';
import './HomePage.scss';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const categories = [
  { title: 'Манікюр', meta: 'від 500 грн' },
  { title: 'Перукар', meta: 'від 600 грн' },
  { title: 'Брови', meta: 'від 300 грн' },
  { title: 'Макіяж', meta: 'від 700 грн' },
  { title: 'Косметологія', meta: 'від 900 грн' },
  { title: 'Масаж', meta: 'від 700 грн' },
];

const results = [
  {
    title: 'Beauty Studio',
    category: 'Салон краси',
    rating: '4.9',
    reviews: 128,
    distance: '1.2 км від вас',
    price: 'від 700 грн',
    services: [
      'Манікюр від 700 грн',
      'Стрижка від 600 грн',
      'Мейкап від 900 грн',
    ],
    available: 'Доступний сьогодні',
    badge: 'AI Рекомендація',
  },
  {
    title: 'Анна Коваль',
    category: 'Майстер манікюру',
    rating: '5.0',
    reviews: 96,
    distance: '0.6 км від вас',
    price: 'від 600 грн',
    services: [
      'Манікюр від 600 грн',
      'Покриття від 500 грн',
      'Дизайн від 100 грн',
    ],
    available: 'Доступний сьогодні о 18:00',
    badge: 'Популярний',
  },
  {
    title: 'Chop-Chop Barbershop',
    category: 'Барбершоп',
    rating: '4.8',
    reviews: 74,
    distance: '2.1 км від вас',
    price: 'від 500 грн',
    services: [
      'Стрижка від 500 грн',
      'Борода від 300 грн',
      'Комплекс від 700 грн',
    ],
    available: 'Доступний сьогодні',
    badge: 'Рекомендовано',
  },
  {
    title: 'Luna Beauty House',
    category: 'Салон краси',
    rating: '4.7',
    reviews: 83,
    distance: '3.0 км від вас',
    price: 'від 850 грн',
    services: [
      'Косметологія від 850 грн',
      'Масаж від 700 грн',
      'Пілінг від 500 грн',
    ],
    available: 'Завтра з 10:00',
    badge: 'Новинка',
  },
  {
    title: 'Perfect Nails',
    category: 'Манікюрний центр',
    rating: '4.9',
    reviews: 156,
    distance: '0.8 км від вас',
    price: 'від 550 грн',
    services: [
      'Манікюр від 550 грн',
      'Педикюр від 600 грн',
      'Дизайн від 150 грн',
    ],
    available: 'Доступний сьогодні',
    badge: 'Топовий',
  },
  {
    title: 'Перукарня "Стиль"',
    category: 'Перукарня',
    rating: '4.6',
    reviews: 92,
    distance: '1.5 км від вас',
    price: 'від 650 грн',
    services: [
      'Стрижка від 650 грн',
      'Фарбування від 900 грн',
      'Укладання від 400 грн',
    ],
    available: 'Вільні місця',
    badge: 'Популярна',
  },
];

export const HomePage = () => {
  const [price, setPrice] = useState(1200);

  return (
    <div className="home-page">
      <section className="hero">
        <div className="hero__content">
          <p className="hero__eyebrow">AI Рекомендації</p>
          <h1 className="hero__title">
            Знайдіть ідеального майстра за допомогою <span>AI</span>
          </h1>
          <p className="hero__subtitle">
            Опишіть, що вам потрібно, а ми знайдемо найкращі варіанти серед салонів та незалежних майстрів.
          </p>

          <div className="hero__search">
            <label className="hero__search-input-field">
              <span className="hero__search-icon">✨</span>
              <input
                type="text"
                placeholder="Наприклад: Манікюр до 800 грн біля мене сьогодні після 18:00"
              />
            </label>
            <button type="button" className="hero__search-location">
              📍 Біля мене
            </button>
            <button type="button" className="hero__search-button">
              Знайти
            </button>
          </div>
        </div>
      </section>

      <section className="home-page__search-section">
        <aside className="home-page__sidebar">
          <div className="home-page__panel home-page__panel--sticky">
            <div className="home-page__panel-header">
              <h2>Фільтри</h2>
              <button type="button">Очистити все</button>
            </div>

            <div className="home-page__filter-group">
              <h3>Категорія</h3>
              <div className="home-page__checkbox-list">
                {[
                  'Всі категорії',
                  'Манікюр',
                  'Перукар',
                  'Барбери',
                  'Макіяж',
                  'Косметологія',
                  'Масаж',
                ].map(name => (
                  <label key={name} className="home-page__checkbox-item">
                    <input
                      type="checkbox"
                      defaultChecked={name === 'Всі категорії'}
                    />
                    <span>{name}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="home-page__filter-group">
              <h3>Ціна, грн</h3>
              <div className="home-page__range-input">
                <input
                  type="range"
                  min="0"
                  max="5000"
                  value={price}
                  onChange={event => setPrice(Number(event.target.value))}
                />
                <div className="home-page__price-value">
                  {price.toLocaleString('uk-UA')} грн
                </div>
                <div className="home-page__range-values">
                  <span>0</span>
                  <span>5000+</span>
                </div>
              </div>
            </div>

            <div className="home-page__filter-group">
              <h3>Рейтинг</h3>
              <div className="home-page__chip-list">
                {['Будь-який', '4.5+', '4.9+', '5.0'].map(name => (
                  <button
                    key={name}
                    type="button"
                    className={
                      name === 'Будь-який'
                        ? 'home-page__chip home-page__chip--active'
                        : 'home-page__chip'
                    }
                  >
                    {name}
                  </button>
                ))}
              </div>
            </div>

            <div className="home-page__filter-group">
              <h3>Відстань</h3>
              <select>
                <option>Будь-яка</option>
                <option>До 1 км</option>
                <option>До 3 км</option>
                <option>До 5 км</option>
              </select>
            </div>

            <div className="home-page__filter-group">
              <h3>Доступність</h3>
              <label className="home-page__switch">
                <input type="checkbox" defaultChecked />
                <span>Доступний сьогодні</span>
              </label>
            </div>
          </div>

          <div className="home-page__panel home-page__panel--compact">
            <h3>Популярні категорії</h3>
            <div className="home-page__popular-grid">
              {categories.map(item => (
                <div key={item.title} className="home-page__popular-card">
                  <div className="home-page__popular-card-icon">
                    {item.title.charAt(0)}
                  </div>
                  <div>
                    <p>{item.title}</p>
                    <span>{item.meta}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        <main className="home-page__results">
          <div className="home-page__results-header">
            <div>
              <p className="home-page__results-count">
                Знайдено 128 результатів
              </p>
              <p className="home-page__results-subtitle">
                Сортування: Рекомендовані
              </p>
            </div>
            <div className="home-page__tab-list">
              <button
                type="button"
                className="home-page__tab home-page__tab--active"
              >
                Всі результати
              </button>
              <button type="button" className="home-page__tab">
                AI Рекомендації
              </button>
            </div>
          </div>

          <div className="home-page__cards-grid">
            {results.map(item => (
              <article key={item.title} className="home-page__result-card">
                <div className="home-page__result-card-top">
                  <div className="home-page__result-card-badge">
                    {item.badge}
                  </div>

                </div>
                <div className="home-page__result-card-image" />
                <div className="home-page__result-card-body">
                  <div className="home-page__result-card-label">
                    {item.category}
                  </div>
                  <h3>{item.title}</h3>
                  <div className="home-page__result-card-info">
                    <span>{item.rating}</span>
                    <span>({item.reviews})</span>
                    <span>• {item.distance}</span>
                  </div>
                  
                  <div className="home-page__result-card-services">
                    {item.services.map(service => (
                      <span key={service}>{service}</span>
                    ))}
                  </div>
                  <div className="home-page__result-card-footer">
                    <span>{item.price}</span>
                    <button type="button">Перейти до бронювання</button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </main>

        <aside className="home-page__map">
          <div className="home-page__map-card">
            <div className="home-page__map-card-header">
              <div>
                <h3>Карта</h3>
                <p>OpenStreetMap</p>
              </div>
              <div className="home-page__map-card-status">Показано 3</div>
            </div>

            <div className="home-page__map-card-canvas">
              <MapContainer
                center={[50.4501, 30.5234]}
                zoom={12}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; OpenStreetMap contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <Marker position={[50.4501, 30.5234]}>
                  <Popup>Київ</Popup>
                </Marker>

                <Marker position={[50.4547, 30.5238]}>
                  <Popup>Локація 2</Popup>
                </Marker>

                <Marker position={[50.446, 30.515]}>
                  <Popup>Локація 3</Popup>
                </Marker>
              </MapContainer>
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
};
