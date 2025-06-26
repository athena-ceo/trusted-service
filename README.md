# Trusted Services README

Trusted Services is a framework that streamlines the build of localizable, accountable, self-service applications.

You can create a new application either by using a Python API or by parameterizing in a low code fashion the framework
through a xlsx.

This README shows the second approach on an example: The Delphes project (Projet de la Préfecture des Yvelines) that 
- streamlines the experience of foreigners requesting services related to their stay in France
- improves the efficiency of the back-office agents in charge of processing these requests
- makes the entire chain far more trustable than the legacy email-based approach.

Applications built with the framework implement an **accountable AI pattern** with 4 major components:
- The requester
- A LLM service
- A rule-based decision service
- The back-office agent

Both the requester and the agent are "humans in the loop", as they validate AI-generated findings.

More details can be found in the pptx in subdirectory `docs` of the current git repository. Also, to understand the
architecture and design of the Trusted Services framework, you should check the UML diagram in
`docs/trusted_services_uml.drawio`

This git repository comes with:

- The source code of the Python library
- A generic Streamlit test client
- The configuration file for the Delphes app provided as a sample

## Warning

If you migrate from the legacy Delphes POC, make sure you create the Thunderbird folders and update the matching filters
according to the instructions below. Accentuated characters have been removed from the tags, folders and filters.

## 1. INSTALLATION
### Install the framework and the sample application (Delphes)
Type
```
git clone https://github.com/athena-ceo/trusted-service.git
pip install -r requirements.txt
```

### Download and install Docker Desktop and the Official IBM Operational Decision Manager for Developers image if you need to use the ODM Decision Engine
Please follow the instructions in https://hub.docker.com/r/ibmcom/odm

### Specifically for the Delphes application, download and install Thunderbird
Visit https://www.thunderbird.net/en-US/download/

## 2. CONFIGURATION
Trusted Services apps are configured in an Excel file. For Delphes check `apps\delphes\runtime\configuration_delphes.xlsx` where fields are either self-explanatory or explained in a comment cell.

### Specifically for the Delphes application, configure Thunderbird
- Crate folder `Bannettes` (right-click `pocagent78@gmail.com`) and the corresponding subfolders: `api-a-renouveler`, `generique`, `pref-etrangers-aes-salarie`, `reorientation`, `sauf-conduits`, `ukraine`
- Create the corresponding filters, for instance, for `réorientation`:
    - Menu on the top-right: `☰  > Tools > Message Filters > New...`
    - `Filter name`: `reorientation`
    - `Subject contains`: `reorientation`
    - `Move Message to`: `reorientation`
- Create the tags:
    - Menu on the top-right: `☰  > Settings > General > Tags > New...`
    - Define the following tags and colors:
        - `VERY_LOW` - Black
        - `LOW` - Blue
        - `MEDIUM` - Green
        - `HIGH` - Orange
        - `VERY_HIGH` - Red
- Create the corresponding filters, for instance, for `LOW`:
    - Menu on the top-right: `☰  > Tools > Message Filters > New...`
    - `Filter name`: `LOW`
    - `Subject contains`: `LOW`
    - `Tag Message`: `LOW`
- **Warning** For filter `HIGH`, add the condition `does not contain VERY_HIGH`

### Configure how the test client accesses the API
- The Streamlist test client can either connect to the API through function calls or through REST calls
- To configure how the test client accesses the API, switch the Excel file to tab `frontend`. Field `connection_to_api`
  has two possible values
    - `direct`: Direct access through Python function
    - `rest`: REST calls to the Uvicorn server. In that case, you will need to launch the uvicorn server (see below) and to configure `rest_api_host` and `rest_api_port`

### Configure what Decision Engine the API connects to
- The API either connects to ODM, Drools or a hardcoded engine (in the case of Delphes:
  `apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`)
- To configure hwhat Decision Engine the API connects to, switch the Excel file to tab `backend`. Field
  `decision_engine` has three possible values
    - `odm`: Connect to an ODM Decision Service. In that case, you will need to launch the ODM Docker image (see below) and to configure the `odm` tab
    - `drools`: Connect to a Drools Decision Service
    - `apps.delphes.design_time.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`: Connect to a hardcoded Decision Service

## 3. RUN THE APP
Proceed in the following order:

### If you configured the Decision Engine to be ODM, launch the ODM Docker image
**Important notes**:
> **1. ODM Decision Center database persistence locale**
> 
> A given instance of the ODM Decision Center database has a native locale and cannot host rules with a different persitence locale.
> 
> To set the locale (en_US by default):
>> - launch the ODM Docker image
>> - remove all rules
>> - run `odm_dc_localization.py` in `src/backend/decision/decision_odm/admin`
>
> 3. ODM Version
> The `-v` option in the docker command ensure the Decision Center and RES databases are backed by a file.
> Nothing will ensure that the format of the files doesn't change. Therefore it is advised to have a directory per ODM version. 

This leads to the following command for Delphes!
```
cd apps/delphes/runtime/odm_databases/9.0
docker run -e LICENSE=accept -m 2048M --memory-reservation 2048M -p 9060:9060 -p 9443:9443 -v .:/config/dbdata/ -e SAMPLE=false icr.io/cpopen/odm-k8s/odm:9.0
```

### Unless you only want to launch the test client, and you configured that client to access the API directly, launch the uvicorn server
In the `trusted-service` top directory, type:
```
python launcher_uvicorn.py ./apps/delphes/runtime/configuration_delphes.xlsx
```

### Launch the test client
In the `trusted-service` top directory, type:
```
streamlit run launcher_streamlit.py apps/delphes/runtime/configuration_delphes.xlsx
```

You should see a message such as:
> You can now view your Streamlit app in your browser.
>  Local URL: http://localhost:8501

Click the link to launch the app in your default browser.

**Warning** If you need to run the Streamlit test client (or any other http client) on another port than 8501, update cell `common > client_url` in the configuration xlsxx file. 


