"use client";

import { useEffect, useState, Suspense, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Loading from "@/components/Loading";
import { useLanguage } from "@/contexts/LanguageContext";
import "@/app/spinner.css";

// TypeScript interfaces for better type safety
interface FieldValues {
    [key: string]: string | number | boolean | undefined;
}

interface Scoring {
    intention_id: string;
    intention_label: string;
    intention_scoring: number;
    intention_fields?: string[];
    extracted_info?: Record<string, unknown>;
}

/**
 * Convertit une date au format français (JJ/MM/AAAA) vers le format ISO (AAAA-MM-JJ)
 * @param dateStr - Date au format "JJ/MM/AAAA"
 * @returns Date au format ISO "AAAA-MM-JJ" ou chaîne vide si invalide
 */
function convertDateToISO(dateStr: string): string {
    if (!dateStr || typeof dateStr !== 'string') return '';

    const dateParts = dateStr.split('/');
    if (dateParts.length !== 3) return '';

    const [day, month, year] = dateParts;

    // Validation basique des parties de date
    if (!day || !month || !year) return '';
    if (day.length !== 2 || month.length !== 2 || year.length !== 4) return '';

    // Formatage avec padding si nécessaire
    const paddedDay = day.padStart(2, '0');
    const paddedMonth = month.padStart(2, '0');

    return `${year}-${paddedMonth}-${paddedDay}`;
}

/**
 * Convertit une date au format ISO (AAAA-MM-JJ) vers le format français (JJ/MM/AAAA)
 * @param isoDateStr - Date au format ISO "AAAA-MM-JJ"
 * @returns Date au format français "JJ/MM/AAAA" ou chaîne vide si invalide
 */
function convertISOToDate(isoDateStr: string): string {
    if (!isoDateStr || typeof isoDateStr !== 'string') return '';

    const dateParts = isoDateStr.split('-');
    if (dateParts.length !== 3) return '';

    const [year, month, day] = dateParts;

    // Validation basique des parties de date
    if (!year || !month || !day) return '';
    if (year.length !== 4 || month.length !== 2 || day.length !== 2) return '';

    // Formatage avec padding si nécessaire
    const paddedDay = day.padStart(2, '0');
    const paddedMonth = month.padStart(2, '0');

    return `${paddedDay}/${paddedMonth}/${year}`;
}

function AnalysisContent({ fieldValues }: { fieldValues: FieldValues | null }) {
    const router = useRouter();
    const { t, currentLang } = useLanguage();
    const [isLoading, setIsLoading] = useState(true);
    const [scoringsPositifs, setScoringsPositifs] = useState<Scoring[]>([]);
    const [selectedIntention, setSelectedIntention] = useState<string>('');
    const [fieldInputValues, setFieldInputValues] = useState<Record<string, string>>({});
    const [statusOptions, setStatusOptions] = useState<Array<{ id: string, label: string }>>([]);

    const hasFetchedRef = useRef(false);

    const analyzeRequest = async () => {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '__NEXT_PUBLIC_API_URL__';
            if (!apiBaseUrl || apiBaseUrl.startsWith('__NEXT_PUBLIC_')) {
                console.warn('NEXT_PUBLIC_API_URL is not configured - API calls may not work');
                return;
            }

            if (!fieldValues) {
                console.error('No field values provided');
                return;
            }

            console.log('Sending analysis request with payload', fieldValues)
            const analyzeResponse = await fetch(apiBaseUrl + '/api/v1/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_values: fieldValues,
                    text: fieldValues.message || '',
                    lang: currentLang || 'fr'
                }),
            });

            const analyzeResult = await analyzeResponse.json();
            console.log('Résultat de l\'analyse:', analyzeResult);

            // Sauver les champs supplémentaires retournés par l'API
            fieldValues.date_expiration_api = analyzeResult.analysis_result.date_expiration_api;
            fieldValues.date_expiration_recepisse = analyzeResult.analysis_result.date_expiration_recepisse;
            fieldValues.date_expiration_titre_sejour = analyzeResult.analysis_result.date_expiration_titre_sejour;
            fieldValues.refugie_ou_protege_subsidiaire = analyzeResult.analysis_result.refugie_ou_protege_subsidiaire === true;
            fieldValues.mention_de_risque_sur_l_emploi = analyzeResult.analysis_result.mention_de_risque_sur_l_emploi === true;
            fieldValues.motif_deces = analyzeResult.analysis_result.motif_deces === true;
            fieldValues.demandeur_d_asile = analyzeResult.analysis_result.demandeur_d_asile === true;

            // Stocker les résultats pour la page de confirmation
            localStorage.setItem('analyzeResult', JSON.stringify({
                analyzeResult: analyzeResult,
            }));

            // Lister les intentions à score positif
            setScoringsPositifs(analyzeResult.analysis_result.scorings.filter((item: { score: number }) => item.score > 0));

        } catch (error) {
            console.error('Erreur lors de l\'analyse de la demande:', error);
            alert('Une erreur est survenue lors de l\'envoi de votre demande. Veuillez réessayer.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        const stored = localStorage.getItem('status');
        if (stored) {
            try {
                const parsed = JSON.parse(stored);
                if (parsed.allowed_values) {
                    setStatusOptions(parsed.allowed_values);
                }
            } catch (e) {
                // Optionnel : log d’erreur
                console.warn("Erreur lors de la lecture du localStorage status", e);
            }
        }

        if (hasFetchedRef.current) return;
        hasFetchedRef.current = true;

        analyzeRequest();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        const formData = new FormData(event.target as HTMLFormElement);
        const selectedIntentionValue = formData.get('intention');

        if (!selectedIntentionValue) {
            alert('Veuillez sélectionner une intention avant de valider.');
            return;
        }

        if (!fieldValues) {
            console.error('No field values available');
            return;
        }

        // Si l'intention avait des champs, vérifier qu'ils sont tous remplis
        const intentionDetails = scoringsPositifs.find(item => item.intention_id === selectedIntentionValue);
        if (intentionDetails && intentionDetails.intention_fields) {
            for (const champ of intentionDetails.intention_fields) {
                const fieldValue = formData.get(champ);
                if (!fieldValue || (typeof fieldValue === 'string' && fieldValue.trim() === '')) {
                    alert(`Veuillez remplir le champ requis : ${champ}`);
                    return;
                }
                // Sauvegarder la valeur dans fieldValues
                if (champ === 'date_expiration_api' || champ === 'date_expiration_recepisse' || champ === 'date_expiration_titre_sejour') {
                    fieldValues[champ] = convertISOToDate(fieldValue.toString());
                } else if (champ === 'refugie_ou_protege_subsidiaire' || champ === 'motif_deces' || champ === 'demandeur_d_asile') {
                    fieldValues[champ] = fieldValue === 'true';
                } else {
                    fieldValues[champ] = fieldValue;
                }
            }
        }

        // Sauvegarder l'intention choisie
        localStorage.setItem('selectedIntention', selectedIntentionValue.toString());
        localStorage.setItem('intentionLabel', scoringsPositifs.find(item => item.intention_id === selectedIntentionValue)?.intention_label || '');
        localStorage.setItem('fieldValues', JSON.stringify(fieldValues));

        // Rediriger vers la page de confirmation
        router.push('/handle-case');
    }

    const handleIntentionChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedIntention(event.target.value);
    }

    const handleFieldChange = (fieldKey: string, value: string) => {
        setFieldInputValues(prev => ({
            ...prev,
            [fieldKey]: value
        }));
    }

    const getFieldValue = (champ: string): string => {
        // Si on a déjà une valeur saisie, l'utiliser
        if (champ === 'refugie_ou_protege_subsidiaire' || champ === 'motif_deces' || champ === 'demandeur_d_asile') {
            console.log(`Valeur du champ booléen avant retour: ${fieldInputValues[champ]}`);
        }
        if (fieldInputValues[champ] !== undefined) {
            return fieldInputValues[champ];
        }

        // Guard against null fieldValues
        if (!fieldValues) {
            return '';
        }

        // Sinon, utiliser la valeur par défaut si disponible
        if (champ === 'date_expiration_api' && fieldValues.date_expiration_api) {
            return convertDateToISO(fieldValues.date_expiration_api);
        } else if (champ === 'date_expiration_recepisse' && fieldValues.date_expiration_recepisse) {
            return convertDateToISO(fieldValues.date_expiration_recepisse);
        } else if (champ === 'date_expiration_titre_sejour' && fieldValues.date_expiration_titre_sejour) {
            return convertDateToISO(fieldValues.date_expiration_titre_sejour);
        } else if (champ === 'refugie_ou_protege_subsidiaire') {
            return fieldValues.refugie_ou_protege_subsidiaire ? 'true' : 'false';
        } else if (champ === 'motif_deces') {
            return fieldValues.motif_deces ? 'true' : 'false';
        } else if (champ === 'demandeur_d_asile') {
            return fieldValues.demandeur_d_asile ? 'true' : 'false';
        } else if (fieldValues[champ]) {
            return fieldValues[champ];
        }

        return '';
    }

    return (
        <>
            <Header />
            <main role="main" id="main" className="fr-container fr-py-6w">
                <div className="fr-grid-row fr-grid-row--gutters">
                    <div className="fr-col-12 fr-col-md-8 fr-col-offset-md-2">
                        <div className={isLoading ? "fr-alert fr-alert--info fr-mb-4w" : "fr-alert fr-alert--success fr-mb-4w"}>
                            <h1 className="fr-alert__title">{isLoading ? t('analysis.alert.processing.title') : t('analysis.alert.success.title')}</h1>
                            <p>
                                {t('analysis.alert.greeting.start')} {fieldValues?.prenom} {fieldValues?.nom}, {t('analysis.alert.greeting.end')}
                            </p>
                        </div>

                        <div className="fr-mb-4w">
                            <div className="fr-mt-1v">
                                <p><strong>{t('analysis.yourMessage')}</strong></p>
                                <div className="fr-text--sm" style={{
                                    fontStyle: 'italic',
                                    backgroundColor: '#f5f5fe',
                                    padding: '1rem',
                                    borderRadius: '4px',
                                    whiteSpace: 'pre-wrap'
                                }}>
                                    {fieldValues?.message}
                                </div>

                                {/* Spinner de chargement */}
                                {isLoading && (
                                    <div className="fr-grid-row fr-grid-row--center fr-mt-3w">
                                        <div className="fr-col-auto">
                                            <div className="fr-spinner fr-spinner--lg"></div>
                                        </div>
                                    </div>
                                )}

                                {/* Formulaire pour le choix de l'intention */}
                                {!isLoading && scoringsPositifs.length > 0 && (
                                    <form id="intentions-form" onSubmit={handleSubmit}>
                                        <p><strong>{t('analysis.form.selectPrompt')}</strong></p>
                                        <fieldset className="fr-fieldset" id="radio-intentions" aria-labelledby="radio-intentions-legend radio-intentions-messages">
                                            <legend className="fr-fieldset__legend--regular fr-fieldset__legend" id="radio-intentions-legend">
                                                {t('analysis.form.aiIdentified')} {scoringsPositifs.length} {t('analysis.form.cases')}<br />{t('analysis.form.yourSelection')} *
                                            </legend>
                                            {scoringsPositifs.map((intention, index) => (
                                                <div className="fr-fieldset__element" key={index}>
                                                    <div className="fr-radio-group">
                                                        <input
                                                            type="radio"
                                                            id={intention.intention_id}
                                                            name="intention"
                                                            value={intention.intention_id}
                                                            onChange={handleIntentionChange}
                                                            required
                                                        />
                                                        <label className="fr-label" htmlFor={intention.intention_id}>
                                                            {intention.intention_label}
                                                        </label>
                                                        {/* Champ caché pour stocker le label correspondant */}
                                                        <input
                                                            type="hidden"
                                                            name={`intention_label_${intention.intention_id}`}
                                                            value={intention.intention_label}
                                                        />

                                                        {/* Champs spécifiques aux intentions */}
                                                        {selectedIntention === intention.intention_id && intention.intention_fields && (
                                                            intention.intention_fields.map((champ: string, index: number) => (
                                                                <div className="fr-input-group fr-text--sm" key={index} style={{ marginLeft: '2em', backgroundColor: '#f6f6f6', padding: '1rem', borderRadius: '4px' }}>
                                                                    <label className="fr-label" htmlFor={champ}>
                                                                        {t('analysis.form.fields.' + champ)} *
                                                                        {(champ === 'date_expiration_api' || champ === 'date_expiration_recepisse' || champ === 'date_expiration_titre_sejour') && <span className="fr-hint-text">{t('analysis.form.fields.dateFormat')}</span>}
                                                                    </label>

                                                                    {/* Traitement spécial pour le champ booléen */}
                                                                    {(champ === 'refugie_ou_protege_subsidiaire' || champ === 'motif_deces' || champ === 'demandeur_d_asile') ? (
                                                                        <fieldset className="fr-fieldset">
                                                                            <div className="fr-fieldset__element">
                                                                                <div className="fr-radio-group">
                                                                                    <input
                                                                                        type="radio"
                                                                                        id={`${champ}-oui`}
                                                                                        name={champ}
                                                                                        value="true"
                                                                                        checked={getFieldValue(champ) === 'true'}
                                                                                        onChange={(e) => handleFieldChange(champ, e.target.value)}
                                                                                        required
                                                                                    />
                                                                                    <label className="fr-label" htmlFor={`${champ}-oui`}>
                                                                                        {t('analysis.form.fields.yes')}
                                                                                    </label>
                                                                                </div>
                                                                            </div>
                                                                            <div className="fr-fieldset__element">
                                                                                <div className="fr-radio-group">
                                                                                    <input
                                                                                        type="radio"
                                                                                        id={`${champ}-non`}
                                                                                        name={champ}
                                                                                        value="false"
                                                                                        checked={getFieldValue(champ) === 'false'}
                                                                                        onChange={(e) => handleFieldChange(champ, e.target.value)}
                                                                                        required
                                                                                    />
                                                                                    <label className="fr-label" htmlFor={`${champ}-non`}>
                                                                                        {t('analysis.form.fields.no')}
                                                                                    </label>
                                                                                </div>
                                                                            </div>
                                                                        </fieldset>
                                                                    ) : (champ === 'statut') ? (
                                                                        /* Champ statut (ex: dropdown) - à personnaliser selon les besoins */
                                                                        <select
                                                                            className="fr-select"
                                                                            aria-describedby={`${champ}-messages`}
                                                                            id={champ}
                                                                            name={champ}
                                                                            value={getFieldValue(champ)}
                                                                            onChange={(e) => handleFieldChange(champ, e.target.value)}
                                                                            required
                                                                        >
                                                                            <option value="">{t('analysis.form.fields.selectOption')}</option>
                                                                            {statusOptions.map((option) => (
                                                                                <option key={option.id} value={option.id}>
                                                                                    {option.label}
                                                                                </option>
                                                                            ))}
                                                                        </select>
                                                                    ) : (
                                                                        /* Champs normaux (texte ou date) */
                                                                        <input
                                                                            className="fr-input"
                                                                            aria-describedby={`${champ}-messages`}
                                                                            id={champ}
                                                                            name={champ}
                                                                            type={(champ === 'date_expiration_api' || champ === 'date_expiration_recepisse' || champ === 'date_expiration_titre_sejour') ? 'date' : 'text'}
                                                                            value={getFieldValue(champ)}
                                                                            onChange={(e) => handleFieldChange(champ, e.target.value)}
                                                                            required
                                                                        />
                                                                    )}

                                                                    <div className="fr-messages-group" id={`${champ}-messages`} aria-live="assertive"> </div>
                                                                </div>
                                                            ))
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                            <div className="fr-messages-group" id="radio-intentions-messages" aria-live="assertive" />
                                        </fieldset>
                                        <button type="submit" id="bouton-valider" className="fr-btn fr-mt-3w">{t('analysis.form.validate')}</button>
                                    </form>
                                )}
                                {!isLoading && scoringsPositifs.length === 0 && (
                                    <div className="fr-mt-3w">
                                        <p><strong>{t('analysis.noResults.title')}</strong></p>
                                        <p>{t('analysis.noResults.message')}</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="fr-grid-row fr-grid-row--gutters">
                            <div className="fr-col-12">
                                <Link href="/" className="fr-btn fr-btn--secondary">
                                    {t('analysis.backToHome')}
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
            <Footer />
        </>
    );
}

export default function Analysis() {
    const { t } = useLanguage();
    const [fieldValues, setFieldValues] = useState<FieldValues | null>(null);

    useEffect(() => {
        // Récupération des données au chargement de la page
        const storedData = localStorage.getItem('accueilEtrangers');

        if (storedData) {
            try {
                const parsedData = JSON.parse(storedData);
                // Corriger : récupérer les fieldValues depuis parsedData.fieldValues
                setFieldValues(parsedData.fieldValues);

                // Optionnel : nettoyer le localStorage après récupération
                // localStorage.removeItem('accueilEtrangers');
            } catch (error) {
                console.error('Erreur lors de la lecture des données de la requête:', error);
            }
        }
    }, []); // Se déclenche une seule fois au montage du composant

    if (!fieldValues) {
        return <Loading message={t('analysis.loadingData')} />;
    }
    return (
        <Suspense fallback={
            <Loading message={t('analysis.loadingData')} />
        }>
            <AnalysisContent fieldValues={fieldValues} />
        </Suspense>
    );
}

