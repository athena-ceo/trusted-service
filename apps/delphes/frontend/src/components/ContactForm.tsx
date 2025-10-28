"use client";

import { useState, useEffect } from "react";
import { useLanguage } from "@/contexts/LanguageContext";

interface FormData {
    nom: string;
    prenom: string;
    email: string;
    arrondissement: string;
    agdref: string;
    statut: string;
    message: string;
    acceptation: boolean;
}

interface ContactFormProps {
    onSubmit: (formData: FormData) => void;
    isLoading: boolean;
}

// Données pour le préremplissage automatique (pour les tests)
const noms = ["Smith", "Jordan", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"];
const prenoms = ["John", "Michael", "David", "James", "Robert", "Maria", "Jennifer", "Linda", "Elizabeth", "Patricia"];
const messageries = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"];

export default function ContactForm({ onSubmit, isLoading }: ContactFormProps) {
    const { t } = useLanguage();
    const [formData, setFormData] = useState<FormData>({
        nom: "",
        prenom: "",
        email: "",
        arrondissement: "",
        agdref: "",
        statut: "",
        message: "",
        acceptation: false,
    });

    const [arrondissements, setArrondissements] = useState<Array<{ id: string, label: string }>>([]);
    const [statuts, setStatuts] = useState<Array<{ id: string, label: string }>>([]);
    const [errors, setErrors] = useState<Partial<FormData>>({});

    // Charger les arrondissements depuis l'API
    useEffect(() => {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '__NEXT_PUBLIC_API_URL__';
        if (!apiBaseUrl || apiBaseUrl.startsWith('__NEXT_PUBLIC_')) {
            console.warn('NEXT_PUBLIC_API_URL is not configured - API calls may not work');
            return;
        }

        fetch(`${apiBaseUrl}/trusted_services/v2/apps/delphes/fr/case_model`)
            .then(response => {
                if (!response.ok) throw new Error("Erreur lors de la récupération des statuts et des arrondissements");
                return response.json();
            })
            .then(data => {
                const caseFields = data.case_fields || [];

                // Chercher le case_field avec id 'arrondissement'
                const arrondissementField = caseFields.find((f: any) => f.id === 'arrondissement');
                if (!arrondissementField || !arrondissementField.allowed_values) return;

                const allowed = arrondissementField.allowed_values;
                const departement = 78;

                // Filtrer selon la condition departement==78
                const filtered = allowed.filter((item: any) => {
                    try {
                        if (!item.condition_javascript) return true;
                        const cond = item.condition_javascript.replace(/\{departement\}/g, departement.toString());
                        return eval(cond);
                    } catch (e) {
                        return false;
                    }
                });

                setArrondissements(filtered);

                // Chercher le case_field avec id 'statut'
                const statutField = caseFields.find((f: any) => f.id === 'statut');
                if (!statutField || !statutField.allowed_values) return;

                setStatuts(statutField.allowed_values);
            })
            .catch(error => {
                console.error('Erreur lors du chargement des statuts et des arrondissements:', error);
                setArrondissements([{ id: "", label: "Impossible de charger les statuts et les arrondissements" }]);
            });
    }, []);

    // Fonction de préremplissage pour les tests
    const preremplirFormulaire = () => {
        const randomNom = noms[Math.floor(Math.random() * noms.length)];
        const randomPrenom = prenoms[Math.floor(Math.random() * prenoms.length)];
        const randomEmail = `${randomNom.toLowerCase()}.${randomPrenom.toLowerCase()}@${messageries[Math.floor(Math.random() * messageries.length)]}`;
        const randomAgdref = "78" + Math.floor(Math.random() * 1000000000);

        setFormData({
            nom: randomNom,
            prenom: randomPrenom,
            email: randomEmail,
            arrondissement: "VERS",
            agdref: randomAgdref,
            statut: "régulier",
            message: `${t('form.message.example')}\n\n${randomPrenom} ${randomNom}`,
            acceptation: true,
        });
    };

    const validateForm = (): boolean => {
        const newErrors: Partial<FormData> = {};

        if (!formData.nom.trim()) newErrors.nom = t('form.error.lastName');
        if (!formData.prenom.trim()) newErrors.prenom = t('form.error.firstName');
        if (!formData.email.trim()) {
            newErrors.email = t('form.error.email.required');
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = t('form.error.email.invalid');
        }
        if (!formData.arrondissement) newErrors.arrondissement = t('form.error.arrondissement');
        if (!formData.message.trim()) newErrors.message = t('form.error.message');
        if (!formData.acceptation) {
            (newErrors as any).acceptation = t('form.error.acceptance');
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) return;

        onSubmit(formData);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        const checked = (e.target as HTMLInputElement).checked;

        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        // Effacer l'erreur si l'utilisateur corrige
        if (errors[name as keyof FormData]) {
            setErrors(prev => ({ ...prev, [name]: undefined }));
        }
    };

    return (
        <form onSubmit={handleSubmit} className="fr-mb-6w">
            <div className="fr-grid-row fr-grid-row--gutters fr-mb-3w">
                <div className="fr-col-12">
                    <p className="fr-text--heavy">{t('form.requiredFields')}</p>
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-input-group ${errors.nom ? 'fr-input-group--error' : ''}`}>
                    <label htmlFor="nom-service" className="fr-label">
                        {t('form.lastName')} *
                    </label>
                    <input className="fr-input" aria-describedby="nom-service-messages" type="text"
                        name="nom" id="nom-service" value={formData.nom} onChange={handleChange} autoComplete="family-name"
                        required />
                    {errors.nom && <p className="fr-error-text">{errors.nom}</p>}
                    <div className="fr-messages-group" id="nom-service-messages" aria-live="polite">
                    </div>
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-input-group ${errors.prenom ? 'fr-input-group--error' : ''}`}>
                    <label htmlFor="prenom-service" className="fr-label">
                        {t('form.firstName')} *
                    </label>
                    <input className="fr-input" aria-describedby="prenom-service-messages"
                        type="text" name="prenom" id="prenom-service" value={formData.prenom}
                        onChange={handleChange} autoComplete="given-name" required />
                    {errors.prenom && <p className="fr-error-text">{errors.prenom}</p>}
                    <div className="fr-messages-group" id="prenom-service-messages"
                        aria-live="polite">
                    </div>
                </div>
            </div>

            <div className={`fr-fieldset__element ${errors.email ? 'fr-input-group--error' : ''}`}>
                <div className="fr-input-group">
                    <label htmlFor="email-service" className="fr-label">
                        {t('form.email')} *
                        <span className="fr-hint-text">{t('form.emailFormat')}</span>
                    </label>
                    <input className="fr-input" autoComplete="email"
                        aria-describedby="email-service-messages" type="email" name="email"
                        id="email-service" value={formData.email} onChange={handleChange} required />
                    {errors.email && <p className="fr-error-text">{errors.email}</p>}
                    <div className="fr-messages-group" id="email-service-messages"
                        aria-live="polite">
                    </div>
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-select-group ${errors.arrondissement ? 'fr-input-group--error' : ''}`}>
                    <label className="fr-label" htmlFor="arrondissement">
                        {t('form.arrondissement')} *
                    </label>
                    <div className="fr-alert fr-alert--warning fr-mb-1w">
                        <p>
                            <a
                                className="fr-link fr-icon-external-link-line fr-link--icon-right"
                                target="_blank"
                                rel="noopener noreferrer"
                                href="https://www.yvelines.gouv.fr/contenu/telechargement/29247/169330/file/bloc%201.2%20-%20Annexe%202_Liste%20des%20communes%20et%20arrondissements%201er%20janvier%202017.pdf">
                                {t('form.arrondissementLink')}
                            </a>
                        </p>
                    </div>
                    <select
                        className="fr-select"
                        id="arrondissement"
                        name="arrondissement"
                        value={formData.arrondissement}
                        onChange={handleChange}
                        required
                    >
                        <option value="">{t('form.selectArrondissement')}</option>
                        {arrondissements.map((arr) => (
                            <option key={arr.id} value={arr.id}>
                                {arr.label}
                            </option>
                        ))}
                    </select>
                    {errors.arrondissement && <p className="fr-error-text">{errors.arrondissement}</p>}
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-input-group ${errors.agdref ? 'fr-input-group--error' : ''}`}>
                    <label htmlFor="agdref-service" className="fr-label">
                        {t('form.agdref')}
                        <span className="fr-hint-text">{t('form.agdrefFormat')}</span>
                    </label>
                    <input className="fr-input"
                        aria-describedby="agdref-service-input-messages" type="text"
                        name="agdref" id="agdref-service" value={formData.agdref} onChange={handleChange} />
                    {errors.agdref && <p className="fr-error-text">{errors.agdref}</p>}
                    <div className="fr-messages-group" id="agdref-service-input-messages"
                        aria-live="polite">
                    </div>
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-select-group ${errors.statut ? 'fr-input-group--error' : ''}`}>
                    <label className="fr-label" htmlFor="statut">
                        {t('form.statut')} *
                    </label>
                    <select
                        className="fr-select"
                        id="statut"
                        name="statut"
                        value={formData.statut}
                        onChange={handleChange}
                        required
                    >
                        <option value="">{t('form.selectStatut')}</option>
                        {statuts.map((stat) => (
                            <option key={stat.id} value={stat.id}>
                                {stat.label}
                            </option>
                        ))}
                    </select>
                    {errors.statut && <p className="fr-error-text">{errors.statut}</p>}
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-input-group ${errors.message ? 'fr-input-group--error' : ''}`}>
                    <label htmlFor="votremessage-service" className="fr-label">
                        {t('form.message')} *
                    </label>
                    <textarea className="fr-input" aria-describedby="message-service-input-messages"
                        name="message" id="votremessage-service" value={formData.message} required rows={15}
                        cols={60} onChange={handleChange}></textarea>
                    {errors.message && <p className="fr-error-text">{errors.message}</p>}
                    <div className="fr-messages-group" id="message-service-input-messages"
                        aria-live="polite">
                    </div>
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-checkbox-group ${(errors as any).acceptation ? 'fr-input-group--error' : ''}`}>
                    <input
                        type="checkbox"
                        name="acceptation"
                        id="reglement-service"
                        required
                        className="fr-input"
                        checked={formData.acceptation}
                        onChange={handleChange}
                    />
                    <label htmlFor="reglement-service" className="fr-label">
                        {t('form.acceptance')} *
                    </label>
                    {(errors as any).acceptation && <p className="fr-error-text">{(errors as any).acceptation}</p>}
                </div>
            </div>

            <div className="fr-grid-row fr-grid-row--gutters">
                <div className="fr-col-12">
                    <button
                        type="submit"
                        className={`fr-btn ${isLoading ? 'fr-btn--loading' : ''}`}
                        disabled={isLoading}
                    >
                        {isLoading ? t('form.sending') : t('form.submit')}
                    </button>

                    <button
                        type="button"
                        className="fr-btn fr-btn--secondary fr-ml-2w"
                        onClick={preremplirFormulaire}
                    >
                        {t('form.prefill')}
                    </button>
                </div>
            </div>
        </form >
    );
}
