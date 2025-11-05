"use client";

import { Suspense, useEffect, useState, useRef } from "react";
import { marked } from 'marked';
import DOMPurify from 'dompurify';
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

interface AnalyzeResult {
    text_analysis_response?: {
        user_intention?: {
            intention_id?: string;
            intention_label?: string;
            intention_scoring?: number;
        }[];
        case_info?: Record<string, unknown>;
    };
    highlighted_text_and_features?: unknown;
}

interface HandleCaseContentProps {
    message: string | null;
    fieldValues: FieldValues | null;
    selectedIntention: string | null;
    intentionLabel: string | null;
    analyzeResult: AnalyzeResult | null;
}

function HandleCaseContent({ message, fieldValues, selectedIntention, intentionLabel, analyzeResult }: HandleCaseContentProps) {
    const { t, currentLang } = useLanguage();
    const [isLoading, setIsLoading] = useState(true);
    const [vueAgent, setVueAgent] = useState(false);
    const [vueAgentReponse, setVueAgentReponse] = useState(false);
    const [caseHandling, setCaseHandling] = useState<string | null>(null);
    const [answer, setAnswer] = useState<string | null>(null);
    const [ack, setAck] = useState<string | null>(null);

    const hasFetchedRef = useRef(false);

    const handleVueAgentReponseClick = () => {
        setVueAgentReponse(!vueAgentReponse);
    };

    const handleVueAgentClick = () => {
        setVueAgent(!vueAgent);
    };

    const handleCase = async () => {
        try {
            if (!fieldValues) {
                console.error('No field values provided');
                return;
            }

            if (!analyzeResult) {
                console.error('No analyze result available');
                return;
            }

            fieldValues.numero_AGDREF = fieldValues.agdref || undefined;
            delete fieldValues.agdref;
            delete fieldValues.message;

            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || '__NEXT_PUBLIC_API_URL__';
            if (!apiBaseUrl || apiBaseUrl.startsWith('__NEXT_PUBLIC_')) {
                console.warn('NEXT_PUBLIC_API_URL is not configured - API calls may not work');
                return;
            }

            console.log('Sending process request with payload', {
                case_request: {
                    intention_id: selectedIntention,
                    field_values: fieldValues,
                    highlighted_text_and_features: analyzeResult.highlighted_text_and_features,
                    lang: currentLang || 'fr'
                }
            });
            const handleCaseResponse = await fetch(`${apiBaseUrl}/api/v2/apps/delphes/${currentLang.toLowerCase() || 'fr'}/handle_case`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    intention_id: selectedIntention,
                    field_values: fieldValues,
                    highlighted_text_and_features: analyzeResult.highlighted_text_and_features,
                    decision_engine_config_id: "tests" // ce qui signigie qu'on utilise le moteur de décision en Python
                })
            });

            // if (!handleCaseResponse.ok) {
            //     throw new Error(`Erreur lors du traitement de la demande: ${handleCaseResponse.statusText}`);
            // }
            console.log('Résultat du handle case:', handleCaseResponse);
            const handleCaseResult = await handleCaseResponse.json();
            console.log('Résultat du handle case:', handleCaseResult);

            // Acknowledgement (Markdown -> sanitized HTML)
            const rawAck = handleCaseResult.case_handling_response?.acknowledgement_to_requester;
            let ackHtml: string | null = null;
            if (rawAck) {
                // Utilisation de marked.parse (synchrone) pour garantir un retour string
                const html: string = marked.parse(String(rawAck), { async: false }) as string;
                // parse HTML and add DSFR classes to links
                try {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const anchors = Array.from(doc.querySelectorAll('a'));
                    anchors.forEach(a => {
                        a.classList.add('fr-link', 'fr-link--icon-right', 'fr-icon-external-link-line', 'fr-mb-1w');
                        // always open links in a new tab and ensure safety attributes
                        a.setAttribute('target', '_blank');
                        const rel = a.getAttribute('rel') || '';
                        // ensure noopener and noreferrer are present
                        const relParts = new Set(rel.split(/\s+/).filter(Boolean));
                        relParts.add('noopener');
                        relParts.add('noreferrer');
                        a.setAttribute('rel', Array.from(relParts).join(' ').trim());
                    });
                    const modified = doc.body.innerHTML;
                    // Allow keeping target attribute (DOMPurify strips some attributes by default)
                    ackHtml = DOMPurify.sanitize(modified, { ADD_ATTR: ['target'] });
                } catch {
                    // fallback: sanitize original HTML
                    ackHtml = DOMPurify.sanitize(html, { ADD_ATTR: ['target'] });
                }
            }
            setAck(ackHtml);

            // Case Handling response
            setCaseHandling(handleCaseResult.case_handling_response?.case_handling_report[0]);

            // Réponse
            let answerText = handleCaseResult.case_handling_response?.case_handling_report[1];
            if (answerText) {
                // remplacer chaque saut de ligne par une balise &nbsp;<br /> pour l'affichage HTML
                answerText = answerText.replace(/\n/g, '&nbsp;<br />');
                // sanitize HTML to avoid XSS; allow keeping target attribute on links
                answerText = DOMPurify.sanitize(answerText, { ADD_ATTR: ['target'] });
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
        if (hasFetchedRef.current) return;
        hasFetchedRef.current = true;

        handleCase();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <>
            <Header departement={"" + fieldValues?.departement} />
            <main role="main" id="main" className="fr-container fr-py-6w">
                <div className="fr-grid-row fr-grid-row--gutters">
                    <div className="fr-col-12 fr-col-md-8 fr-col-offset-md-2">
                        <div className={isLoading ? "fr-alert fr-alert--info fr-mb-4w" : "fr-alert fr-alert--success fr-mb-4w"}>
                            <h1 className="fr-alert__title">{isLoading ? t('handleCase.alert.processing.title') : t('handleCase.alert.success.title')}</h1>
                            <p>
                                {t('handleCase.alert.greeting.start')} {fieldValues?.prenom} {fieldValues?.nom}, {t('handleCase.alert.greeting.end')}
                            </p>
                        </div>

                        <div className="fr-mb-4w">
                            <div className="fr-mt-1v">
                                <h3 className="fr-h6">{intentionLabel}</h3>
                                <div className="fr-text--sm" style={{
                                    fontStyle: 'italic',
                                    backgroundColor: '#f5f5fe',
                                    padding: '1rem',
                                    borderRadius: '4px',
                                    whiteSpace: 'pre-wrap'
                                }}>
                                    {message}
                                </div>
                            </div>
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
                                <div className="fr-alert fr-alert--info fr-mb-4w">
                                    <div
                                        className="ack-bold"
                                        dangerouslySetInnerHTML={{
                                            __html: ack || ""
                                        }}
                                    />
                                </div>
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
                                <h3 className="fr-h6">{t('handleCase.analysisResult', String(fieldValues?.prenom || ''), String(fieldValues?.nom || ''), String(fieldValues?.date_demande || ''))}</h3>
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
            </main >
            <Footer departement={"" + fieldValues?.departement} />
        </>
    );
}

export default function HandleCase() {
    const { t } = useLanguage();
    const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResult | null>(null);
    const [selectedIntention, setSelectedIntention] = useState<string | null>(null);
    const [intentionLabel, setIntentionLabel] = useState<string | null>(null);
    const [fieldValues, setFieldValues] = useState<FieldValues | null>(null);

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
        if (storedData2) {
            // selectedIntention is stored as a plain string, not JSON
            setSelectedIntention(storedData2);
        }

        const storedData3 = localStorage.getItem('intentionLabel');
        setIntentionLabel(storedData3)

        const storedData4 = localStorage.getItem('fieldValues');
        if (storedData4) {
            try {
                const parsedData = JSON.parse(storedData4);
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
            <HandleCaseContent
                message={typeof fieldValues.message === 'string' ? fieldValues.message : null}
                fieldValues={fieldValues}
                selectedIntention={selectedIntention}
                intentionLabel={intentionLabel}
                analyzeResult={analyzeResult}
            />
        </Suspense>
    );
}