import './HomePage.scss';

export const HomePage = () => {
  return (
    <div className="home-page">
      <h1 className="visually-hidden">Home</h1>

      <section className="hero">
        <div className="hero__content">
          <p className="hero__eyebrow">Book beauty & wellness</p>
          <h2 className="hero__title">
            Your beauty.
            <span className="hero__title--accent"> Your time.</span>
          </h2>
          <p className="hero__subtitle">
            Discover top salons, specialists and services near you and book in
            minutes.
          </p>

          <div className="search-bar">
            <input
              className="search-bar__input"
              placeholder="Search salons, specialists or services"
            />
            <input
              className="search-bar__input"
              placeholder="Location — New York, NY"
            />
            <button className="search-bar__btn">Search</button>
          </div>
        </div>

        <div className="hero__visual">
          <div className="hero__visual--placeholder">
            Hero image (you will replace)
          </div>
        </div>
      </section>

      <section className="categories">
        <div className="categories__header">
          <h3>Popular categories</h3>
          <a className="categories__viewall">View all</a>
        </div>

        <div className="categories__list">
          {['Hair', 'Nails', 'Skin', 'Makeup', 'Massage', 'Spa'].map(cat => (
            <div key={cat} className="category-card">
              <div className="category-card__icon">{cat.charAt(0)}</div>
              <div className="category-card__name">{cat}</div>
              <div className="category-card__meta">123 salons</div>
            </div>
          ))}
        </div>
      </section>

      <section className="how-it-works">
        <h3>How it works</h3>
        <div className="how-it-works__steps">
          <div className="step">
            <div className="step__num">1</div>
            <div className="step__body">
              <strong>Find</strong>
              <div>Search for services or specialists</div>
            </div>
          </div>
          <div className="step">
            <div className="step__num">2</div>
            <div className="step__body">
              <strong>Book</strong>
              <div>Choose a time that works for you</div>
            </div>
          </div>
          <div className="step">
            <div className="step__num">3</div>
            <div className="step__body">
              <strong>Enjoy</strong>
              <div>Relax and enjoy your transformation</div>
            </div>
          </div>
        </div>
      </section>

      <section className="recommended">
        <div className="recommended__header">
          <h3>Recommended for you</h3>
          <a className="recommended__seeall">See all</a>
        </div>
        <div className="recommended__grid">
          {[1, 2, 3, 4].map(i => (
            <article key={i} className="card">
              <div className="card__media">Image {i}</div>
              <div className="card__body">
                <div className="card__title">Luxe Beauty Studio</div>
                <div className="card__meta">4.8 • 123 Madison Ave</div>
                <div className="card__tags">Hair • Nails • Makeup</div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
};
