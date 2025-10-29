"use client";

import Link from "next/link";
import { useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Header() {
    const { currentLang, setLanguage, t } = useLanguage();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isMenuMobileOpen, setIsMenuMobileOpen] = useState(false);

    const handleLanguageChange = (lang: 'FR' | 'EN', isMobile: boolean = false) => {
        setLanguage(lang);
        if (isMobile) {
            setIsMenuMobileOpen(false);
        } else {
            setIsMenuOpen(false);
        }
    };

    const toggleMenu = (isMobile: boolean = false) => {
        if (isMobile) {
            setIsMenuMobileOpen(!isMenuMobileOpen);
        } else {
            setIsMenuOpen(!isMenuOpen);
        }
    };

    return (
        <header role="banner" className="fr-header" suppressHydrationWarning>
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
                                        title={t('header.search')}>
                                        {t('header.search')}
                                    </button>
                                    <button className="fr-btn--menu fr-btn"
                                        aria-controls="modal-398"
                                        aria-haspopup="menu"
                                        id="button-399"
                                        title={t('header.menu')}>
                                        {t('header.menu')}
                                    </button>
                                </div>
                            </div>
                            <div className="fr-header__service">
                                <Link href="/" title={t('service.home')}>
                                    <p className="fr-header__service-title">
                                        {t('service.title')}
                                    </p>
                                </Link>
                                <p className="fr-header__service-tagline">
                                    {t('service.tagline')}
                                </p>
                            </div>
                        </div>
                        <div className="fr-header__tools">
                            <div className="fr-header__tools-links">
                                <ul className="fr-btns-group">
                                    <li className="fr-translate fr-nav">
                                        <button aria-controls="translate-menu-desktop"
                                            title={t('header.language.select')}
                                            aria-expanded={isMenuOpen}
                                            className="fr-btn fr-icon-translate-2 fr-btn--tertiary-no-outline fr-translate fr-nav language-select"
                                            id="fr-header-with-horizontal-operator-logo-quick-access-item-2"
                                            onClick={() => toggleMenu(false)}
                                            data-fr-js-collapse-button="true" data-fr-js-navigation="true">
                                            <div>
                                                <span className="short-label">{currentLang}</span>
                                                <span className="fr-hidden-lg"> {currentLang} - {currentLang === 'FR' ? t('header.language.fr').split(' - ')[1] : t('header.language.en').split(' - ')[1]}</span>
                                            </div>
                                            <div className={`fr-collapse fr-translate__menu fr-menu ${isMenuOpen ? 'fr-collapse--expanded' : ''}`}
                                                id="translate-menu-desktop" data-fr-js-collapse="true" style={{ ['--collapse' as any]: '-132px' }}>
                                                <ul className="fr-menu__list">
                                                    <li><a className="fr-translate__language fr-nav__link" hrefLang="fr" lang="fr"
                                                        aria-current={currentLang === 'FR' ? 'true' : 'false'}
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            handleLanguageChange('FR', false);
                                                        }}>
                                                        {t('header.language.fr')}
                                                    </a>
                                                    </li>
                                                    <li><a className="fr-translate__language fr-nav__link" hrefLang="en" lang="en"
                                                        aria-current={currentLang === 'EN' ? 'true' : 'false'}
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            handleLanguageChange('EN', false);
                                                        }}>
                                                        {t('header.language.en')}</a></li>
                                                </ul>
                                            </div>
                                        </button>
                                    </li>
                                    <li className="contact-li">
                                        <a className="fr-btn fr-icon-mail-line" href="/accueil-etrangers" title={t('header.contact.title')}>
                                            {t('header.contact')}
                                        </a>
                                    </li>
                                    <li>
                                        <button className="fr-btn fr-icon-theme-fill fr-link--icon-left"
                                            aria-controls="fr-theme-modal">
                                            {t('header.display')}
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
                                        {t('header.close')}
                                    </button>
                                    <form className="search-container loupe autocomplete" role="search">
                                        <div className="fr-search-bar"
                                            id="search-371"
                                            role="search">
                                            <label className="fr-label" htmlFor="search-371-input">{t('header.search')}</label>
                                            <input className="fr-input searchh autocomplete"
                                                placeholder={t('header.search')}
                                                type="search"
                                                id="search-371-input"
                                                name="SearchText"
                                                required />
                                            <button className="fr-btn"
                                                title={t('header.search')}>
                                                {t('header.search')}
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
                        title={t('header.closeMenu')}>
                        {t('header.closeMenu')}
                    </button>
                    <div className="fr-header__menu-links">
                        <ul className="fr-btns-group">
                            <li className="contact-li">
                                <a className="fr-btn fr-icon-mail-line" href="/accueil-etrangers" title={t('header.contact.title')}>
                                    {t('header.contact')}
                                </a>
                            </li>
                            <li>
                                <button className="fr-btn fr-icon-theme-fill fr-link--icon-left" aria-controls="fr-theme-modal">
                                    {t('header.display')}
                                </button>
                            </li>
                            <li className="fr-translate fr-nav">
                                <button
                                    aria-controls="translate-menu-mobile"
                                    aria-expanded={isMenuMobileOpen}
                                    title={t('header.language.select')}
                                    className="fr-btn fr-icon-translate-2 fr-btn--tertiary-no-outline fr-translate"
                                    onClick={() => toggleMenu(true)}>
                                    <div>
                                        <span className="short-label">{currentLang}</span>
                                        <span className="fr-hidden-lg"> {currentLang} - {currentLang === 'FR' ? t('header.language.fr').split(' - ')[1] : t('header.language.en').split(' - ')[1]}</span>
                                    </div>
                                    <div
                                        className={`fr-collapse fr-translate__menu fr-menu ${isMenuMobileOpen ? 'fr-collapse--expanded' : ''}`}
                                        id="translate-menu-mobile">
                                        <ul className="fr-menu__list">
                                            <li>
                                                <a className="fr-translate__language fr-nav__link"
                                                    href="/"
                                                    hrefLang="fr"
                                                    lang="fr"
                                                    aria-current={currentLang === 'FR' ? 'true' : 'false'}
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        handleLanguageChange('FR', true);
                                                    }}>
                                                    {t('header.language.fr')}
                                                </a>
                                            </li>
                                            <li>
                                                <a className="fr-translate__language fr-nav__link"
                                                    href="/"
                                                    hrefLang="en"
                                                    lang="en"
                                                    aria-current={currentLang === 'EN' ? 'true' : 'false'}
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        handleLanguageChange('EN', true);
                                                    }}>
                                                    {t('header.language.en')}
                                                </a>
                                            </li>
                                        </ul>
                                    </div>
                                </button>
                            </li>
                        </ul>
                    </div>
                    <nav className="fr-nav" id="nav-main" role="navigation" aria-label="Menu principal">
                        <ul className="fr-nav__list">
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-actualites">
                                    {t('nav.news')}
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-actualites">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-actualites">
                                                    {t('nav.close.news')}
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">{t('nav.news')}</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Actualites">
                                                        {t('nav.seeAll')}
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-actions">
                                    {t('nav.actions')}
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-actions">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-actions">
                                                    {t('nav.close.actions')}
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">{t('nav.actions')}</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Actions-de-l-Etat">
                                                        {t('nav.seeAll')}
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-services">
                                    {t('nav.services')}
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-services">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-services">
                                                    {t('nav.close.services')}
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">{t('nav.services')}</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Services-de-l-Etat">
                                                        {t('nav.seeAll')}
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-publications">
                                    {t('nav.publications')}
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-publications">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-publications">
                                                    {t('nav.close.publications')}
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">{t('nav.publications')}</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Publications">
                                                        {t('nav.seeAll')}
                                                    </Link>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                            <li className="fr-nav__item">
                                <button className="fr-nav__btn" aria-expanded="false" aria-controls="menu-demarches">
                                    {t('nav.procedures')}
                                </button>
                                <div className="fr-collapse fr-mega-menu" id="menu-demarches">
                                    <div className="fr-container fr-container--fluid">
                                        <div className="fr-grid-row">
                                            <div className="fr-col-12">
                                                <button className="fr-btn--close fr-btn" aria-controls="menu-demarches">
                                                    {t('nav.close.procedures')}
                                                </button>
                                                <div className="fr-mega-menu__leader">
                                                    <h4 className="fr-h4">{t('nav.procedures')}</h4>
                                                    <Link className="fr-link fr-icon-arrow-right-line fr-link--icon-right" href="https://www.yvelines.gouv.fr/Demarches">
                                                        {t('nav.seeAll')}
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