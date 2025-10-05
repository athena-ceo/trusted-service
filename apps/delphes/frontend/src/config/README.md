# Configuration Watson Orchestrate

## Variables d'environnement requises

Pour utiliser Watson Orchestrate, les variables d'environnement suivantes doivent être définies :

### Variables Watson
- `NEXT_PUBLIC_WATSON_REGION` : Région Watson (ex: `us-south`, `eu-de`)
- `NEXT_PUBLIC_WATSON_INSTANCE_ID` : ID de l'instance Watson 
- `NEXT_PUBLIC_WATSON_INTEGRATION_ID` : ID de l'intégration Watson
- `NEXT_PUBLIC_WATSON_AGENT_ID` : ID de l'agent Watson

### Construction automatique
À partir de ces variables, le système construit automatiquement :
- `orchestrationID` = `${INSTANCE_ID}_${INTEGRATION_ID}`
- `hostURL` = `https://${REGION}.watson-orchestrate.cloud.ibm.com`
- `crn` = `crn:v1:bluemix:public:watsonx-orchestrate:${REGION}:a/${INSTANCE_ID}:${INTEGRATION_ID}::`

## Fichiers de configuration

### `.env` (racine du projet)
Configuration partagée pour Docker et production

### `.env.local` (dans /frontend)
Configuration pour le développement local (ignoré par git)

## Exemple d'utilisation

```tsx
import { useWatsonConfig } from "@/config/watson";

function MyComponent() {
    const watsonConfig = useWatsonConfig();
    
    useWatsonOrchestrate({
        enabled: true,
        orchestrationID: watsonConfig.orchestrationID,
        hostURL: watsonConfig.hostURL,
        agentId: watsonConfig.agentId,
        crn: watsonConfig.crn,
        onActivated: () => console.log("Watson activé"),
        onButtonSetup: () => setupButtons()
    });
}
```