"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Header({ departement = '' }: { departement?: string }) {
    const { currentLang, setLanguage, t } = useLanguage();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isMenuMobileOpen, setIsMenuMobileOpen] = useState(false);
    const [departementLabel, setDepartementLabel] = useState('');

    useEffect(() => {
        if (departement === '78') {
            setDepartementLabel('des Yvelines');
        } else if (departement === '91') {
            setDepartementLabel('de l\'Essonne');
        } else if (departement === '92') {
            setDepartementLabel('des Hauts-de-Seine');
        } else if (departement === '94') {
            setDepartementLabel('du Val-de-Marne');
        }
    }, [departement]);

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
                                        préfet
                                        <br />
                                        {departementLabel}
                                    </p>
                                </div>
                                <div className="fr-header__navbar">
                                    {/* <button className="fr-btn--search fr-btn"
                                        aria-controls="modal-372"
                                        id="button-373"
                                        title={t('header.search')}>
                                        {t('header.search')}
                                    </button> */}
                                    {/* <button className="fr-btn--menu fr-btn"
                                        aria-controls="modal-398"
                                        aria-haspopup="menu"
                                        id="button-399"
                                        title={t('header.menu')}>
                                        {t('header.menu')}
                                    </button> */}
                                </div>
                            </div>
                            <div className="fr-header__service">
                                <Link href="/" title={t('service.home' + "." + departement)} className="fr-header__service-link">
                                    <p className="fr-header__service-title">
                                        {t('service.title' + "." + departement)}
                                    </p>
                                </Link>
                                <p className="fr-header__service-tagline">
                                    {t('service.tagline' + "." + departement)}
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
                                    {departement && (
                                        <li className="contact-li">
                                            <a className="fr-btn fr-icon-mail-line" href={`/accueil-etrangers${departement ? `?departement=${departement}` : ''}`} title={t('header.contact.title')}>
                                                {t('header.contact')}
                                            </a>
                                        </li>
                                    )}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}