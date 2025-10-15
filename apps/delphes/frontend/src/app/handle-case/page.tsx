"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Loading from "@/components/Loading";
import { useLanguage } from "@/contexts/LanguageContext";
import "@/app/spinner.css";

function HandleCaseContent({ message, fieldValues, selectedIntention, analyzeResult }: { message: string | null, fieldValues: any, selectedIntention: any, analyzeResult: any }) {
    const { t, currentLang } = useLanguage();
    const [isLoading, setIsLoading] = useState(true);
    const [vueAgent, setVueAgent] = useState(false);
    const [vueAgentReponse, setVueAgentReponse] = useState(false);
    const [caseHandling, setCaseHandling] = useState<string | null>(null);
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
                        lang: currentLang || 'fr'
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

            // Case Handling response
            setCaseHandling(handleCaseResult.case_handling_response?.case_handling_report[0]);

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
                            <h1 className="fr-alert__title">{isLoading ? t('handleCase.alert.processing.title') : t('handleCase.alert.success.title')}</h1>
                            <p>
                                {t('handleCase.alert.greeting.start')} {fieldValues.prenom} {fieldValues.nom}, {t('handleCase.alert.greeting.end')}
                            </p>
                        </div>

                        <div className="fr-mb-4w">
                            <div className="fr-mt-1v">
                                <p><strong>{t('handleCase.yourMessage')}</strong></p>
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
                                        <h3 className="fr-h6">{t('handleCase.thanks')}</h3>
                                        <div
                                            className="fr-text--sm"
                                            dangerouslySetInnerHTML={{
                                                __html: ack || ""
                                            }}
                                        />
                                        <div className="fr-notice fr-notice--info fr-mb-4w">
                                            <div className="fr-container">
                                                <div className="fr-notice__body">
                                                    <p className="fr-notice__title fr-mr-3w">
                                                        {t('handleCase.nextSteps.title')}
                                                    </p>
                                                    <p>
                                                        {t('handleCase.nextSteps.message')}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>

                                        <hr />
                                        <button type="button" id="vue-agent" className="fr-btn fr-mt-3w" onClick={handleVueAgentClick}>
                                            {t('handleCase.agentView')}
                                        </button>
                                    </div>
                                )}

                                {/* Résumé de l'analyse */}
                                {!isLoading && vueAgent && (
                                    <div className="fr-mb-3w">
                                        <h3 className="fr-h6">{t('handleCase.analysisResult', fieldValues.prenom, fieldValues.nom, fieldValues.date_demande)}</h3>
                                        <style jsx>{`
                                            .highlighted-content table td,
                                            .highlighted-content table th {
                                                padding: 0.1rem !important;
                                            }
                                            .highlighted-content table {
                                                border-collapse: separate;
                                                width: 100%;
                                                border-spacing: 0;
                                            }
                                        `}</style>
                                        <div
                                            className="fr-text--sm highlighted-content"
                                            dangerouslySetInnerHTML={{
                                                __html: caseHandling || ""
                                            }}
                                        />
                                        <hr />
                                        <button type="button" id="vue-agent-reponse" className="fr-btn fr-mt-3w" onClick={handleVueAgentReponseClick}>
                                            {t('handleCase.generateResponse')}
                                        </button>
                                    </div>
                                )}

                                {/* field values */}
                                {/* {!isLoading && vueAgent && fieldValues && (
                                    <div className="fr-mb-3w">
                                        <h3 className="fr-h6">{t('handleCase.fieldValues')}</h3>
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
                                    </div>
                                )} */}

                                {/* Vue Réponse */}
                                {!isLoading && vueAgentReponse && (
                                    <div className="fr-mb-3w">
                                        <h3 className="fr-h6">{t('handleCase.generatedResponse')}</h3>
                                        <div
                                            className="fr-text--sm"
                                            dangerouslySetInnerHTML={{
                                                __html: answer || t('handleCase.noResponse')
                                            }}
                                        />
                                    </div>
                                )}

                                <div className="fr-grid-row fr-grid-row--gutters">
                                    <div className="fr-col-12">
                                        <Link href="/" className="fr-btn fr-btn--secondary">
                                            {t('analysis.backToHome')}
                                        </Link>
                                    </div>
                                </div>
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
    const { t } = useLanguage();
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
        return <Loading message={t('handleCase.loadingData')} />;
    }
    return (
        <Suspense fallback={
            <Loading message={t('handleCase.loadingData')} />
        }>
            <HandleCaseContent message={fieldValues.message} fieldValues={fieldValues} selectedIntention={selectedIntention} analyzeResult={analyzeResult} />
        </Suspense>
    );
}