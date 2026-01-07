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
      <Header departement="" />

      <main role="main" style={{
        minHeight: 'calc(100vh - 180px)', // Ajuster selon la hauteur du header/footer
        display: 'flex',
        alignItems: 'center'
      }}>
        <div className="fr-container" id="main">
          {/* Lien vers les départements */}
          <section id="demarches-test" className="fr-mt-4w">
            <h2 className="fr-h2 fr-mb-4w">{t('home.title.test')}</h2>
            <div id="bloc-demarches" className="fr-grid-row fr-grid-row--gutters" style={{ display: 'flex', flexWrap: 'wrap' }}>
              <div className="fr-col-6 fr-col-md-4 fr-col-lg" style={{ flex: '1 1 20%' }}>
                <div className="fr-tile fr-enlarge-link">
                  <div className="fr-tile__body">
                    <div className="fr-tile__content">
                      <h3 className="fr-tile__title">
                        <Link
                          className="fr-tile__link"
                          href="/accueil-etrangers?departement=78&mode=test"
                          title={t('home.prefecture.test.78')}
                          onClick={handleAccueilEtrangersClick}
                        >
                          {t('home.prefecture.test.78')}
                        </Link>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/78.png" className="fr-responsive-img" alt="78" suppressHydrationWarning />
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
                          href="/accueil-etrangers?departement=92&mode=test"
                          title={t('home.prefecture.test.92')}
                          onClick={handleAccueilEtrangersClick}
                        >
                          {t('home.prefecture.test.92')}
                        </Link>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/92.png" className="fr-responsive-img" alt="92" suppressHydrationWarning />
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
                          href="/accueil-etrangers?departement=91&mode=test"
                          title={t('home.prefecture.test.91')}
                          onClick={handleAccueilEtrangersClick}
                        >
                          {t('home.prefecture.test.91')}
                        </Link>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/91.png" className="fr-responsive-img" alt="91" suppressHydrationWarning />
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
                          href="/accueil-etrangers?departement=94&mode=test"
                          title={t('home.prefecture.test.94')}
                          onClick={handleAccueilEtrangersClick}
                        >
                          {t('home.prefecture.test.94')}
                        </Link>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/94.png" className="fr-responsive-img" alt="94" suppressHydrationWarning />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section de DELPHES en production */}
          <section id="demarches-production" className="fr-mt-4w">
            <h2 className="fr-h2 fr-mb-4w">{t('home.title.production')}</h2>
            <div id="bloc-demarches" className="fr-grid-row fr-grid-row--gutters" style={{ display: 'flex', flexWrap: 'wrap' }}>
              <div className="fr-col-6 fr-col-md-4 fr-col-lg" style={{ flex: '1 1 20%' }}>
                <div className="fr-tile fr-enlarge-link">
                  <div className="fr-tile__body">
                    <div className="fr-tile__content">
                      <h3 className="fr-tile__title">
                        <Link
                          className="fr-tile__link"
                          href="/accueil-etrangers?departement=78"
                          title={t('home.prefecture.production.78')}
                          onClick={handleAccueilEtrangersClick}
                        >
                          {t('home.prefecture.production.78')}
                        </Link>
                      </h3>
                    </div>
                  </div>
                  <div className="fr-tile__header">
                    <div className="fr-tile__pictogram">
                      <img src="/images/78.png" className="fr-responsive-img" alt="78" suppressHydrationWarning />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main >

      <Footer displayWatson={true} />
    </>
  );
}
