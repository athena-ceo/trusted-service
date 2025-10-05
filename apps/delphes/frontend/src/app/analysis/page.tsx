"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Loading from "@/components/Loading";
import "@/app/spinner.css";

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

function AnalysisContent({ fieldValues }: { fieldValues: any }) {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(true);
    const [scoringsPositifs, setScoringsPositifs] = useState<any[]>([]);
    const [selectedIntention, setSelectedIntention] = useState<string>('');
    const [fieldInputValues, setFieldInputValues] = useState<Record<string, string>>({});

    const analyzeRequest = async () => {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '__NEXT_PUBLIC_API_URL__';
            if (!apiBaseUrl || apiBaseUrl.startsWith('__NEXT_PUBLIC_')) {
                console.warn('NEXT_PUBLIC_API_URL is not configured - API calls may not work');
                return;
            }

            const analyzeResponse = await fetch(apiBaseUrl + '/api/v1/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_values: fieldValues,
                    text: fieldValues.message,
                }),
            });

            const analyzeResult = await analyzeResponse.json();
            console.log('Résultat de l\'analyse:', analyzeResult);

            // Sauver la date d'expiration de l'API
            fieldValues.date_expiration_api = analyzeResult.analysis_result.date_expiration_api;
            fieldValues.refugie_ou_protege_subsidiaire = analyzeResult.analysis_result.refugie_ou_protege_subsidiaire === true;
            fieldValues.mention_de_risque_sur_l_emploi = analyzeResult.analysis_result.mention_de_risque_sur_l_emploi === true;

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
        analyzeRequest();
    }, []);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        const formData = new FormData(event.target as HTMLFormElement);
        const selectedIntentionValue = formData.get('intention');

        if (!selectedIntentionValue) {
            alert('Veuillez sélectionner une intention avant de valider.');
            return;
        }
        // Si l'intention avait des champs, vérifier qu'ils sont tous remplis
        const intentionDetails = scoringsPositifs.find(item => item.intention_id === selectedIntentionValue);
        if (intentionDetails) {
            for (const champ of intentionDetails.intention_fields) {
                const fieldValue = formData.get(champ);
                if (!fieldValue || (typeof fieldValue === 'string' && fieldValue.trim() === '')) {
                    alert(`Veuillez remplir le champ requis : ${champ}`);
                    return;
                }
                // Sauvegarder la valeur dans fieldValues
                if (champ === 'date_expiration_api') {
                    fieldValues[champ] = convertISOToDate(fieldValue.toString());
                } else if (champ === 'refugie_ou_protege_subsidiaire') {
                    fieldValues[champ] = fieldValue === 'true';
                } else {
                    fieldValues[champ] = fieldValue;
                }
            }
        }

        // Sauvegarder l'intention choisie
        console.log('Intention choisie:', selectedIntentionValue.toString());
        localStorage.setItem('selectedIntention', selectedIntentionValue.toString());
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
        if (champ === 'refugie_ou_protege_subsidiaire') {
            console.log(`Valeur du champ booléen avant retour: ${fieldInputValues[champ]}`);
        }
        if (fieldInputValues[champ] !== undefined) {
            return fieldInputValues[champ];
        }

        // Sinon, utiliser la valeur par défaut si disponible
        if (champ === 'date_expiration_api' && fieldValues.date_expiration_api) {
            return convertDateToISO(fieldValues.date_expiration_api);
        } else if (champ === 'refugie_ou_protege_subsidiaire') {
            return fieldValues.refugie_ou_protege_subsidiaire ? 'true' : 'false';
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
                            <h1 className="fr-alert__title">{isLoading ? "Votre demande est en cours de traitement automatique" : "Votre demande a été analysée automatiquement"}</h1>
                            <p>
                                Merci {fieldValues.prenom} {fieldValues.nom}, nous avons bien reçu votre demande et notre système
                                l'analyse pour vous orienter vers le bon service.
                            </p>
                        </div>

                        <div className="fr-mb-4w">
                            <div className="fr-mt-1v">
                                <p><strong>Votre message :</strong></p>
                                <div className="fr-text--sm" style={{
                                    fontStyle: 'italic',
                                    backgroundColor: '#f5f5fe',
                                    padding: '1rem',
                                    borderRadius: '4px',
                                    whiteSpace: 'pre-wrap'
                                }}>
                                    {fieldValues.message}
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
                                        <p><strong>Veuillez sélectionner le cas qui s'applique à votre situation.</strong></p>
                                        <fieldset className="fr-fieldset" id="radio-intentions" aria-labelledby="radio-intentions-legend radio-intentions-messages">
                                            <legend className="fr-fieldset__legend--regular fr-fieldset__legend" id="radio-intentions-legend">
                                                L'IA a identifié {scoringsPositifs.length} cas correspondant à votre demande.<br />Votre sélection : *
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
                                                        {selectedIntention === intention.intention_id && (
                                                            intention.intention_fields.map((champ: string, index: number) => (
                                                                <div className="fr-input-group fr-text--sm" key={index} style={{ marginLeft: '2em', backgroundColor: '#f6f6f6', padding: '1rem', borderRadius: '4px' }}>
                                                                    <label className="fr-label" htmlFor={champ}>
                                                                        {champ === 'date_expiration_api' ? 'Date d\'expiration de l\'API' :
                                                                            champ === 'refugie_ou_protege_subsidiaire' ? 'Réfugié ou protégé subsidiaire' :
                                                                                champ} *
                                                                        {champ === 'date_expiration_api' && <span className="fr-hint-text">Format attendu : JJ/MM/AAAA</span>}
                                                                    </label>

                                                                    {/* Traitement spécial pour le champ booléen */}
                                                                    {champ === 'refugie_ou_protege_subsidiaire' ? (
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
                                                                                        Oui
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
                                                                                        Non
                                                                                    </label>
                                                                                </div>
                                                                            </div>
                                                                        </fieldset>
                                                                    ) : (
                                                                        /* Champs normaux (texte ou date) */
                                                                        <input
                                                                            className="fr-input"
                                                                            aria-describedby={`${champ}-messages`}
                                                                            id={champ}
                                                                            name={champ}
                                                                            type={champ === 'date_expiration_api' ? 'date' : 'text'}
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
                                        <button type="submit" id="bouton-valider" className="fr-btn fr-mt-3w">Valider</button>
                                    </form>
                                )}
                                {!isLoading && scoringsPositifs.length === 0 && (
                                    <div className="fr-mt-3w">
                                        <p><strong>Résultats de l'analyse automatique</strong></p>
                                        <p>Notre système n'a pas pu identifier d'intention claire dans votre message. Veuillez reformuler votre demande.</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="fr-grid-row fr-grid-row--gutters">
                            <div className="fr-col-12">
                                <Link href="/" className="fr-btn fr-btn--secondary">
                                    Retour à l'accueil
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

import Link from "next/link";

export default function Analysis() {
    const [fieldValues, setFieldValues] = useState<any>(null);

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
        return <Loading message="Chargement des données de votre demande..." />;
    }
    return (
        <Suspense fallback={
            <Loading message="Chargement des données de votre demande..." />
        }>
            <AnalysisContent fieldValues={fieldValues} />
        </Suspense>
    );
}

