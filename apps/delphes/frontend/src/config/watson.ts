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
    const region = process.env.NEXT_PUBLIC_WATSON_REGION || '__NEXT_PUBLIC_WATSON_REGION__' || 'us-south';
    const instanceId = process.env.NEXT_PUBLIC_WATSON_INSTANCE_ID || '__NEXT_PUBLIC_WATSON_INSTANCE_ID__';
    const integrationId = process.env.NEXT_PUBLIC_WATSON_INTEGRATION_ID || '__NEXT_PUBLIC_WATSON_INTEGRATION_ID__';
    const agentId = process.env.NEXT_PUBLIC_WATSON_AGENT_ID || '__NEXT_PUBLIC_WATSON_AGENT_ID__';

    // Validation des variables requises (skip en production avec placeholders)
    if (!instanceId || instanceId.startsWith('__NEXT_PUBLIC_')) {
        console.warn('NEXT_PUBLIC_WATSON_INSTANCE_ID is not configured - Watson features may not work');
    }
    if (!integrationId || integrationId.startsWith('__NEXT_PUBLIC_')) {
        console.warn('NEXT_PUBLIC_WATSON_INTEGRATION_ID is not configured - Watson features may not work');
    }
    if (!agentId || agentId.startsWith('__NEXT_PUBLIC_')) {
        console.warn('NEXT_PUBLIC_WATSON_AGENT_ID is not configured - Watson features may not work');
    }

    // Construction des paramètres (avec gestion des placeholders)
    const orchestrationID = `${instanceId}_${integrationId}`;
    const hostURL = `https://${region}.watson-orchestrate.cloud.ibm.com`;
    const crn = `crn:v1:bluemix:public:watsonx-orchestrate:${region}:a/${instanceId}:${integrationId}::`;

    return {
        orchestrationID: orchestrationID.includes('__NEXT_PUBLIC_') ? '' : orchestrationID,
        hostURL: hostURL.includes('__NEXT_PUBLIC_') ? '' : hostURL,
        agentId: agentId?.startsWith('__NEXT_PUBLIC_') ? '' : agentId || '',
        crn: crn.includes('__NEXT_PUBLIC_') ? '' : crn
    };
}

/**
 * Hook pour récupérer la configuration Watson
 */
export function useWatsonConfig(): WatsonConfig {
    return getWatsonConfig();
}