"use client";

import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Accueil() {
  const { t } = useLanguage();

  // Fonction appelée lors du clic sur le lien "Accueil des étrangers"
  const handleAccueilEtrangersClick = () => {
    console.log('Nettoyage du localStorage à l\'accueil');
    // Vider le localStorage
    localStorage.removeItem('analyzeResult');
    localStorage.removeItem('selectedIntention');
    localStorage.removeItem('intentionLabel');
    localStorage.removeItem('fieldValues');
    localStorage.removeItem('accueilEtrangers');
    localStorage.removeItem('status');
  };

  return (
    <>
      <Header />

      <main role="main">
        {/* Bandeau d'information */}
        <div className="fr-notice fr-notice--info">
          <div className="fr-container">
            <div className="fr-notice__body">
              <p className="fr-notice__title">
                {t('home.banner.title')} :
                <span className="fr-text--medium"> {t('home.banner.message')}</span>
              </p>
            </div>
          </div>
        </div>

        <div className="fr-container" id="main">
          {/* Section Démarches en ligne */}
          <section id="demarches" className="fr-mt-4w">
            <h2 className="fr-h2 fr-mb-4w">{t('home.procedures.title')}</h2>

            <div className="fr-grid-row fr-grid-row--right fr-mb-4v">
              <div className="fr-col-12 fr-col-md-4 fr-col-xl-3">
                <a className="fr-link fr-link--icon-right fr-icon-arrow-right-line" href="https://www.yvelines.gouv.fr/Outils/Horaires-et-coordonnees/Horaires-et-coordonnees">
                  {t('home.procedures.hours')}
                </a>
              </div>
              <div className="fr-col-12 fr-col-md-3 fr-col-xl-2">
                <a className="fr-link fr-link--icon-right fr-icon-arrow-right-line" href="#">
                  {t('home.procedures.all')}
                </a>
              </div>
            </div>

            {/* Tuiles des démarches principales */}
            <div id="bloc-demarches" className="fr-grid-row fr-grid-row--gutters" style={{ display: 'flex', flexWrap: 'wrap' }}>
              <div className="fr-col-6 fr-col-md-4 fr-col-lg" style={{ flex: '1 1 20%' }}>
                <div className="fr-tile fr-enlarge-link">
                  <div className="fr-tile__body">
                    <div className="fr-tile__content">
                      <h3 className="fr-tile__title">
                        <a className="fr-tile__link" href="#">
                          {t('home.procedures.carteGrise')}
                        </a>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/carte_grise.svg" className="fr-responsive-img" alt="" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="fr-col-6 fr-col-md-4 fr-col-lg" style={{ flex: '1 1 20%' }}>
                <div className="fr-tile fr-enlarge-link">
                  <div className="fr-tile__body">
                    <div className="fr-tile__content">
                      <h3 className="fr-tile__title">
                        <a className="fr-tile__link" href="#">
                          {t('home.procedures.permis')}
                        </a>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/permis_de_conduire.svg" className="fr-responsive-img" alt="" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="fr-col-6 fr-col-md-4 fr-col-lg" style={{ flex: '1 1 20%' }}>
                <div className="fr-tile fr-enlarge-link">
                  <div className="fr-tile__body">
                    <div className="fr-tile__content">
                      <h3 className="fr-tile__title">
                        <a className="fr-tile__link" href="#">
                          {t('home.procedures.carteId')}
                        </a>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/carte_identite.svg" className="fr-responsive-img" alt="" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="fr-col-6 fr-col-md-4 fr-col-lg" style={{ flex: '1 1 20%' }}>
                <div className="fr-tile fr-enlarge-link">
                  <div className="fr-tile__body">
                    <div className="fr-tile__content">
                      <h3 className="fr-tile__title">
                        <a className="fr-tile__link" href="#">
                          {t('home.procedures.passeport')}
                        </a>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/passeport.svg" className="fr-responsive-img" alt="" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="fr-col-6 fr-col-md-4 fr-col-lg" style={{ flex: '1 1 20%' }}>
                <div className="fr-tile fr-enlarge-link">
                  <div className="fr-tile__body">
                    <div className="fr-tile__content">
                      <h3 className="fr-tile__title">
                        <Link
                          className="fr-tile__link"
                          href="/accueil-etrangers"
                          title={t('home.procedures.etrangers')}
                          onClick={handleAccueilEtrangersClick}
                        >
                          {t('home.procedures.etrangers')}
                        </Link>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/accueil-etrangers.svg" className="fr-responsive-img" alt="" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section principale avec actualités et accompagnement */}
          <div className="fr-grid-row fr-grid-row--gutters fr-mt-10w">
            <div className="fr-col-12 fr-col-lg-8">
              <section aria-label={t('home.news.ariaLabel')}>
                {/* Actualité principale avec image */}
                <div className="fr-grid-row fr-mb-4w">
                  <div className="fr-col-12">
                    <div className="fr-card fr-card--horizontal fr-enlarge-link">
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h3 className="fr-card__title">
                            <a href="#">
                              {t('home.news.article1.title')}
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">{t('home.news.published')} 22/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              {t('home.news.readMore')}
                            </a>
                          </div>
                        </div>
                      </div>
                      <div className="fr-card__header">
                        <div className="fr-card__img">
                          <img
                            src="/images/actualites/comite-action-economique.png"
                            alt={t('home.news.article1.title')}
                            style={{
                              width: '100%',
                              height: '200px',
                              objectFit: 'cover'
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Grille des 3 actualités secondaires */}
                <div className="fr-grid-row fr-grid-row--gutters">
                  <div className="fr-col-12 fr-col-md-4">
                    <div className="fr-card fr-enlarge-link">
                      <div className="fr-card__header">
                        <div className="fr-card__img">
                          <img
                            src="/images/actualites/risques-majeurs.jpg"
                            alt={t('home.news.article2.title')}
                            style={{
                              width: '100%',
                              height: '120px',
                              objectFit: 'cover'
                            }}
                          />
                        </div>
                      </div>
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h3 className="fr-card__title">
                            <a href="#">
                              {t('home.news.article2.title')}
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">{t('home.news.published')} 29/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              {t('home.news.readMore')}
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="fr-col-12 fr-col-md-4">
                    <div className="fr-card fr-enlarge-link">
                      <div className="fr-card__header">
                        <div className="fr-card__img">
                          <img
                            src="/images/actualites/lgbtqia-permanence.png"
                            alt={t('home.news.article3.title')}
                            style={{
                              width: '100%',
                              height: '120px',
                              objectFit: 'cover'
                            }}
                          />
                        </div>
                      </div>
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h3 className="fr-card__title">
                            <a href="#">
                              {t('home.news.article3.title')}
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">{t('home.news.published')} 23/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              {t('home.news.readMore')}
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="fr-col-12 fr-col-md-4">
                    <div className="fr-card fr-enlarge-link">
                      <div className="fr-card__header">
                        <div className="fr-card__img">
                          <div style={{
                            width: '100%',
                            height: '120px',
                            background: 'linear-gradient(135deg, #1e7fcb 0%, #0052cc 100%)',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            position: 'relative',
                            padding: '10px'
                          }}>
                            <div style={{
                              fontSize: '11px',
                              fontWeight: 'bold',
                              textAlign: 'center',
                              lineHeight: '1.2',
                              marginBottom: '5px'
                            }}>
                              {t('home.news.article4.line1')}
                            </div>
                            <div style={{
                              fontSize: '10px',
                              textAlign: 'center',
                              lineHeight: '1.3'
                            }}>
                              {t('home.news.article4.line2')}
                            </div>
                            <div style={{
                              fontSize: '9px',
                              textAlign: 'center',
                              marginTop: '5px',
                              fontStyle: 'italic'
                            }}>
                              {t('home.news.article4.line3')}
                            </div>
                            <div style={{
                              position: 'absolute',
                              bottom: '5px',
                              right: '8px',
                              width: '30px',
                              height: '15px',
                              background: 'rgba(255,255,255,0.2)',
                              borderRadius: '2px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '8px',
                              fontWeight: 'bold'
                            }}>
                              COP25
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h3 className="fr-card__title">
                            <a href="#">
                              {t('home.news.article4.title')}
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">{t('home.news.published')} 19/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              {t('home.news.readMore')}
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>

            {/* Sidebar Vous accompagner */}
            <div className="fr-col-12 fr-col-lg-4">
              <div className="fr-grid-row fr-ml-md-4w fr-mt-1v">
                <div className="fr-col-12 fr-mt-3v">
                  <h2 className="fr-h4 fr-mb-2w fr-ml-md-2w">{t('home.sidebar.title')}</h2>
                </div>
              </div>
              <div className="fr-grid-row fr-grid-row--gutters fr-ml-md-4w">
                <div className="fr-col-12">
                  <div className="fr-tile fr-tile--grey fr-enlarge-link">
                    <div className="fr-tile__body">
                      <div className="fr-tile__content">
                        <h3 className="fr-tile__title">
                          <Link className="fr-tile__link" href="/accueil-etrangers">
                            {t('home.sidebar.reception.title')}
                          </Link>
                        </h3>
                        <p className="fr-tile__desc">
                          {t('home.sidebar.reception.desc')}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="fr-col-12">
                  <div className="fr-tile fr-tile--grey fr-enlarge-link">
                    <div className="fr-tile__body">
                      <div className="fr-tile__content">
                        <h3 className="fr-tile__title">
                          <a className="fr-tile__link" href="#">
                            {t('home.sidebar.hours.title')}
                          </a>
                        </h3>
                        <p className="fr-tile__desc">
                          {t('home.sidebar.hours.desc')}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="fr-col-12">
                  <div className="fr-tile fr-tile--grey fr-enlarge-link">
                    <div className="fr-tile__body">
                      <div className="fr-tile__content">
                        <h3 className="fr-tile__title">
                          <a className="fr-tile__link" href="#">
                            {t('home.sidebar.faq.title')}
                          </a>
                        </h3>
                        <p className="fr-tile__desc">
                          {t('home.sidebar.faq.desc')}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Section Newsletter */}
          <div className="fr-follow fr-mt-10w">
            <div className="fr-container">
              <div className="fr-grid-row">
                <div className="fr-col-12 fr-col-md-8">
                  <div className="fr-follow__newsletter">
                    <div>
                      <h2 className="fr-h5 fr-follow__title">{t('home.newsletter.title')}</h2>
                      <p className="fr-text--sm fr-follow__desc">
                        {t('home.newsletter.desc')}
                      </p>
                    </div>
                    <div>
                      <ul className="fr-btns-group fr-btns-group--inline-md">
                        <li>
                          <a className="fr-btn fr-btn--secondary" href="#">
                            {t('home.newsletter.subscribe')}
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="fr-col-12 fr-col-md-4">
                  <div className="fr-follow__social">
                    <h2 className="fr-h5 fr-mb-3v">
                      {t('home.social.title')}<br /> {t('home.social.subtitle')}
                    </h2>
                    <ul className="fr-btns-group">
                      <li>
                        <a className="fr-btn--twitter fr-btn" href="#" title={t('home.social.twitter.title')}>
                          {t('home.social.twitter')}
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main >

      <Footer displayWatson={true} />
    </>
  );
}
