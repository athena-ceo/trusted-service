"use client";

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

type Language = 'FR' | 'EN';

interface LanguageContextType {
    currentLang: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string, ...params: (string | number)[]) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations: Record<Language, Record<string, string>> = {
    FR: {
        // Header
        'header.search': 'Rechercher',
        'header.menu': 'Menu',
        'header.contact': 'Nous contacter',
        'header.contact.title': 'Nous contacter - formulaire de contact',
        'header.display': 'Paramètres d\'affichage',
        'header.close': 'Fermer',
        'header.closeMenu': 'Fermer Menu',
        'header.language.select': 'Sélectionner une langue',
        'header.language.fr': 'FR - Français',
        'header.language.en': 'EN - English',

        // Service title
        'service.title': 'Les services de l\'État dans les Yvelines',
        'service.tagline': 'Portail de l\'État en Yvelines',
        'service.home': 'Accueil - Les services de l\'État dans les Yvelines',

        // Navigation
        'nav.news': 'Actualités',
        'nav.actions': 'Actions de l\'Etat',
        'nav.services': 'Services de l\'État',
        'nav.publications': 'Publications',
        'nav.procedures': 'Démarches',
        'nav.seeAll': 'Voir toute la rubrique',
        'nav.close.news': 'Fermer - Actualités',
        'nav.close.actions': 'Fermer - Actions de l\'Etat',
        'nav.close.services': 'Fermer - Services de l\'État',
        'nav.close.publications': 'Fermer - Publications',
        'nav.close.procedures': 'Fermer - Démarches',

        // Footer
        'footer.home': 'Retour à l\'accueil du site - Les services de l\'État dans les Yvelines',
        'footer.description': 'Portail officiel des services de l\'État dans le département des Yvelines',
        'footer.sitemap': 'Plan du site',
        'footer.contact': 'Nous contacter',
        'footer.accessibility': 'Accessibilité : partiellement conforme',
        'footer.license.text': 'Sauf mention contraire, tous les contenus de ce site sont sous',
        'footer.license.name': 'licence etalab-2.0',

        // Home Page
        'home.banner.title': 'Information importante',
        'home.banner.message': 'Nouveau service d\'accueil des étrangers avec assistance intelligente disponible',
        'home.procedures.title': 'Les démarches en ligne',
        'home.procedures.hours': 'Horaires et lieux d\'accueil',
        'home.procedures.all': 'Toutes les démarches',
        'home.procedures.carteGrise': 'Carte grise',
        'home.procedures.permis': 'Permis de conduire',
        'home.procedures.carteId': 'Carte d\'identité',
        'home.procedures.passeport': 'Passeport',
        'home.procedures.etrangers': 'Accueil des étrangers',
        'home.news.title': 'Actualités',
        'home.news.ariaLabel': 'Consultez nos actualités',
        'home.news.all': 'Toutes les actualités',
        'home.news.readMore': 'Lire la suite',
        'home.news.published': 'Publié le',
        'home.news.article1.title': 'Les Yvelines lancent leur premier Comité d\'action économique locale',
        'home.news.article2.title': 'Se préparer aux risques majeurs : les Yvelines en situation d\'entraînement',
        'home.news.article3.title': 'Une permanence pour les victimes d\'actes LGBTQIA+',
        'home.news.article4.title': 'COP25 : de l\'engagement global à la mobilisation locale dans les Yvelines',
        'home.news.article4.line1': 'La COP25 et les actions territoriales :',
        'home.news.article4.line2': 'de l\'engagement global à la mobilisation locale',
        'home.news.article4.line3': 'dans les Yvelines',
        'home.sidebar.title': 'Vous accompagner',
        'home.sidebar.reception.title': 'Accueil des étrangers dans les Yvelines',
        'home.sidebar.reception.desc': 'Nouveau service intelligent avec assistance IA pour faciliter vos démarches',
        'home.sidebar.hours.title': 'Horaires - coordonnées et accessibilité',
        'home.sidebar.hours.desc': 'Préfecture et Sous-Préfectures des Yvelines',
        'home.sidebar.faq.title': 'Foire aux questions',
        'home.sidebar.faq.desc': 'Trouvez rapidement des réponses à vos questions',
        'home.newsletter.title': 'Abonnez-vous à notre lettre d\'information',
        'home.newsletter.desc': 'Restez informé des dernières actualités et nouveautés des services de l\'État dans les Yvelines',
        'home.newsletter.subscribe': 'S\'abonner',
        'home.social.title': 'Suivez-nous',
        'home.social.subtitle': 'sur les réseaux sociaux',
        'home.social.twitter': 'Twitter',
        'home.social.twitter.title': 'Twitter - nouvelle fenêtre',

        // Accueil Etrangers Page
        'accueil.breadcrumb.show': 'Voir le fil d\'Ariane',
        'accueil.breadcrumb.home': 'Accueil',
        'accueil.breadcrumb.current': 'Accueil des étrangers',
        'accueil.title': 'Accueil des étrangers',
        'accueil.intro.line1': 'Vous souhaitez contacter les services d\'accueil des étrangers dans le département des Yvelines.',
        'accueil.intro.line2': 'Nous vous invitons à utiliser le formulaire ci-dessous.',
        'accueil.intro.line3': 'Nos services mettront tout en œuvre pour vous répondre dans les meilleurs délais.',
        'accueil.alert.info.title': 'Information importante',
        'accueil.alert.info.message': 'Pour toute information concernant le suivi de votre demande de titre de séjour, indiquez impérativement votre numéro étranger/AGDREF (à 10 chiffres) si vous en avez un.',
        'accueil.alert.warning': 'Les données personnelles recueillies par le formulaire de prise de contact ne sont pas conservées par la préfecture des Yvelines.',
        'accueil.sidebar.title': 'En complément',
        'accueil.sidebar.sites.title': 'Sites officiels pour vos démarches',
        'accueil.sidebar.sites.desc': 'Accédez directement aux sites officiels de l\'administration française.',
        'accueil.sidebar.sites.servicePublic': 'service-public.fr',
        'accueil.sidebar.sites.servicePublic.title': 'Accéder à service-public.fr - Nouvelle fenêtre',
        'accueil.sidebar.sites.demarches': 'Démarches du Ministère de l\'Intérieur',
        'accueil.sidebar.sites.demarches.title': 'Accéder aux démarches du Ministère de l\'Intérieur - Nouvelle fenêtre',
        'accueil.sidebar.anef.title': 'ANEF',
        'accueil.sidebar.anef.desc': 'L\'administration numérique pour les étrangers en France (ANEF) a pour objectif de dématérialiser les démarches concernant le séjour des étrangers en France.',
        'accueil.sidebar.anef.link': 'Accédez à la plateforme',
        'accueil.sidebar.anef.linkTitle': 'Accéder à l\'ANEF - Nouvelle fenêtre',
        'accueil.sidebar.services.title': 'Les services de l\'État',
        'accueil.sidebar.services.desc': 'Vous pouvez saisir l\'administration par voie électronique en adressant en ligne vos demandes d\'information ou envoyer un dossier lié à une démarche administrative.',
        'accueil.sidebar.services.link': 'Accédez à la plateforme',
        'accueil.sidebar.services.linkTitle': 'Accéder à la plateforme les services de l\'état https://contacts-demarches.interieur.gouv.fr/ - Nouvelle fenêtre',

        // Analysis Page
        'analysis.alert.processing.title': 'Votre demande est en cours de traitement automatique',
        'analysis.alert.success.title': 'Votre demande a été analysée automatiquement',
        'analysis.alert.greeting.start': 'Merci',
        'analysis.alert.greeting.end': 'nous avons bien reçu votre demande et notre système l\'analyse pour vous orienter vers le bon service.',
        'analysis.yourMessage': 'Votre message :',
        'analysis.form.selectPrompt': 'Veuillez sélectionner le cas qui s\'applique à votre situation.',
        'analysis.form.aiIdentified': 'L\'IA a identifié',
        'analysis.form.cases': 'cas correspondant à votre demande.',
        'analysis.form.yourSelection': 'Votre sélection :',
        'analysis.form.fields.date_expiration_api': 'Date d\'expiration de l\'API',
        'analysis.form.fields.date_expiration_recepisse': 'Date d\'expiration du récépissé',
        'analysis.form.fields.date_expiration_titre_sejour': 'Date d\'expiration du titre de séjour',
        'analysis.form.fields.refugie_ou_protege_subsidiaire': 'Réfugié ou protégé subsidiaire',
        'analysis.form.fields.motif_deces': 'Motif de décès',
        'analysis.form.fields.demandeur_d_asile': 'Demandeur d\'asile',
        'analysis.form.fields.statut': 'Statut',
        'analysis.form.fields.dateFormat': 'Format attendu : JJ/MM/AAAA',
        'analysis.form.fields.yes': 'Oui',
        'analysis.form.fields.no': 'Non',
        'analysis.form.validate': 'Valider',
        'analysis.noResults.title': 'Résultats de l\'analyse automatique',
        'analysis.noResults.message': 'Notre système n\'a pas pu identifier d\'intention claire dans votre message. Veuillez reformuler votre demande.',
        'analysis.backToHome': 'Retour à l\'accueil',
        'analysis.loadingData': 'Chargement des données de votre demande...',

        // Handle Case Page
        'handleCase.alert.processing.title': 'Votre demande est en cours de traitement',
        'handleCase.alert.success.title': 'Votre demande a été traitée',
        'handleCase.alert.greeting.start': 'Merci',
        'handleCase.alert.greeting.end': 'nous avons bien reçu votre demande et notre système l\'a analysée pour vous apporter la meilleure réponse.',
        'handleCase.yourMessage': 'Votre message :',
        'handleCase.thanks': 'Merci de votre patience',
        'handleCase.nextSteps.title': 'Prochaines étapes',
        'handleCase.nextSteps.message': 'Veuillez suivre les instructions ci-dessus. En cas de besoin, un agent du service concerné vous contactera à l\'adresse email que vous avez fournie, après examen de votre demande.',
        'handleCase.agentView': 'Vue Boîte aux lettres de l\'Agent',
        'handleCase.fieldValues': 'Valeurs des champs :',
        'handleCase.generateResponse': 'Générer la réponse',
        'handleCase.generatedResponse': 'Réponse générée :',
        'handleCase.noResponse': 'Aucune réponse générée',
        'handleCase.loadingData': 'Chargement des données de votre demande...',
        'handleCase.analysisResult': 'Résultat de l\'analyse de la demande de $1 $2 du $3',

        // Contact Form
        'form.requiredFields': '* Champs obligatoires',
        'form.lastName': 'Nom',
        'form.firstName': 'Prénom',
        'form.email': 'Adresse électronique',
        'form.emailFormat': 'Format attendu : nom@domaine.ext',
        'form.arrondissement': 'Arrondissement de rattachement de votre commune de résidence',
        'form.arrondissementLink': 'Cliquer ici pour consulter la liste des arrondissements de rattachement des communes des Yvelines.',
        'form.selectArrondissement': 'Choisissez un arrondissement',
        'form.agdref': 'Numéro étranger',
        'form.agdrefFormat': 'Format attendu : 10 chiffres',
        'form.statut': 'Statut',
        'form.selectStatut': 'Choisissez le statut qui correspond le mieux à votre situation',
        'form.message': 'Message',
        'form.acceptance': 'En soumettant ce formulaire, j\'accepte que les informations saisies soient utilisées pour permettre de me recontacter, répondre à ma demande.',
        'form.sending': 'Envoi en cours...',
        'form.submit': 'Envoyer votre message',
        'form.prefill': 'Préremplir le formulaire (test)',
        'form.error.lastName': 'Le nom est requis',
        'form.error.firstName': 'Le prénom est requis',
        'form.error.email.required': 'L\'email est requis',
        'form.error.email.invalid': 'L\'email n\'est pas valide',
        'form.error.arrondissement': 'Veuillez sélectionner un arrondissement',
        'form.error.message': 'Le message est requis',
        'form.error.acceptance': 'Vous devez accepter les conditions',
        'form.message.example': `Bonjour,

J'ai effectué la démarche en ligne sur le site ANEF pour le renouvellement de mon titre séjour - passeport talent le 09-08-2024. 
J'ai reçu l'attestation de prolongation directement après l'expiration de mon titre de séjour. 
Cette dernière a été renouvelée durant l'été mais maintenant, mon API est expirée depuis le début du mois.
Mais jusqu'à ce jour je n'ai pas reçu de nouvelle API.
Mon contrat de travail est suspendu et si ça continue, mon contrat de travail va être résilié.

Cordialement,`,
    },
    EN: {
        // Header
        'header.search': 'Search',
        'header.menu': 'Menu',
        'header.contact': 'Contact us',
        'header.contact.title': 'Contact us - contact form',
        'header.display': 'Display settings',
        'header.close': 'Close',
        'header.closeMenu': 'Close Menu',
        'header.language.select': 'Select language',
        'header.language.fr': 'FR - French',
        'header.language.en': 'EN - English',

        // Service title
        'service.title': 'State Services in Yvelines',
        'service.tagline': 'Yvelines State Portal',
        'service.home': 'Home - State Services in Yvelines',

        // Navigation
        'nav.news': 'News',
        'nav.actions': 'State Actions',
        'nav.services': 'State Services',
        'nav.publications': 'Publications',
        'nav.procedures': 'Procedures',
        'nav.seeAll': 'See all',
        'nav.close.news': 'Close - News',
        'nav.close.actions': 'Close - State Actions',
        'nav.close.services': 'Close - State Services',
        'nav.close.publications': 'Close - Publications',
        'nav.close.procedures': 'Close - Procedures',

        // Footer
        'footer.home': 'Back to homepage - State Services in Yvelines',
        'footer.description': 'Official portal of state services in the Yvelines department',
        'footer.sitemap': 'Site map',
        'footer.contact': 'Contact us',
        'footer.accessibility': 'Accessibility: partially compliant',
        'footer.license.text': 'Unless otherwise stated, all content on this site is licensed under',
        'footer.license.name': 'etalab-2.0 license',

        // Home Page
        'home.banner.title': 'Important information',
        'home.banner.message': 'New intelligent assistance service for foreign reception now available',
        'home.procedures.title': 'Online procedures',
        'home.procedures.hours': 'Reception hours and locations',
        'home.procedures.all': 'All procedures',
        'home.procedures.carteGrise': 'Vehicle registration',
        'home.procedures.permis': 'Driver\'s license',
        'home.procedures.carteId': 'Identity card',
        'home.procedures.passeport': 'Passport',
        'home.procedures.etrangers': 'Foreign reception',
        'home.news.title': 'News',
        'home.news.ariaLabel': 'View our news',
        'home.news.all': 'All news',
        'home.news.readMore': 'Read more',
        'home.news.published': 'Published on',
        'home.news.article1.title': 'Yvelines launches its first Local Economic Action Committee',
        'home.news.article2.title': 'Preparing for major risks: Yvelines in training situation',
        'home.news.article3.title': 'Support desk for victims of LGBTQIA+ acts',
        'home.news.article4.title': 'COP25: from global commitment to local mobilization in Yvelines',
        'home.news.article4.line1': 'COP25 and territorial actions:',
        'home.news.article4.line2': 'from global commitment to local mobilization',
        'home.news.article4.line3': 'in Yvelines',
        'home.sidebar.title': 'Supporting you',
        'home.sidebar.reception.title': 'Foreign reception in Yvelines',
        'home.sidebar.reception.desc': 'New intelligent service with AI assistance to facilitate your procedures',
        'home.sidebar.hours.title': 'Hours - contact details and accessibility',
        'home.sidebar.hours.desc': 'Prefecture and Sub-Prefectures of Yvelines',
        'home.sidebar.faq.title': 'Frequently asked questions',
        'home.sidebar.faq.desc': 'Quickly find answers to your questions',
        'home.newsletter.title': 'Subscribe to our newsletter',
        'home.newsletter.desc': 'Stay informed of the latest news and updates from State services in Yvelines',
        'home.newsletter.subscribe': 'Subscribe',
        'home.social.title': 'Follow us',
        'home.social.subtitle': 'on social media',
        'home.social.twitter': 'Twitter',
        'home.social.twitter.title': 'Twitter - new window',

        // Accueil Etrangers Page
        'accueil.breadcrumb.show': 'Show breadcrumb',
        'accueil.breadcrumb.home': 'Home',
        'accueil.breadcrumb.current': 'Foreign reception',
        'accueil.title': 'Foreign reception',
        'accueil.intro.line1': 'You wish to contact the foreign reception services in the Yvelines department.',
        'accueil.intro.line2': 'We invite you to use the form below.',
        'accueil.intro.line3': 'Our services will do their best to respond to you as soon as possible.',
        'accueil.alert.info.title': 'Important information',
        'accueil.alert.info.message': 'For any information regarding the follow-up of your residence permit application, you must provide your foreign number/AGDREF (10 digits) if you have one.',
        'accueil.alert.warning': 'Personal data collected through the contact form is not stored by the Yvelines prefecture.',
        'accueil.sidebar.title': 'Additional information',
        'accueil.sidebar.sites.title': 'Official sites for your procedures',
        'accueil.sidebar.sites.desc': 'Access directly the official sites of the French administration.',
        'accueil.sidebar.sites.servicePublic': 'service-public.fr',
        'accueil.sidebar.sites.servicePublic.title': 'Access service-public.fr - New window',
        'accueil.sidebar.sites.demarches': 'Ministry of Interior Procedures',
        'accueil.sidebar.sites.demarches.title': 'Access Ministry of Interior procedures - New window',
        'accueil.sidebar.anef.title': 'ANEF',
        'accueil.sidebar.anef.desc': 'The digital administration for foreigners in France (ANEF) aims to digitize procedures concerning the stay of foreigners in France.',
        'accueil.sidebar.anef.link': 'Access the platform',
        'accueil.sidebar.anef.linkTitle': 'Access ANEF - New window',
        'accueil.sidebar.services.title': 'State services',
        'accueil.sidebar.services.desc': 'You can contact the administration electronically by sending your information requests online or sending a file related to an administrative procedure.',
        'accueil.sidebar.services.link': 'Access the platform',
        'accueil.sidebar.services.linkTitle': 'Access the state services platform https://contacts-demarches.interieur.gouv.fr/ - New window',

        // Analysis Page
        'analysis.alert.processing.title': 'Your request is being automatically processed',
        'analysis.alert.success.title': 'Your request has been automatically analyzed',
        'analysis.alert.greeting.start': 'Thank you',
        'analysis.alert.greeting.end': 'we have received your request and our system is analyzing it to direct you to the right service.',
        'analysis.yourMessage': 'Your message:',
        'analysis.form.selectPrompt': 'Please select the case that applies to your situation.',
        'analysis.form.aiIdentified': 'AI has identified',
        'analysis.form.cases': 'cases matching your request.',
        'analysis.form.yourSelection': 'Your selection:',
        'analysis.form.fields.date_expiration_api': 'API expiration date',
        'analysis.form.fields.date_expiration_recepisse': 'Receipt expiration date',
        'analysis.form.fields.date_expiration_titre_sejour': 'Residence permit expiration date',
        'analysis.form.fields.refugie_ou_protege_subsidiaire': 'Refugee or beneficiary of subsidiary protection',
        'analysis.form.fields.motif_deces': 'Reason is death',
        'analysis.form.fields.demandeur_d_asile': 'Asylum seeker',
        'analysis.form.fields.statut': 'Status',
        'analysis.form.fields.dateFormat': 'Expected format: DD/MM/YYYY',
        'analysis.form.fields.yes': 'Yes',
        'analysis.form.fields.no': 'No',
        'analysis.form.validate': 'Submit',
        'analysis.noResults.title': 'Automatic analysis results',
        'analysis.noResults.message': 'Our system could not identify a clear intention in your message. Please rephrase your request.',
        'analysis.backToHome': 'Back to home',
        'analysis.loadingData': 'Loading your request data...',

        // Handle Case Page
        'handleCase.alert.processing.title': 'Your request is being processed.',
        'handleCase.alert.success.title': 'Your request has been processed.',
        'handleCase.alert.greeting.start': 'Thank you',
        'handleCase.alert.greeting.end': 'We have received your request and our system has analysed it to provide you with the best response.',
        'handleCase.yourMessage': 'Your message:',
        'handleCase.thanks': 'Thank you for your patience',
        'handleCase.nextSteps.title': 'Next steps',
        'handleCase.nextSteps.message': 'Please follow the instructions above. If necessary, an agent from the relevant department will contact you at the email address you provided, after reviewing your request.',
        'handleCase.agentView': 'Agent View',
        'handleCase.fieldValues': 'Field values:',
        'handleCase.generateResponse': 'Generate response',
        'handleCase.generatedResponse': 'Generated response:',
        'handleCase.noResponse': 'No response generated',
        'handleCase.loadingData': 'Loading your request data...',
        'handleCase.analysisResult': 'Analysis result of the request from $1 $2 dated $3',

        // Contact Form
        'form.requiredFields': '* Required fields',
        'form.lastName': 'Last name',
        'form.firstName': 'First name',
        'form.email': 'Email address',
        'form.emailFormat': 'Expected format: name@domain.ext',
        'form.arrondissement': 'District of your municipality of residence',
        'form.arrondissementLink': 'Click here to view the list of districts of municipalities in Yvelines.',
        'form.selectArrondissement': 'Choose a district',
        'form.agdref': 'Numéro étranger',
        'form.agdrefFormat': 'Expected format: 10 digits',
        'form.statut': 'Status',
        'form.selectStatut': 'Select the status that best fits your situation.',
        'form.message': 'Message',
        'form.acceptance': 'By submitting this form, I agree that the information entered may be used to contact me and respond to my request.',
        'form.sending': 'Sending...',
        'form.submit': 'Send your message',
        'form.prefill': 'Prefill form (test)',
        'form.error.lastName': 'Last name is required',
        'form.error.firstName': 'First name is required',
        'form.error.email.required': 'Email is required',
        'form.error.email.invalid': 'Email is not valid',
        'form.error.arrondissement': 'Please select a district',
        'form.error.message': 'Message is required',
        'form.error.acceptance': 'You must accept the conditions',
        'form.message.example': `Hello,

I completed the online process on the ANEF website for the renewal of my residence permit - talent passport on 09-08-2024.
I received the extension certificate directly after the expiration of my residence permit.
The latter was renewed during the summer but my API is now expired since the beginning of the month.
But to this day I have not received a new API.
My work contract is suspended and if this continues, my work contract will be terminated.

Best regards,`
    }
};

export function LanguageProvider({ children }: { children: ReactNode }) {
    const [currentLang, setCurrentLang] = useState<Language>('FR');

    // Charger la langue depuis localStorage au montage
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const savedLang = localStorage.getItem('language') as Language;
            if (savedLang && (savedLang === 'FR' || savedLang === 'EN')) {
                setCurrentLang(savedLang);
            }
        }
    }, []);

    const setLanguage = (lang: Language) => {
        setCurrentLang(lang);
        // Sauvegarder dans localStorage
        if (typeof window !== 'undefined') {
            localStorage.setItem('language', lang);
        }
    };

    const t = (key: string, ...params: (string | number)[]): string => {
        let translation = translations[currentLang][key] || key;

        // Remplacer les paramètres $1, $2, $3, etc. par les valeurs fournies
        params.forEach((param, index) => {
            const placeholder = `$${index + 1}`;
            translation = translation.replace(new RegExp(`\\${placeholder}`, 'g'), String(param));
        });

        return translation;
    };

    return (
        <LanguageContext.Provider value={{ currentLang, setLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}
