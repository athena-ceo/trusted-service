"use client";

import { Suspense, useEffect, useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Loading from "@/components/Loading";
import "@/app/spinner.css";

function HandleCaseContent({ message, fieldValues, selectedIntention, analyzeResult }: { message: string | null, fieldValues: any, selectedIntention: any, analyzeResult: any }) {
    const [isLoading, setIsLoading] = useState(true);
    const [vueAgent, setVueAgent] = useState(false);
    const [vueAgentReponse, setVueAgentReponse] = useState(false);
    const [answer, setAnswer] = useState<string | null>(null);
    const [ack, setAck] = useState<string | null>(null);

    const handleVueAgentReponseClick = () => {
        setVueAgentReponse(!vueAgentReponse);
    };

    const handleVueAgentClick = () => {
        setVueAgent(!vueAgent);
    };

    const handleCase = async () => {
        try {
            fieldValues.numero_AGDREF = fieldValues.agdref || null;
            delete fieldValues.agdref;
            delete fieldValues.message;

            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '__NEXT_PUBLIC_API_URL__';
            if (!apiBaseUrl || apiBaseUrl.startsWith('__NEXT_PUBLIC_')) {
                console.warn('NEXT_PUBLIC_API_URL is not configured - API calls may not work');
                return;
            }

            const handleCaseResponse = await fetch(apiBaseUrl + '/api/v1/process_request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    case_request: {
                        intention_id: selectedIntention,
                        field_values: fieldValues,
                        highlighted_text_and_features: analyzeResult.highlighted_text_and_features,
                    },
                }),
            });

            // if (!handleCaseResponse.ok) {
            //     throw new Error(`Erreur lors du traitement de la demande: ${handleCaseResponse.statusText}`);
            // }
            console.log('Résultat du handle case:', handleCaseResponse);
            const handleCaseResult = await handleCaseResponse.json();
            console.log('Résultat du handle case:', handleCaseResult);

            // Acknowledgement
            setAck(handleCaseResult.case_handling_response?.acknowledgement_to_requester)

            // Réponse
            let answerText = handleCaseResult.case_handling_response?.case_handling_report[1];
            if (answerText) {
                // remplacer chaque saut de ligne par une balise &nbsp;<br /> pour l'affichage HTML
                answerText = answerText.replace(/\n/g, '&nbsp;<br />');
            }
            setAnswer(answerText);
        } catch (error) {
            console.error('Erreur lors du traitement de la demande:', error);
            // alert('Une erreur est survenue lors du traitement de la demande. Veuillez réessayer.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        handleCase();
    }, []);

    return (
        <>
            <Header />
            <main role="main" id="main" className="fr-container fr-py-6w">
                <div className="fr-grid-row fr-grid-row--gutters">
                    <div className="fr-col-12 fr-col-md-8 fr-col-offset-md-2">
                        <div className={isLoading ? "fr-alert fr-alert--info fr-mb-4w" : "fr-alert fr-alert--success fr-mb-4w"}>
                            <h1 className="fr-alert__title">{isLoading ? "Votre demande est en cours de réorientation vers le bon destinataire" : "Votre demande a été réorientée automatiquement vers le bon destinataire"}</h1>
                            <p>
                                Merci {fieldValues.prenom} {fieldValues.nom}, nous avons bien reçu votre demande et notre système
                                l'a analysée pour vous orienter vers le bon destinataire.
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
                                    {message}
                                </div>

                                {/* Spinner de chargement */}
                                {isLoading && (
                                    <div className="fr-grid-row fr-grid-row--center fr-mt-3w">
                                        <div className="fr-col-auto">
                                            <div className="fr-spinner fr-spinner--lg"></div>
                                        </div>
                                    </div>
                                )}

                                {/* Message d'accusé de réception */}
                                {!isLoading && (
                                    <div className="fr-mb-3w">
                                        <h3 className="fr-h6">Merci de votre patience</h3>
                                        <div
                                            className="fr-text--sm"
                                            dangerouslySetInnerHTML={{
                                                __html: `<p>${ack ? ack : ""}</p>`
                                            }}
                                        />
                                        <div className="fr-notice fr-notice--info fr-mb-4w">
                                            <div className="fr-container">
                                                <div className="fr-notice__body">
                                                    <p className="fr-notice__title fr-mr-3w">
                                                        Prochaines étapes
                                                    </p>
                                                    <p>
                                                        Un agent du service concerné examinera votre demande et vous contactera
                                                        si nécessaire à l'adresse email que vous avez fournie.
                                                        En général, nous répondons sous 5 jours ouvrés.
                                                    </p>
                                                </div>
                                            </div>
                                        </div>

                                        <hr />
                                        <button type="button" id="vue-agent" className="fr-btn fr-mt-3w" onClick={handleVueAgentClick}>
                                            Vue Agent
                                        </button>
                                    </div>
                                )}

                                {/* Résumé de l'analyse */}
                                {!isLoading && vueAgent && analyzeResult && analyzeResult.highlighted_text_and_features && (
                                    <div className="fr-mb-3w">
                                        <h3 className="fr-h6">Éléments identifiés dans votre message :</h3>
                                        <div
                                            className="fr-text--sm"
                                            dangerouslySetInnerHTML={{
                                                __html: `
                                                    <style>
                                                        .highlighted-content table td,
                                                        .highlighted-content table th {
                                                            padding: 1rem !important;
                                                        }
                                                        .highlighted-content table {
                                                            border-collapse: separate;
                                                            width: 100%;
                                                            border-spacing: 0;
                                                        }
                                                    </style>
                                                    <div class="highlighted-content">
                                                        ${analyzeResult.highlighted_text_and_features}
                                                    </div>
                                                `
                                            }}
                                        />
                                    </div>
                                )}

                                {/* field values */}
                                {!isLoading && vueAgent && fieldValues && (
                                    <div className="fr-mb-3w">
                                        <h3 className="fr-h6">Valeurs des champs :</h3>
                                        <ul className="fr-list">
                                            {Object.entries(fieldValues).map(([key, value]) => {
                                                const displayValue = value === null || value === undefined
                                                    ? 'null'
                                                    : typeof value === 'boolean'
                                                        ? value ? 'true' : 'false'
                                                        : typeof value === 'object'
                                                            ? JSON.stringify(value)
                                                            : String(value);

                                                return (
                                                    <li key={key} className="fr-mb-1w">
                                                        <strong>{key}:</strong> {displayValue}
                                                    </li>
                                                );
                                            })}
                                        </ul>
                                        <hr />
                                        <button type="button" id="vue-agent-reponse" className="fr-btn fr-mt-3w" onClick={handleVueAgentReponseClick}>
                                            Générer la réponse
                                        </button>
                                    </div>
                                )}

                                {/* Vue Réponse */}
                                {!isLoading && vueAgentReponse && (
                                    <div className="fr-mb-3w">
                                        <h3 className="fr-h6">Réponse générée :</h3>
                                        <div
                                            className="fr-text--sm"
                                            dangerouslySetInnerHTML={{
                                                __html: answer ? `<p>${answer}</p>` : "<p>Aucune réponse générée</p>"
                                            }}
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </main>
            <Footer />
        </>
    );
}

export default function HandleCase() {
    const [analyzeResult, setAnalyzeResult] = useState<any>(null);
    const [selectedIntention, setSelectedIntention] = useState<any>(null);
    const [fieldValues, setFieldValues] = useState<any>(null);

    useEffect(() => {
        // Récupération des données au chargement de la page
        const storedData1 = localStorage.getItem('analyzeResult');
        if (storedData1) {
            try {
                const parsedData = JSON.parse(storedData1);
                setAnalyzeResult(parsedData.analyzeResult);

                // Optionnel : nettoyer le localStorage après récupération
                // localStorage.removeItem('analyzeResult');
            } catch (error) {
                console.error('Erreur lors de la lecture des données de la requête:', error);
            }
        }

        const storedData2 = localStorage.getItem('selectedIntention');
        setSelectedIntention(storedData2)

        const storedData3 = localStorage.getItem('fieldValues');
        if (storedData3) {
            try {
                const parsedData = JSON.parse(storedData3);
                setFieldValues(parsedData);

                // Optionnel : nettoyer le localStorage après récupération
                // localStorage.removeItem('fieldValues');
            } catch (error) {
                console.error('Erreur lors de la lecture des données de la requête:', error);
            }
        }

    }, []); // Se déclenche une seule fois au montage du composant

    if (!fieldValues || !selectedIntention || !analyzeResult) {
        return <Loading message="Chargement des données de votre demande..." />;
    }
    return (
        <Suspense fallback={
            <Loading message="Chargement des données de votre demande..." />
        }>
            <HandleCaseContent message={fieldValues.message} fieldValues={fieldValues} selectedIntention={selectedIntention} analyzeResult={analyzeResult} />
        </Suspense>
    );
}