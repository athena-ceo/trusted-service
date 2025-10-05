"use client";

import Link from "next/link";

export default function Header() {
    return (
        <header role="banner" className="fr-header">
            <div className="fr-header__body">
                <div className="fr-container">
                    <div className="fr-header__body-row">
                        <div className="fr-header__brand fr-enlarge-link">
                            <div className="fr-header__brand-top">
                                <div className="fr-header__logo">
                                    <p className="fr-logo">
                                        préfet<br />des Yvelines
                                    </p>
                                </div>
                                <div className="fr-header__navbar">
                                    <button className="fr-btn--search fr-btn"
                                        aria-controls="modal-372"
                                        id="button-373"
                                        title="Rechercher">
                                        Rechercher
                                    </button>
                                    <button className="fr-btn--menu fr-btn"
                                        aria-controls="modal-398"
                                        aria-haspopup="menu"
                                        id="button-399"
                                        title="Menu">
                                        Menu
                                    </button>
                                </div>
                            </div>
                            <div className="fr-header__service">
                                <Link href="/" title="Accueil - Les services de l&apos;État dans les Yvelines">
                                    <p className="fr-header__service-title">
                                        Les services de l&apos;État dans les Yvelines
                                    </p>
                                </Link>
                                <p className="fr-header__service-tagline">
                                    Portail de l&apos;État en Yvelines
                                </p>
                            </div>
                        </div>
                        <div className="fr-header__tools">
                            <div className="fr-header__tools-links">
                                <ul className="fr-btns-group">
                                    <li className="contact-li">
                                        <a className="fr-btn fr-icon-mail-line" href="/accueil-etrangers" title="Nous contacter - formulaire de contact">
                                            Nous contacter
                                        </a>
                                    </li>
                                    <li>
                                        <button className="fr-btn fr-icon-theme-fill fr-link--icon-left"
                                            aria-controls="fr-theme-modal">
                                            Paramètres d&apos;affichage
                                        </button>
                                    </li>
                                </ul>
                            </div>
                            <div className="fr-header__search fr-modal"
                                id="modal-372"
                                aria-labelledby="button-373">
                                <div className="fr-container fr-container-lg--fluid">
                                    <button className="fr-link--close fr-link"
                                        aria-controls="modal-372">
                                        Fermer
                                    </button>
                                    <form className="search-container loupe autocomplete" role="search">
                                        <div className="fr-search-bar"
                                            id="search-371"
                                            role="search">
                                            <label className="fr-label" htmlFor="search-371-input">Rechercher</label>
                                            <input className="fr-input searchh autocomplete"
                                                placeholder="Rechercher"
                                                type="search"
                                                id="search-371-input"
                                                name="SearchText"
                                                required />
                                            <button className="fr-btn"
                                                title="Rechercher">
                                                Rechercher
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="fr-header__menu fr-modal"
                id="modal-398"
                aria-labelledby="button-399">
                <div className="fr-container">
                    <button className="fr-btn fr-btn--close"
                        aria-controls="modal-398"
                        title="Fermer Menu">
                        Fermer Menu
                    </button>
                    <div className="fr-header__menu-links">
                        <ul className="fr-btns-group">
                            <li className="contact-li">
                                <a className="fr-btn fr-icon-mail-line" href="/accueil-etrangers" title="Nous contacter - formulaire de contact">
                                    Nous contacter
                                </a>
                            </li>
                            <li>
                                <button className="fr-btn fr-icon-theme-fill fr-link--icon-left" aria-controls="fr-theme-modal">
                                    Paramètres d&apos;affichage
                                </button>
                            </li>
                        </ul>
                    </div>
                    <nav className="fr-nav" id="nav-main" role="navigation" aria-label="Menu principal">
                        <ul className="fr-nav__list">
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-actualites">
                                    Actualités
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-actualites">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-actualites">
                                                    Fermer - Actualités
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">Actualités</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Actualites">
                                                        Voir toute la rubrique
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-actions">
                                    Actions de l&apos;Etat
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-actions">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-actions">
                                                    Fermer - Actions de l&apos;Etat
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">Actions de l&apos;Etat</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Actions-de-l-Etat">
                                                        Voir toute la rubrique
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-services">
                                    Services de l&apos;État
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-services">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-services">
                                                    Fermer - Services de l&apos;État
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">Services de l&apos;État</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Services-de-l-Etat">
                                                        Voir toute la rubrique
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-publications">
                                    Publications
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-publications">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-publications">
                                                    Fermer - Publications
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">Publications</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Publications">
                                                        Voir toute la rubrique
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-demarches">
                                    Démarches
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-demarches">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-demarches">
                                                    Fermer - Démarches
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">Démarches</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Demarches">
                                                        Voir toute la rubrique
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </nav>
                </div>
            </div>
        </header>
    );
}