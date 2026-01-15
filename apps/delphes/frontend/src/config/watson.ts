/**
 * Configuration Watson Orchestrate à partir des variables d'environnement
 */

export interface WatsonConfig {
    orchestrationID: string;
    hostURL: string;
    agentId: string;
    crn: string;
}

/**
 * Construit la configuration Watson à partir des variables d'environnement
 */
export function getWatsonConfig(): WatsonConfig {
    // Récupération des variables d'environnement (avec placeholders pour le runtime)
    const region = process.env.NEXT_PUBLIC_WATSON_REGION || '__NEXT_PUBLIC_WATSON_REGION__';
    const instanceId = process.env.NEXT_PUBLIC_WATSON_INSTANCE_ID || '__NEXT_PUBLIC_WATSON_INSTANCE_ID__';
    const integrationId = process.env.NEXT_PUBLIC_WATSON_INTEGRATION_ID || '__NEXT_PUBLIC_WATSON_INTEGRATION_ID__';
    const agentId = process.env.NEXT_PUBLIC_WATSON_AGENT_ID || '__NEXT_PUBLIC_WATSON_AGENT_ID__';

    // Si on a des placeholders, c'est qu'on est en mode runtime substitution
    if (region?.includes('__NEXT_PUBLIC_') ||
        instanceId?.includes('__NEXT_PUBLIC_') ||
        integrationId?.includes('__NEXT_PUBLIC_') ||
        agentId?.includes('__NEXT_PUBLIC_')) {

        if (process.env.NODE_ENV !== "production") {
            console.warn(
                "Variables Watson en mode placeholder - en attente de substitution runtime",
            );
        }
        // En mode runtime, on retourne des valeurs vides et on laisse le script faire la substitution
        return {
            orchestrationID: '',
            hostURL: '',
            agentId: '',
            crn: ''
        };
    }

    // Mode normal avec vraies variables d'environnement
    const finalRegion = region || 'us-south';

    // Construction des paramètres
    const orchestrationID = `${instanceId}_${integrationId}`;
    const hostURL = `https://${finalRegion}.watson-orchestrate.cloud.ibm.com`;
    const crn = `crn:v1:bluemix:public:watsonx-orchestrate:${finalRegion}:a/${instanceId}:${integrationId}::`;

    return {
        orchestrationID,
        hostURL,
        agentId: agentId || '',
        crn
    };
}

/**
 * Hook pour récupérer la configuration Watson
 */
export function useWatsonConfig(): WatsonConfig {
    return getWatsonConfig();
}
