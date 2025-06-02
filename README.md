# Trusted Services README

Trusted Services is a framework to support and streamline the build of self service applicatioins. More details can be found in the pptx in docs.

Creating an app merely consists in parameterizing the framework with a pptx.

This git repository comes with:
- The source codee for the Python library
- A generic Streamlit client
- The configuration file for the Delphes app

To understand the architecture and design of the Trusted Services framework, check the UML diagram in docs/trusted_services_uml.drawio

## 1. INSTALL THE FRANEWORK AND THE SAMPLE DELPHES APP
Type `git clone https://github.com/athena-ceo/trusted-service.git`
Type `pip install -r requirements.txt`

## 2. CONFIGURE THE DELPHES APP (Projet des préfectures)
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


