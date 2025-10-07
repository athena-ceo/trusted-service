"use client";

import { useEffect, useRef } from "react";

interface WatsonOrchestrateConfig {
    orchestrationID: string;
    hostURL: string;
    rootElementID: string;
    deploymentPlatform: string;
    crn: string;
    chatOptions: {
        agentId: string;
    };
}

interface UseWatsonOrchestrateOptions {
    enabled: boolean;
    orchestrationID: string;
    hostURL: string;
    agentId: string;
    onActivated: () => void;
    onButtonSetup?: () => void;
    rootElementID?: string;
    deploymentPlatform?: string;
    crn?: string;
}

export const useWatsonOrchestrate = ({
    enabled,
    orchestrationID,
    hostURL,
    agentId,
    onActivated,
    onButtonSetup,
    rootElementID = "watson-chat-container",
    deploymentPlatform = "ibmcloud",
    crn
}: UseWatsonOrchestrateOptions) => {
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const scriptElementRef = useRef<HTMLScriptElement | null>(null);

    // Construction de la configuration à partir des paramètres
    const finalConfig: WatsonOrchestrateConfig = {
        orchestrationID,
        hostURL,
        rootElementID,
        deploymentPlatform,
        crn: crn || `crn:v1:bluemix:public:watsonx-orchestrate:us-south:a/${orchestrationID.split('_')[0]}:${orchestrationID.split('_')[1]}::`,
        chatOptions: {
            agentId,
        }
    };

    useEffect(() => {
        if (!enabled) {
            return;
        }

        // Marquer Watson comme activé
        onActivated();

        // S'assurer que l'élément container existe avant de configurer Watson
        const container = document.getElementById(finalConfig.rootElementID);
        if (!container) {
            console.error('Watson container not found');
            return;
        }

        // Configuration Watson Orchestrate AVANT le chargement du script
        (window as any).wxOConfiguration = finalConfig;

        // Chargement du script Watson Orchestrate avec délai
        timerRef.current = setTimeout(() => {
            // Vérifier qu'aucun script Watson n'est déjà chargé
            const existingScript = document.querySelector('script[src*="wxoLoader.js"]');
            if (existingScript) {
                try {
                    if (existingScript.remove) {
                        existingScript.remove();
                    } else if (existingScript.parentNode) {
                        existingScript.parentNode.removeChild(existingScript);
                    }
                } catch (error) {
                    console.warn('Impossible de supprimer le script existant:', error);
                }
            }

            scriptElementRef.current = document.createElement('script');
            scriptElementRef.current.src = `${finalConfig.hostURL}/wxochat/wxoLoader.js?embed=true`;
            scriptElementRef.current.async = true;

            scriptElementRef.current.addEventListener('load', () => {
                // Re-forcer la configuration au cas où
                if ((window as any).wxOConfiguration) {
                    (window as any).wxOConfiguration.rootElementID = finalConfig.rootElementID;
                }

                if ((window as any).wxoLoader) {
                    try {
                        (window as any).wxoLoader.init();

                        // Une fois Watson chargé, déplacer le container en bas et le redimensionner
                        setTimeout(() => {
                            const container = document.getElementById(finalConfig.rootElementID);
                            if (container) {
                                // Déplacer en bas de la page
                                document.body.appendChild(container);

                                // Callback pour configurer les boutons personnalisés
                                onButtonSetup?.();
                            }
                        }, 1000);
                    } catch (error) {
                        console.error('Watson init error:', error);
                    }
                }
            });

            scriptElementRef.current.addEventListener('error', (error) => {
                console.error('Watson script loading error:', error);
            });

            if (document.head) {
                document.head.appendChild(scriptElementRef.current);
            }
        }, 1000); // Délai pour s'assurer que le DOM est prêt

        // Cleanup function
        return () => {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        };
    }, [enabled, onActivated, onButtonSetup, finalConfig]);

    return {
        config: finalConfig
    };
};