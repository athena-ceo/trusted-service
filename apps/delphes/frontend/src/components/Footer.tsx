import Link from "next/link";

export default function Footer() {
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
                        <Link href="/" title="Retour à l&apos;accueil du site - Les services de l&apos;État dans les Yvelines">
                            <p className="fr-logo">
                                préfet<br />des Yvelines
                            </p>
                        </Link>
                    </div>
                    <div className="fr-footer__content">
                        <p className="fr-footer__content-desc">
                            Portail officiel des services de l&apos;État dans le département des Yvelines
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
                                <a className="fr-footer__content-link" href="https://data.gouv.fr" target="_blank" rel="noopener noreferrer">
                                    data.gouv.fr
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
                <div className="fr-footer__bottom">
                    <ul className="fr-footer__bottom-list">
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/plan-du-site">
                                Plan du site
                            </a>
                        </li>
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/accueil-etrangers">
                                Nous contacter
                            </a>
                        </li>
                        <li className="fr-footer__bottom-item">
                            <a className="fr-footer__bottom-link" href="/accessibilite">
                                Accessibilité : partiellement conforme
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
                    </ul>
                    <div className="fr-footer__bottom-copy">
                        <p>
                            Sauf mention contraire, tous les contenus de ce site sont sous{" "}
                            <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md" target="_blank" rel="noopener noreferrer">
                                licence etalab-2.0
                            </a>
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
}
