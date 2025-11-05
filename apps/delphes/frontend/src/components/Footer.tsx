"use client";

import { Suspense, useEffect, useState } from "react";
import { useWatsonExpandButton } from "@/hooks/useWatsonExpandButton";
import { useWatsonOrchestrate } from "@/hooks/useWatsonOrchestrate";
import { useWatsonConfig } from "@/config/watson";
import { IbmWatsonxOrchestrate } from "@carbon/icons-react";
import Link from "next/link";
import { Button } from "@carbon/react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Footer({ departement = '', displayWatson = false }: { departement?: string, displayWatson?: boolean }) {
    const { t } = useLanguage();
    const [watsonEnabled, setWatsonEnabled] = useState(false);
    const [watsonActivated, setWatsonActivated] = useState(false);
    const [departementLabel, setDepartementLabel] = useState('');

    useEffect(() => {
        if (departement === '78') {
            setDepartementLabel('des Yvelines');
        } else if (departement === '91') {
            setDepartementLabel('de l\'Essonne');
        } else if (departement === '92') {
            setDepartementLabel('des Hauts de Seine');
        } else if (departement === '94') {
            setDepartementLabel('du Val de Marne');
        }
    }, [departement]);

    // Utilisation du hook pour créer le bouton d'expansion Watson
    const { createExpandButton, setupWatsonButtonObserver } = useWatsonExpandButton();

    // Configuration Watson à partir des variables d'environnement
    const watsonConfig = useWatsonConfig();

    // Utilisation du hook Watson Orchestrate
    useWatsonOrchestrate({
        enabled: watsonEnabled,
        orchestrationID: watsonConfig.orchestrationID,
        hostURL: watsonConfig.hostURL,
        agentId: watsonConfig.agentId,
        crn: watsonConfig.crn,
        onActivated: () => setWatsonActivated(true),
        onButtonSetup: () => setupWatsonButtonObserver(createExpandButton)
    });

    return (
        <footer className="fr-footer" role="contentinfo" id="footer">
            <div className="fr-footer__top">
                <div className="fr-container">
                    <div className="fr-grid-row fr-grid-row--start fr-grid-row--gutters">
                    </div>
                </div>
            </div>
            <div className="fr-container">
                <div className="fr-footer__body">
                    <div className="fr-footer__brand fr-enlarge-link">
                        <Link href="/" title={t('footer.home')}>
                            <p className="fr-logo">
                                préfet
                                <br />
                                {departementLabel}
                            </p>
                        </Link>
                    </div>
                    <div className="fr-footer__content">
                        <p className="fr-footer__content-desc">
                            {t('footer.description')}
                        </p>

                        <ul className="fr-footer__content-links">
                            <li className="fr-footer__content-item">
                                <a className="fr-footer__content-link" href="https://info.gouv.fr" target="_blank" rel="noopener noreferrer">
                                    info.gouv.fr
                                </a>
                            </li>
                            <li className="fr-footer__content-item">
                                <a className="fr-footer__content-link" href="https://service-public.fr" target="_blank" rel="noopener noreferrer">
                                    service-public.fr
                                </a>
                            </li>
                            <li className="fr-footer__content-item">
                                <a className="fr-footer__content-link" href="https://legifrance.gouv.fr" target="_blank" rel="noopener noreferrer">
                                    legifrance.gouv.fr
                                </a>
                            </li>
                            <li className="fr-footer__content-item">
                                <a className="fr-footer__content-link" href="https://data.gouv.fr" target="_blank">
                                    data.gouv.fr
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Container pour Watson Orchestrate */}
                <div id="watson-chat-container" style={watsonEnabled ? { display: 'block' } : { display: 'none' }} >
                    <div style={{ border: '1px solid #ddd', borderRadius: '8px', marginTop: '20px', textAlign: 'center', padding: '20px', color: '#666', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                        <IbmWatsonxOrchestrate size={20} />
                        Loading Delphes Advisor...
                    </div>
                </div>

                <div className="fr-footer__bottom">
                    <ul className="fr-footer__bottom-list">
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/plan-du-site">
                                {t('footer.sitemap')}
                            </a>
                        </li>
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href={`/accueil-etrangers${departement ? `?departement=${departement}` : ''}`}>
                                {t('footer.contact')}
                            </a>
                        </li>
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/accessibilite">
                                {t('footer.accessibility')}
                            </a>
                        </li>
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/mentions-legales">
                                Mentions légales
                            </a>
                        </li>
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/donnees-personnelles">
                                Données personnelles
                            </a>
                        </li>
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/gestion-des-cookies">
                                Gestion des cookies
                            </a>
                        </li>
                        {displayWatson && !watsonActivated && (
                            <li className="fr-footer__bottom-item">
                                <Button
                                    hasIconOnly
                                    isExpressive
                                    kind="ghost"
                                    renderIcon={() => <IbmWatsonxOrchestrate size={16} />}
                                    size="xs"
                                    tooltipAlignment="center"
                                    tooltipDropShadow
                                    tooltipHighContrast
                                    tooltipPosition="bottom"
                                    iconDescription="Delphes Advisor"
                                    title="Delphes Advisor"
                                    aria-label="Delphes Advisor"
                                    onClick={() => setWatsonEnabled(true)} />
                            </li>
                        )}
                    </ul>

                    <div className="fr-footer__bottom-copy">
                        <p>
                            {t('footer.license.text')}{" "}
                            <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md" target="_blank" rel="noopener noreferrer">
                                {t('footer.license.name')}
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
}
