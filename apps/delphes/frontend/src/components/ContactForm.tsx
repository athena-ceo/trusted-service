"use client";

import { useState, useEffect } from "react";

interface FormData {
    nom: string;
    prenom: string;
    email: string;
    arrondissement: string;
    agdref: string;
    message: string;
    acceptation: boolean;
}

interface ContactFormProps {
    onSubmit: (formData: FormData) => void;
    isLoading: boolean;
}

interface CaseModel {
    case_fields?: Array<{
        id: string;
        allowed_values?: Array<{
            id: string;
            label: string;
            condition_javascript?: string;
        }>;
    }>;
}

// Données pour le préremplissage automatique (pour les tests)
const noms = ["Smith", "Jordan", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"];
const prenoms = ["John", "Michael", "David", "James", "Robert", "Maria", "Jennifer", "Linda", "Elizabeth", "Patricia"];
const messageries = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"];

const exempleMessage = `Bonjour,

J'ai effectué la démarche en ligne sur ANEF pour le renouvellement de mon titre séjour - passeport talent le 09-08-2023. 
J'ai reçu l'attestation de prolongation directement après l'expiration de mon titre de séjour. 
Cette dernière à été renouvelée le 29-02-2024 et expirée le 28/05/2024.
Mais jusqu'à ce jour je n'ai pas reçu une nouvelle API.
Mon contrat de travail et suspendu et si ça continue, mon contrat de travail va être résilié.

Cordialement,`;

export default function ContactForm({ onSubmit, isLoading }: ContactFormProps) {
    const [formData, setFormData] = useState<FormData>({
        nom: "",
        prenom: "",
        email: "",
        arrondissement: "",
        agdref: "",
        message: "",
        acceptation: false,
    });

    const [arrondissements, setArrondissements] = useState<Array<{ id: string, label: string }>>([]);
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
                if (!response.ok) throw new Error("Erreur lors de la récupération des arrondissements");
                return response.json();
            })
            .then(data => {
                // Chercher le case_field avec id 'arrondissement'
                const caseFields = data.case_fields || [];
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
            })
            .catch(error => {
                console.error('Erreur lors du chargement des arrondissements:', error);
                setArrondissements([{ id: "", label: "Impossible de charger les arrondissements" }]);
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
            message: `${exempleMessage}\n\n${randomPrenom} ${randomNom}`,
            acceptation: true,
        });
    };

    const validateForm = (): boolean => {
        const newErrors: Partial<FormData> = {};

        if (!formData.nom.trim()) newErrors.nom = "Le nom est requis";
        if (!formData.prenom.trim()) newErrors.prenom = "Le prénom est requis";
        if (!formData.email.trim()) {
            newErrors.email = "L'email est requis";
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = "L'email n'est pas valide";
        }
        if (!formData.arrondissement) newErrors.arrondissement = "Veuillez sélectionner un arrondissement";
        if (!formData.message.trim()) newErrors.message = "Le message est requis";
        if (!formData.acceptation) {
            (newErrors as any).acceptation = "Vous devez accepter les conditions";
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
                    <p className="fr-text--heavy">* Champs obligatoires</p>
                </div>
            </div>

            <div className="fr-fieldset__element">
                <div className={`fr-input-group ${errors.nom ? 'fr-input-group--error' : ''}`}>
                    <label htmlFor="nom-service" className="fr-label">
                        Nom *
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
                        Prénom *
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
                        Adresse électronique *
                        <span className="fr-hint-text">Format attendu : nom@domaine.ext</span>
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

            <div className={`fr-select-group ${errors.arrondissement ? 'fr-input-group--error' : ''}`}>
                <label className="fr-label" htmlFor="arrondissement">
                    Veuillez sélectionner l'arrondissement de rattachement de votre commune de résidence *
                    <span className="fr-hint-text">
                        <a target="_blank" rel="noopener noreferrer"
                            href="https://www.yvelines.gouv.fr/contenu/telechargement/29247/169330/file/bloc%201.2%20-%20Annexe%202_Liste%20des%20communes%20et%20arrondissements%201er%20janvier%202017.pdf">
                            Cliquer ici pour consulter la liste des arrondissements de rattachement des communes des Yvelines.
                        </a>
                    </span>
                </label>
                <select
                    className="fr-select"
                    id="arrondissement"
                    name="arrondissement"
                    value={formData.arrondissement}
                    onChange={handleChange}
                    required
                >
                    <option value="">Choisissez un arrondissement</option>
                    {arrondissements.map((arr) => (
                        <option key={arr.id} value={arr.id}>
                            {arr.label}
                        </option>
                    ))}
                </select>
                {errors.arrondissement && <p className="fr-error-text">{errors.arrondissement}</p>}
            </div>

            <div className={`fr-input-group ${errors.agdref ? 'fr-input-group--error' : ''}`}>
                <label htmlFor="agdref-service" className="fr-label">
                    N° AGDREF
                    <span className="fr-hint-text">Format attendu : 78123456789</span>
                </label>
                <input className="fr-input" autoComplete="agdref-national"
                    aria-describedby="agdref-service-input-messages" type="agdref"
                    name="agdref" id="agdref-service" value={formData.agdref} onChange={handleChange} />
                {errors.agdref && <p className="fr-error-text">{errors.agdref}</p>}
                <div className="fr-messages-group" id="agdref-service-input-messages"
                    aria-live="polite">
                </div>
            </div>

            <div className={`fr-input-group ${errors.message ? 'fr-input-group--error' : ''}`}>
                <div className="fr-input-group">
                    <label htmlFor="votremessage-service" className="fr-label">
                        Message *
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
                    <input type="checkbox" name="acceptation" id="reglement-service" required
                        className="fr-input" />
                    <label htmlFor="reglement-service" className="fr-label">
                        En soumettant ce formulaire, j’accepte que les informations saisies
                        soient utilisées pour permettre de me recontacter, répondre à ma
                        demande. *
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
                        {isLoading ? 'Envoi en cours...' : 'Envoyer votre message'}
                    </button>

                    <button
                        type="button"
                        className="fr-btn fr-btn--secondary fr-ml-2w"
                        onClick={preremplirFormulaire}
                    >
                        Préremplir le formulaire (test)
                    </button>
                </div>
            </div>
        </form >
    );
}
