"use client";

import { useMemo, useState, useEffect, useCallback } from "react";
import { useLanguage } from "@/contexts/LanguageContext";
import Arrondissement78, { communesYvelines } from "./Arrondissement78";

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

interface ContactFormProps {
    onSubmit: (formData: FormData) => void;
    isLoading: boolean;
    departement?: string;
    mode?: string;
}

type ConditionToken =
    | { type: "number"; value: number }
    | { type: "operator"; value: string }
    | { type: "lparen" }
    | { type: "rparen" };

const CONDITION_OPERATORS = ["===", "!==", ">=", "<=", "==", "!=", "&&", "||", ">", "<"];

const tokenizeCondition = (condition: string): ConditionToken[] | null => {
    const tokens: ConditionToken[] = [];
    let i = 0;

    while (i < condition.length) {
        const char = condition[i];
        if (char === " " || char === "\t" || char === "\n") {
            i += 1;
            continue;
        }

        if (char === "(") {
            tokens.push({ type: "lparen" });
            i += 1;
            continue;
        }

        if (char === ")") {
            tokens.push({ type: "rparen" });
            i += 1;
            continue;
        }

        if (/\d/.test(char)) {
            let numberText = char;
            i += 1;
            while (i < condition.length && /\d/.test(condition[i])) {
                numberText += condition[i];
                i += 1;
            }
            tokens.push({ type: "number", value: Number(numberText) });
            continue;
        }

        const operator = CONDITION_OPERATORS.find((op) => condition.startsWith(op, i));
        if (operator) {
            tokens.push({ type: "operator", value: operator });
            i += operator.length;
            continue;
        }

        return null;
    }

    return tokens;
};

const evaluateCondition = (condition: string, departementNumber: number): boolean => {
    const normalized = condition
        .replace(/\{departement\}/g, String(departementNumber))
        .replace(/\bdepartement\b/g, String(departementNumber))
        .trim();

    const tokens = tokenizeCondition(normalized);
    if (!tokens || tokens.length === 0) {
        return false;
    }

    let index = 0;
    const peek = () => tokens[index];
    const consume = () => tokens[index++];

    const toNumber = (value: number | boolean) => (value ? 1 : 0);

    const parsePrimary = (): number | boolean => {
        const token = consume();
        if (!token) {
            throw new Error("Unexpected end of condition");
        }
        if (token.type === "number") {
            return token.value;
        }
        if (token.type === "lparen") {
            const value = parseOr();
            const closing = consume();
            if (!closing || closing.type !== "rparen") {
                throw new Error("Missing closing parenthesis");
            }
            return value;
        }
        throw new Error("Invalid token in condition");
    };

    const parseComparison = (): boolean => {
        const leftValue = parsePrimary();
        const nextToken = peek();
        if (nextToken && nextToken.type === "operator" && !["&&", "||"].includes(nextToken.value)) {
            const operatorToken = consume() as { type: "operator"; value: string };
            const rightValue = parsePrimary();
            const left = typeof leftValue === "number" ? leftValue : toNumber(leftValue);
            const right = typeof rightValue === "number" ? rightValue : toNumber(rightValue);

            switch (operatorToken.value) {
                case "===":
                    return left === right;
                case "!==":
                    return left !== right;
                case "==":
                    return left === right;
                case "!=":
                    return left !== right;
                case ">":
                    return left > right;
                case "<":
                    return left < right;
                case ">=":
                    return left >= right;
                case "<=":
                    return left <= right;
                default:
                    return false;
            }
        }

        if (typeof leftValue === "number") {
            return leftValue !== 0;
        }
        return leftValue;
    };

    const parseAnd = (): boolean => {
        let value = parseComparison();
        while (true) {
            const token = peek();
            if (token?.type !== "operator" || token.value !== "&&") {
                break;
            }
            consume();
            value = value && parseComparison();
        }
        return value;
    };

    const parseOr = (): boolean => {
        let value = parseAnd();
        while (true) {
            const token = peek();
            if (token?.type !== "operator" || token.value !== "||") {
                break;
            }
            consume();
            value = value || parseAnd();
        }
        return value;
    };

    try {
        const result = parseOr();
        return index === tokens.length ? result : false;
    } catch (error) {
        console.warn("Invalid condition expression:", condition, error);
        return false;
    }
};

// Données pour le préremplissage automatique (pour les tests)
const noms = ["Smith", "Jordan", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
    "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres",
    "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"];

const prenoms = ["John", "Michael", "David", "James", "Robert", "Maria", "Jennifer", "Linda", "Elizabeth", "Patricia", "Barbara",
    "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle",
    "Dorothy", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen", "Amy",
    "Shirley", "Angela", "Helen", "Anna", "Brenda", "Pamela", "Nicole", "Samantha", "Katherine", "Emma", "Ruth", "Christine"];

const messageries = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"];

export default function ContactForm({ onSubmit, isLoading, departement = '78', mode = '' }: ContactFormProps) {
    const { t, currentLang } = useLanguage();
    const isProd = process.env.NODE_ENV === "production";
    const [formData, setFormData] = useState<FormData>({
        nom: "",
        prenom: "",
        email: "",
        arrondissement: "",
        agdref: "",
        statut: "",
        message: "",
        captcha: false,
        acceptation: false,
    });

    const [arrondissements, setArrondissements] = useState<Array<{ id: string, label: string }>>([]);
    const [statuts, setStatuts] = useState<Array<{ id: string, label: string }>>([]);
    const [errors, setErrors] = useState<Partial<FormData>>({});
    const urlArrondissement = useMemo(() => {
        if (departement === "78") {
            return "https://www.yvelines.gouv.fr/contenu/telechargement/29247/169330/file/bloc%201.2%20-%20Annexe%202_Liste%20des%20communes%20et%20arrondissements%201er%20janvier%202017.pdf";
        }
        if (departement === "91") {
            return "https://www.essonne.gouv.fr/contenu/telechargement/18579/158914/file/communes-arrondissements.pdf";
        }
        if (departement === "92") {
            return "https://www.hauts-de-seine.gouv.fr/layout/set/print/Services-de-l-Etat/Prefecture-et-Sous-Prefectures/Arrondissements";
        }
        if (departement === "94") {
            return "https://www.val-de-marne.gouv.fr/contenu/telechargement/14051/100949/file/Liste+des+communes.pdf";
        }
        return "";
    }, [departement]);
    const [initialCommune, setInitialCommune] = useState<string | undefined>(undefined);

    // Charger les arrondissements depuis l'API
    useEffect(() => {
        if (!isProd) {
            console.log("Fetching arrondissements and statuts from API");
        }
        fetch(`/api/v2/apps/delphes${departement}${mode}/${currentLang.toLowerCase() || "fr"}/case_model`)
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
                const departementNumber = parseInt(departement);

                // Filtrer selon la condition departement=={departement}
                // Inutile pour le 78 puisque l'usager choisit une commune dans le composant dédié
                const filtered = allowed.filter((item: any) => {
                    try {
                        if (!item.condition_javascript) return true;
                        return evaluateCondition(item.condition_javascript, departementNumber);
                    } catch (e) {
                        return false;
                    }
                });

                setArrondissements(filtered);

                // Chercher le case_field avec id 'statut'
                const statutField = caseFields.find((f: any) => f.id === 'statut');
                if (!statutField || !statutField.allowed_values) return;

                setStatuts(statutField.allowed_values);

                // Stocker les résultats pour la page d'analyse
                localStorage.setItem('status', JSON.stringify({
                    allowed_values: statutField.allowed_values,
                }));

                // Réinitialiser les valeurs si l'usager avait déjà rempli le formulaire
                const stored = localStorage.getItem('accueilEtrangers');
                if (stored) {
                    try {
                        const parsed = JSON.parse(stored);
                        if (parsed.fieldValues) {
                            setFormData((prev) => ({
                                ...prev,
                                ...parsed.fieldValues,
                                email: parsed.fieldValues.adresse_mail || prev.email,
                                agdref: parsed.fieldValues.numero_AGDREF || prev.agdref,
                                captcha: parsed.fieldValues.captcha !== undefined ? parsed.fieldValues.captcha : prev.captcha,
                                acceptation: true, // Forcer l'acceptation des CGU
                            }));
                        }
                    } catch (e) {
                        // Optionnel : log d'erreur
                        console.warn("Erreur lors de la lecture du localStorage accueilEtrangers", e);
                    }
                }
            })
            .catch(error => {
                console.error('Erreur lors du chargement des statuts et des arrondissements:', error);
                setArrondissements([{ id: "", label: "Impossible de charger les statuts et les arrondissements" }]);
            });
    }, [currentLang, departement, mode]);

    // Fonction de préremplissage pour les tests
    const preremplirFormulaire = () => {
        const randomNom = noms[Math.floor(Math.random() * noms.length)];
        const randomPrenom = prenoms[Math.floor(Math.random() * prenoms.length)];
        const randomEmail = `${randomNom.toLowerCase()}.${randomPrenom.toLowerCase()}@${messageries[Math.floor(Math.random() * messageries.length)]}`;
        const randomAgdref = departement + Math.floor(Math.random() * 100000000);

        // Pour le département 78, sélectionner une commune aléatoire
        let randomArrondissement = arrondissements.length > 0 ? arrondissements[0].id : "";
        let randomCommune: string | undefined = undefined;

        if (departement === "78" && communesYvelines.length > 0) {
            const randomCommuneData = communesYvelines[Math.floor(Math.random() * communesYvelines.length)];
            randomCommune = randomCommuneData.commune;
            // Déterminer le code d'arrondissement à partir de la commune
            const arrondissementCodes: Record<string, string> = {
                "Versailles": "VERS",
                "Rambouillet": "RAMB",
                "Saint-Germain-en-Laye": "SGEL",
                "Mantes-la-Jolie": "MLJ",
            };
            randomArrondissement = arrondissementCodes[randomCommuneData.arrondissement] || "";
        }

        setInitialCommune(randomCommune);
        setFormData({
            nom: randomNom,
            prenom: randomPrenom,
            email: randomEmail,
            arrondissement: randomArrondissement,
            agdref: randomAgdref,
            statut: "régulier",
            message: `${t('form.message.example')}\n\n${randomPrenom} ${randomNom}`,
            captcha: true,
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
        if (!formData.captcha) {
            (newErrors as any).captcha = t('form.error.captcha') || 'Veuillez confirmer que vous êtes une personne réelle';
        }
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

    const handleArrondissementChange = useCallback((value: string) => {
        setFormData(prev => ({ ...prev, arrondissement: value }));
        setErrors(prev => {
            if (prev.arrondissement) {
                return { ...prev, arrondissement: undefined };
            }
            return prev;
        });
        // Reinitialiser initialCommune apres le changement manuel
        setInitialCommune(undefined);
    }, []);

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

            {departement === "78" ? (
                <Arrondissement78
                    value={formData.arrondissement}
                    onChange={handleArrondissementChange}
                    error={errors.arrondissement}
                    initialCommune={initialCommune}
                />
            ) : (
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
                                    href={urlArrondissement}>
                                    {t('form.arrondissementLink' + "." + departement)}
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
            )}

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
                <div className={`fr-alert ${formData.captcha ? 'fr-alert--success' : 'fr-alert--warning'} fr-mb-3w`}>
                    <h3 className="fr-alert__title">{t('form.captcha')}</h3>
                    <div className="fr-checkbox-group">
                        <input
                            type="checkbox"
                            name="captcha"
                            id="captcha-verification"
                            required
                            className="fr-input"
                            checked={formData.captcha}
                            onChange={handleChange}
                            suppressHydrationWarning
                        />
                        <label htmlFor="captcha-verification" className="fr-label">
                            {t('form.captcha.label')} *
                        </label>
                    </div>
                    {(errors as any).captcha && <p className="fr-error-text">{(errors as any).captcha}</p>}
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
                        suppressHydrationWarning
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

                    {mode === 'test' && (
                        <button
                            type="button"
                            className="fr-btn fr-btn--secondary fr-ml-2w"
                            onClick={preremplirFormulaire}
                        >
                            {t('form.prefill')}
                        </button>
                    )}
                </div>
            </div>
        </form >
    );
}
