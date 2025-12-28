"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ContactForm from "@/components/ContactForm";
import { useLanguage } from "@/contexts/LanguageContext";

interface FormData {
  nom: string;
  prenom: string;
  email: string;
  arrondissement: string;
  agdref: string;
  statut: string;
  message: string;
  captcha: boolean;
  acceptation: boolean;
}

import "../globals.css";
// import "./AccueilEtrangers.css"; // Fichier CSS supprimé temporairement pour le build

function AccueilEtrangersContent() {
  const { t } = useLanguage();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Récupérer le département depuis l'URL, valeur par défaut '78'
  const departement = searchParams.get('departement') || '78';

  const analyzeRequest = (formData: FormData) => {
    // Préparer les données pour l'API
    const today = new Date();
    const dateString = today.toLocaleDateString('fr-FR');

    const fieldValues = {
      numero_AGDREF: formData.agdref,
      date_demande: dateString,
      nom: formData.nom,
      prenom: formData.prenom,
      adresse_mail: formData.email,
      statut: formData.statut,
      arrondissement: formData.arrondissement,
      message: formData.message,
      departement: departement,
      captcha: formData.captcha,
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
      <Header departement={departement} />
      <main role="main" id="content">
        <div className="fr-container">
          {/* Fil d'Ariane */}
          {/* <nav role="navigation" className="fr-breadcrumb" aria-label="vous êtes ici :">
            <button className="fr-breadcrumb__button" aria-expanded="false" aria-controls="breadcrumb-1">
              {t('accueil.breadcrumb.show')}
            </button>
            <div className="fr-collapse" id="breadcrumb-1">
              <ol className="fr-breadcrumb__list">
                <li>
                  <Link className="fr-breadcrumb__link" href="/">{t('accueil.breadcrumb.home')}</Link>
                </li>
                <li>
                  <a className="fr-breadcrumb__link" aria-current="page">{t('accueil.breadcrumb.current')}</a>
                </li>
              </ol>
            </div>
          </nav> */}
          <div className="fr-mt-1w fr-grid-row fr-grid-row--gutters">
            <div className="fr-col-12">
              <h1 className="fr-h1">{t('accueil.title')}</h1>

              <p>
                {t('accueil.intro.line1' + "." + departement)}
                <br />
                {t('accueil.intro.line2')}
                <br />
                {t('accueil.intro.line3')}
              </p>

              <p>
                {t('accueil.intro.aiProcessing' + "." + departement)}
              </p>

              <div className="fr-alert fr-alert--info fr-mb-4w">
                <p className="fr-alert__title">{t('accueil.alert.info.title')}</p>
                <p>
                  <strong>{t('accueil.alert.info.message')}</strong>
                  <br />
                  {t('accueil.alert.info.processingTime' + "." + departement)}
                </p>
              </div>

              <div className="fr-alert fr-alert--warning fr-mb-4w">
                <p>
                  <strong>{t('accueil.alert.warning.' + departement)}</strong>
                </p>
              </div>
            </div>
          </div>

          {/* Contenu principal avec formulaire et sidebar */}
          <div className="fr-grid-row fr-grid-row--gutters fr-mb-6w">
            {/* Formulaire principal */}
            <div className="fr-col-12 fr-col-md-8">
              <ContactForm onSubmit={analyzeRequest} isLoading={false} departement={departement} />
            </div>

            {/* Sidebar informative */}
            <div className="fr-col-12 fr-col-md-4">
              <nav className="fr-sidemenu fr-sidemenu--right fr-sidemenu--full-border" role="navigation" aria-label="secondaire">
                <div className="fr-sidemenu__inner">
                  <button className="fr-sidemenu__btn" aria-controls="fr-sidemenu-wrapper-right" aria-expanded="false" suppressHydrationWarning>
                    {t('accueil.sidebar.title')}
                  </button>
                  <div className="fr-collapse fr-px-1w" id="fr-sidemenu-wrapper-right" suppressHydrationWarning>

                    {/* Sites officiels */}
                    <div className="fr-card fr-enlarge-link fr-card--grey fr-card--no-border fr-mt-3w">
                      <div className="fr-card__body">
                        <div className="fr-card__content">
                          <h2 className="fr-card__title">
                            {t('accueil.sidebar.sites.title')}
                          </h2>
                          <p className="fr-card__desc">
                            {t('accueil.sidebar.sites.desc')}
                          </p>
                          <div className="fr-card__end">
                            <a className="fr-link fr-link--icon-right fr-icon-external-link-line fr-mb-1w"
                              href="https://www.service-public.fr"
                              target="_blank"
                              title={t('accueil.sidebar.sites.servicePublic.title')}>
                              {t('accueil.sidebar.sites.servicePublic')}
                            </a>
                            <a className="fr-link fr-link--icon-right fr-icon-external-link-line fr-mb-1w"
                              href="https://www.demarches.interieur.gouv.fr"
                              target="_blank"
                              title={t('accueil.sidebar.sites.demarches.title')}>
                              {t('accueil.sidebar.sites.demarches')}
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
                            {t('accueil.sidebar.anef.title')}
                          </h2>
                          <p className="fr-card__desc">
                            {t('accueil.sidebar.anef.desc')}
                          </p>
                          <div className="fr-card__end">
                            <a className="fr-link fr-link--icon-right fr-icon-external-link-line fr-mb-3w"
                              href="https://administration-etrangers-en-france.interieur.gouv.fr/particuliers/#/"
                              target="_blank"
                              title={t('accueil.sidebar.anef.linkTitle')}>
                              {t('accueil.sidebar.anef.link')}
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
      <Footer departement={departement} />
    </>
  );
}

export default function AccueilEtrangers() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AccueilEtrangersContent />
    </Suspense>
  );
}
