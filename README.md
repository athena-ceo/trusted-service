# Trusted Services README

Trusted Services is a framework to streamline the build of localized, accountable, self service applications.

You can create a new application either by using a Python API or by parameterizing in a low code fashion the framework through a xlsx.

This README shows the second approach on an example: The Delphes project (Projet de la Préfecture des Yvelines) that streamlines the experience of foreign requesters and improves the efficiency of back-office agents, while making the entire chain far more trustable than the legacy email-based approach.

Applications built with the framework implement an **accountable AI pattern** with 4 major components:
- The requester
- A LLM service
- A rule-based decision service
- The back-office agent

Both the requester and the agent are "humans in the loop", as they validate AI-generated findings.

More details can be found in the pptx in subdirectory `docs` of the current git repository. Also, to understand the architecture and design of the Trusted Services framework, you should check the UML diagram in `docs/trusted_services_uml.drawio`

This git repository comes with:
- The source codee for the Python library
- A generic Streamlit client
- The configuration file for the Delphes app

## Warning
If you migrate from the legacy Delphes POC, make sure you create the Thunderbird folders and update the matching filters according to the names below. Allow accentuated characters have been removed from the tags, folders and filters. 

## 1. INSTALLATION

### Install the framework and the sample application (Delphes)
Type `git clone https://github.com/athena-ceo/trusted-service.git`
Type `pip install -r requirements.txt`

### Specifically for the Delphes application, download, install and preconfigure Thunderbird
- Visit https://www.thunderbird.net/en-US/download/
- Crate folder `Bannettes` (right-click `pocagent78@gmail.com`) and the corresponding subfolders:
  - api-a-renouveler
  - generique
  - pref-etrangers-aes-salarie
  - reorientation
  - sauf-conduits
  - ukraine
- Create the corresponding filters, for instance, for `réorientation`
  - On the top-right: ☰  > Tools > Message Filters > New... 
  - Filter name: réorientation
  - Subject contains reorientation
  - Move Message to: reorientation
- Créer les étiquettes (Paramètres / Général / Etiquettes)
  - BASSE - Bleue
  - NORMALE - Verte
  - HAUTE - Orange
  - TRES_HAUTE - Rouge
- Créer les filtres correspondants, par exemple pour BASSE (menu Outils) :
  - Nom du filtre: BASSE
  - Sujet contient BASSE
  - Etiqueter le message BASSE
- **Attention** Pour le filtre HAUTE, ajouter la condition "ne contient pas TRES_HAUTE"



## 2. CONFIGURATION
E THE DELPHES APP (Projet des préfectures)
All configuration is done in `apps\delphes\runtime\configuration_delphes.xlsx`
Fields ar either self-explanatory or explained.

### Configure how the test client accesses the API
- The Streamlist test client can either connect to the API through function calls or through REST/http calls
- To configure how the test client accesses the API, switch the Excel file to tab `frontend`. Field `connection_to_api` has two possible values
  - `direct`: Direct access through Python function
  - `http`: http access to Uvicorn server.
    - In that case, you will need to launch the uvicorn server (see below) and to configure `http_connection_url` 
- *Warning* Currently `http` has an issue, so use `direct`.

### Configure what Decision Engine the API connects to
- The API either connects to ODM, Drools or a hardcoded engine (in the case of Delphes: `apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`)
- To configure hwhat Decision Engine the API connects to, switch the Excel file to tab `backend`. Field `decision_engine` has three possible values
  - `odm`: Connect to an ODM Decision Service
    - In that case, you will need to launch the ODM Docker image (see below) and to configure the `odm` tab 
  - `drools`: Connect to a Drools Decision Service
  - `apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`: Connect to a hardcoded Decision Service
- *Warning* Currently, only ODM works.

## 3. RUN THE APP

### Launch the ODM Docker image
```
cd apps/delphes/runtime/odm_databases/9.0
docker run -e LICENSE=accept -m 2048M --memory-reservation 2048M -p 9060:9060 -p 9443:9443 -v .:/config/dbdata/ -e SAMPLE=false icr.io/cpopen/odm-k8s/odm:9.0
```
*Important* The port specified with option `-p` should match the `decision_service_url` option in tab `odm`

### Launch the uvicorn server
In the `trusted-service` top directory, type:
```
fastapi dev launcher_fastapi.py --port 8002 
```
*Important* The port specified with option `--port` should match the `http_connection_url` option in tab `frontend`

### Launch the Delphes application
In the `trusted-service` top directory, type:
```
streamlit run launcher_streamlit.py apps/delphes/runtime/configuration_delphes.xlsx
```


