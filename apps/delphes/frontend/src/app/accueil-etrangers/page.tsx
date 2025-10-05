"use client";

import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ContactForm from "@/components/ContactForm";

interface FormData {
  nom: string;
  prenom: string;
  email: string;
  arrondissement: string;
  agdref: string;
  message: string;
  acceptation: boolean;
}

import "../globals.css";
// import "./AccueilEtrangers.css"; // Fichier CSS supprimé temporairement pour le build

export default function AccueilEtrangers() {
  const router = useRouter();

  const analyzeRequest = (formData: FormData) => {
    // Préparer les données pour l'API
    const today = new Date();
    const dateString = today.toLocaleDateString('fr-FR');

    const fieldValues = {
      date_demande: dateString,
      departement: '78',
      nom: formData.nom,
      prenom: formData.prenom,
      adresse_mail: formData.email,
      arrondissement: formData.arrondissement,
      agdref: formData.agdref,
      message: formData.message,
    };

    // Stocker les résultats pour la page de confirmation
    localStorage.setItem('accueilEtrangers', JSON.stringify({
      fieldValues: fieldValues,
    }));

    // Rediriger vers la page de l'analyse
    router.push('/analysis');
  };

  return (
    <>
      <Header />
      <main role="main" id="content">
        <div className="fr-container">
          {/* Fil d'Ariane */}
          <nav role="navigation" className="fr-breadcrumb" aria-label="vous êtes ici :">
            <button className="fr-breadcrumb__button" aria-expanded="false" aria-controls="breadcrumb-1">
              Voir le fil d'Ariane
            </button>
            <div className="fr-collapse" id="breadcrumb-1">
              <ol className="fr-breadcrumb__list">
                <li>
                  <a className="fr-breadcrumb__link" href="/">Accueil</a>
                </li>
                <li>
                  <a className="fr-breadcrumb__link" aria-current="page">Accueil des étrangers</a>
                </li>
              </ol>
            </div>
          </nav>
          <div className="fr-grid-row fr-grid-row--gutters">
            <div className="fr-col-12">
              <h1 className="fr-h1">Accueil des étrangers</h1>

              <p>
                Vous souhaitez contacter les services d'accueil des étrangers dans le département des Yvelines.
                <br />
                Nous vous invitons à utiliser le formulaire ci-dessous.
                <br />
                Nos services mettront tout en œuvre pour vous répondre dans les meilleurs délais.
              </p>

              <div className="fr-alert fr-alert--info fr-mb-4w">
                <p className="fr-alert__title">Information importante</p>
                <p>
                  <strong>Pour toute information concernant le suivi de votre demande de titre de séjour, indiquez impérativement votre numéro étranger/AGDREF (à 10 chiffres) si vous en avez un.</strong>
                </p>
              </div>

              <div className="fr-alert fr-alert--warning fr-mb-4w">
                <p>
                  <strong>Les données personnelles recueillies par le formulaire de prise de contact ne sont pas conservées par la préfecture des Yvelines.</strong>
                </p>
              </div>
            </div>
          </div>

          {/* Contenu principal avec formulaire et sidebar */}
          <div className="fr-grid-row fr-grid-row--gutters fr-mb-6w">
            {/* Formulaire principal */}
            <div className="fr-col-12 fr-col-md-8">
              <ContactForm onSubmit={analyzeRequest} isLoading={false} />
            </div>

            {/* Sidebar informative */}
            <div className="fr-col-12 fr-col-md-4">
              <nav className="fr-sidemenu fr-sidemenu--right fr-sidemenu--full-border" role="navigation" aria-label="secondaire">
                <div className="fr-sidemenu__inner">
                  <button className="fr-sidemenu__btn" aria-controls="fr-sidemenu-wrapper-right" aria-expanded="false">
                    En complément
                  </button>
                  <div className="fr-collapse fr-px-1w" id="fr-sidemenu-wrapper-right">

                    {/* Sites officiels */}
                    <div className="fr-card fr-enlarge-link fr-card--grey fr-card--no-border fr-mt-3w">
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h2 className="fr-card__title">
                            Sites officiels pour vos démarches
                          </h2>
                          <p className="fr-card__desc">
                            Accédez directement aux sites officiels de l'administration française.
                          </p>
                          <div className="fr-card__end">
                            <a className="fr-link fr-link--icon-right fr-icon-external-link-line fr-mb-1w"
                              href="https://www.service-public.fr"
                              target="_blank"
                              title="Accéder à service-public.fr - Nouvelle fenêtre">
                              service-public.fr
                            </a>
                            <a className="fr-link fr-link--icon-right fr-icon-external-link-line fr-mb-1w"
                              href="https://www.demarches.interieur.gouv.fr"
                              target="_blank"
                              title="Accéder aux démarches du Ministère de l'Intérieur - Nouvelle fenêtre">
                              Démarches du Ministère de l'Intérieur
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Site de l'ANEF */}
                    <div className="fr-card fr-enlarge-link fr-card--grey fr-card--no-border fr-mt-3w">
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h2 className="fr-card__title">
                            ANEF
                          </h2>
                          <p className="fr-card__desc">
                            L’administration numérique pour les étrangers en France (ANEF) a pour objectif de
                            dématérialiser les démarches concernant le séjour des étrangers en France.
                          </p>
                          <div className="fr-card__end">
                            <a className="fr-link fr-link--icon-right fr-icon-external-link-line fr-mb-3w"
                              href="https://administration-etrangers-en-france.interieur.gouv.fr/particuliers/#/"
                              target="_blank"
                              title="Accéder à l'ANEF - Nouvelle fenêtre">
                              Accédez à la plateforme
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Les services de l'État */}
                    <div className="fr-card fr-enlarge-link fr-card--grey fr-card--no-border fr-mt-3w">
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h2 className="fr-card__title">
                            Les services de l'État
                          </h2>
                          <p className="fr-card__desc">
                            Vous pouvez saisir l'administration par voie électronique en adressant en ligne vos demandes d'information ou envoyer un dossier lié à une démarche administrative.
                          </p>
                          <div className="fr-card__end">
                            <a className="fr-link fr-link--icon-right fr-icon-external-link-line fr-mb-3w"
                              href="https://contacts-demarches.interieur.gouv.fr/"
                              target="_blank"
                              title="Accéder à la plateforme les services de l'état https://contacts-demarches.interieur.gouv.fr/ - Nouvelle fenêtre">
                              Accédez à la plateforme
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </nav>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
