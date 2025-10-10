"use client";

import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function Accueil() {
  return (
    <>
      <Header />

      <main role="main">
        {/* Bandeau d'information */}
        <div className="fr-notice fr-notice--info">
          <div className="fr-container">
            <div className="fr-notice__body">
              <p className="fr-notice__title">
                Information importante :
                <span className="fr-text--medium"> Nouveau service d'accueil des étrangers avec assistance intelligente disponible</span>
              </p>
            </div>
          </div>
        </div>

        <div className="fr-container" id="main">
          {/* Section Démarches en ligne */}
          <section id="demarches" className="fr-mt-4w">
            <h2 className="fr-h2 fr-mb-4w">Les démarches en ligne</h2>

            <div className="fr-grid-row fr-grid-row--right fr-mb-4v">
              <div className="fr-col-12 fr-col-md-4 fr-col-xl-3">
                <a className="fr-link fr-link--icon-right fr-icon-arrow-right-line" href="https://www.yvelines.gouv.fr/Outils/Horaires-et-coordonnees/Horaires-et-coordonnees">
                  Horaires et lieux d'accueil
                </a>
              </div>
              <div className="fr-col-12 fr-col-md-3 fr-col-xl-2">
                <a className="fr-link fr-link--icon-right fr-icon-arrow-right-line" href="#">
                  Toutes les démarches
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
                          Carte grise
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
                          Permis de conduire
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
                          Carte d'identité
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
                          Passeport
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
                        <Link className="fr-tile__link" href="/accueil-etrangers" title="Accueil des étrangers">
                          Accueil des étrangers
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
              <section aria-label="Consultez nos actualités">
                <div className="fr-grid-row fr-mb-4w">
                  <div className="fr-col-12 fr-col-md-7">
                    <h2 className="fr-h2">Actualités</h2>
                  </div>
                  <div className="fr-col-12 fr-col-md-5 fr-col--middle" style={{ textAlign: 'right' }}>
                    <a className="fr-link fr-link--icon-right fr-icon-arrow-right-line" href="#">
                      Toutes les actualités
                    </a>
                  </div>
                </div>

                {/* Actualité principale avec image */}
                <div className="fr-grid-row fr-mb-4w">
                  <div className="fr-col-12">
                    <div className="fr-card fr-card--horizontal fr-enlarge-link">
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h3 className="fr-card__title">
                            <a href="#">
                              Les Yvelines lancent leur premier Comité d'action économique locale
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">Publié le 22/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              Lire la suite
                            </a>
                          </div>
                        </div>
                      </div>
                      <div className="fr-card__header">
                        <div className="fr-card__img">
                          <img
                            src="/images/actualites/comite-action-economique.png"
                            alt="Lancement du Comité d'action économique locale"
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
                            alt="Se préparer aux risques majeurs : les Yvelines en situation d'entraînement"
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
                              Se préparer aux risques majeurs : les Yvelines en (...)
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">Publié le 29/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              Lire la suite
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
                            alt="Une permanence pour les victimes d'actes LGBTQIA+"
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
                              Une permanence pour les victimes d'actes LGBTQIA+ (...)
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">Publié le 23/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              Lire la suite
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
                              La COP25 et les actions territoriales :
                            </div>
                            <div style={{
                              fontSize: '10px',
                              textAlign: 'center',
                              lineHeight: '1.3'
                            }}>
                              de l'engagement global à la mobilisation locale
                            </div>
                            <div style={{
                              fontSize: '9px',
                              textAlign: 'center',
                              marginTop: '5px',
                              fontStyle: 'italic'
                            }}>
                              dans les Yvelines
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
                              COP25 : de l'engagement global à la mobilisation (...)
                            </a>
                          </h3>
                          <div className="fr-card__end">
                            <p className="fr-card__detail">Publié le 19/09/2025</p>
                            <a href="#" className="fr-link fr-link--icon-right fr-icon-arrow-right-line">
                              Lire la suite
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
                  <h2 className="fr-h4 fr-mb-2w fr-ml-md-2w">Vous accompagner</h2>
                </div>
              </div>
              <div className="fr-grid-row fr-grid-row--gutters fr-ml-md-4w">
                <div className="fr-col-12">
                  <div className="fr-tile fr-tile--grey fr-enlarge-link">
                    <div className="fr-tile__body">
                      <div className="fr-tile__content">
                        <h3 className="fr-tile__title">
                          <Link className="fr-tile__link" href="/accueil-etrangers">
                            Accueil des étrangers dans les Yvelines
                          </Link>
                        </h3>
                        <p className="fr-tile__desc">
                          Nouveau service intelligent avec assistance IA pour faciliter vos démarches
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
                            Horaires - coordonnées et accessibilité
                          </a>
                        </h3>
                        <p className="fr-tile__desc">
                          Préfecture et Sous-Préfectures des Yvelines
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
                            Foire aux questions
                          </a>
                        </h3>
                        <p className="fr-tile__desc">
                          Trouvez rapidement des réponses à vos questions
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
                      <h2 className="fr-h5 fr-follow__title">Abonnez-vous à notre lettre d'information</h2>
                      <p className="fr-text--sm fr-follow__desc">
                        Restez informé des dernières actualités et nouveautés des services de l'État dans les Yvelines
                      </p>
                    </div>
                    <div>
                      <ul className="fr-btns-group fr-btns-group--inline-md">
                        <li>
                          <a className="fr-btn fr-btn--secondary" href="#">
                            S'abonner
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="fr-col-12 fr-col-md-4">
                  <div className="fr-follow__social">
                    <h2 className="fr-h5 fr-mb-3v">
                      Suivez-nous<br /> sur les réseaux sociaux
                    </h2>
                    <ul className="fr-btns-group">
                      <li>
                        <a className="fr-btn--twitter fr-btn" href="#" title="Twitter - nouvelle fenêtre">
                          Twitter
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
