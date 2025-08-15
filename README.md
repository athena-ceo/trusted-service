# Trusted Services README

If needed, please refer to more specific README files:

- [ODM README.md](src/backend/decision/decision_odm/README.md)
- [Delphes README.md](apps/delphes/README.md)

## Table of Contents

- [Quickstart](#quickstart)
- [What is Trusted Services?](#what-is-trusted-services)
- [Git Repository Contents](#git-repository-contents)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run](#run)
- [Common tasks](#common-tasks)  
  1. [Defining a Trusted Services app through Excel configuration](#defining-a-trusted-services-app-through-excel-configuration)
  2. [Adding support for a new language in the Trusted Services framework](#adding-support-for-a-new-language-in-the-trusted-services-framework)
  3. [Localizing an existing application](#localizing-an-existing-application)
- [Troubleshooting](#troubleshooting)

## Quickstart
Launch the intagrated demo (test/demo client + colocated Trusted Services server)

```streamlit run launcher_testclient_direct.py runtime/config_server.yaml apps/delphes/design_time/appdef_delphes_ff.xlsx apps/conneXion/design_time/appdef_conneXion_ff.xlsx```  

Launch the Trusted Services API  

```python launcher_api.py runtime/config_connection.yaml apps/delphes/design_time/appdef_delphes_ff.xlsx apps/conneXion/design_time/appdef_conneXion_ff.xlsx```  

Launch the Trusted Services test client  

```streamlit run launcher_testclient_rest.py runtime/config_connection.yaml```

## What is Trusted Services?

Trusted Services is an application server and a LOW CODE development framework that streamline the build of localizable,
accountable, self-service applications.

Trusted Services app follow a well defined flow:

- The requester is filling-in basic information in a flow
- The requester is describing his situation and need in natural language
- A **LLM-based text analyzer** is determining the intent among a list of predefined ones, and is extracting structured
  information from the natural language message
- Ths user is confirming the intent and extracted data
- A **rule-based decision engine** is determining the case priority and where to route the case
- A **distribution component** (e-mail, ticketing, case management) is posting the case along with insight to help the
  agent process the case

Defining a new application requires defining the application model and the decision rules:

1. The application model defines the predefined intents and the fields (such as "name", "date of application") that
   structure a case. It can be defined through an API or by configuring an Excel document. This README.md focuses on
   Excel-based approach.
2. The rules implement the following decisions:

- The (localized) messages to showw to the requester
- The priority attached to a new case
- The basket where to route it
- The alerts that must be brpought to the agent attention
- A recommended response that the agent can amend

------
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
------
More details can be found in the pptx in subdirectory `docs` of the current git repository. Also, to understand the
architecture and design of the Trusted Services framework, you should check the UML diagram in
`docs/trusted_services_uml.drawio`

## Git Repository Contents

This git repository comes with:

- The source code of the Trusted Services server
- A generic Streamlit test client
- Two application definition Excel files: One for the Delphes app, and one for a self-service app for a fictitious telco
  operator.

## Installation

### Get the Trusted Service and the sample applications

Type

```
git clone https://github.com/athena-ceo/trusted-service.git
pip install -r requirements.txt
```

### Download and install Docker Desktop and the Official IBM Operational Decision Manager for Developers image if you need to use the ODM Decision Engine

Please follow the instructions in https://hub.docker.com/r/ibmcom/odm

### Specifically for the Delphes application, download and install Thunderbird

Visit https://www.thunderbird.net/en-US/download/

## Configuration

Trusted Services apps are configured in an Excel file. For Delphes check `apps\delphes\runtime\spec_delphes_ff.xlsx`
where fields are either self-explanatory or explained in a comment cell.

### Configure how the test client accesses the API

- The Streamlist test client can either connect to the API through function calls or through REST calls
- To configure how the test client accesses the API, switch the Excel file to tab `frontend`. Field `connection_to_api`
  has two possible values
    - `direct`: Direct access through Python function
    - `rest`: REST calls to the Uvicorn server. In that case, you will need to launch the uvicorn server (see below) and
      to configure `rest_api_host` and `rest_api_port`

### Configure what Decision Engine the API connects to

- The API either connects to ODM, Drools or a hardcoded engine (in the case of Delphes:
  `apps.delphes.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`)
- To configure hwhat Decision Engine the API connects to, switch the Excel file to tab `backend`. Field
  `decision_engine` has three possible values
    - `odm`: Connect to an ODM Decision Service. In that case, you will need to launch the ODM Docker image (see below)
      and to configure the `odm` tab
    - `drools`: Connect to a Drools Decision Service
    - `apps.delphes.design_time.src.app_delphes.CaseHandlingDecisionEngineDelphesPython`: Connect to a hardcoded
      Decision Service

## Run

Proceed in the following order:

### If you configured the Decision Engine to be ODM, launch the ODM Docker image

**Important notes**:
> **1. ODM Decision Center database persistence locale**
>
> A given instance of the ODM Decision Center database has a native locale and cannot host rules with a different
> persitence locale.
>
> To set the locale (en_US by default):
>> - launch the ODM Docker image
>> - remove all rules
>> - run `odm_dc_localization.py` in `src/backend/decision/decision_odm/admin`
>
> 3. ODM Version
     > The `-v` option in the docker command ensure the Decision Center and RES databases are backed by a file.
     > Nothing will ensure that the format of the files doesn't change. Therefore it is advised to have a directory per
     ODM version.

This leads to the following command for Delphes!

```
cd apps/delphes/runtime/odm_databases/9.0
docker run -e LICENSE=accept -m 2048M --memory-reservation 2048M -p 9060:9060 -p 9443:9443 -v .:/config/dbdata/ -e SAMPLE=false icr.io/cpopen/odm-k8s/odm:9.0
```

### Unless you only want to launch the test client, and you configured that client to access the API directly, launch the uvicorn server

In the `trusted-service` top directory, type:

```
python launcher_uvicorn.py ./apps/delphes/runtime/spec_delphes_ff.xlsx
```

### Launch the test client

In the `trusted-service` top directory, type:

```
streamlit run launcher_streamlit_direct.py apps/delphes/design_time/appdef_delphes_ff.xlsx apps/conneXion/design_time/appdef_conneXion_ff.xlsx

```

You should see a message such as:
> You can now view your Streamlit app in your browser.
> Local URL: http://localhost:8501

Click the link to launch the app in your default browser.

**Warning** If you need to run the Streamlit test client (or any other http client) on another port than 8501, update
cell `common > client_url` in the configuration xlsxx file.

## Common tasks

### Defining a Trusted Services app through Excel configuration

### Adding support for a new language in the Trusted Services framework

Each language supported is identified by a string, such as "fr_FR" (French of France) or "fr" (General French, in
practice identical to fr_FR). As of today, the supported languages are: `fr` and `en`.
If you need to add support for a new language, for instance `fi` (Finnish):

- Add `fi` to the list above
- Update the Trusted Services framework Python code. To do so, look for the following comment:
    ```
    # IF YOU CHANGE THE FOLLOWING COMMENT, UPDATE README.md ACCORDINGLY
    # Add here support for new languages
    ```
  in the following files:
    - `trusted-service/src/common/configuration.py` (definition of `SupportedLocale`)
    - `trusted-service/src/backend/text_analysis/text_analysis_localization.py`
    - `trusted-service/src/sample_frontend/frontend_localization.py`
    - `trusted-service/src/sample_frontend/streamlit_main.py`

### Localizing an existing application

- First, make sure there exists support for the language in the Trusted Services framework
- Second, follow the steps below, shown on what it took to localize the Delphes app to `en`, initially supporting `fr`
  only
  This is an illustration on Delphes, which was supporting `fr` initially. Below are the steps followed to support `en`
  too
- In `./apps/delphes/runtime/spec_delphes_ff.xlsx` duplicate all rows and columns labeled `<property>_fr` and label the
  duplicate row or column `<property>_en`
- Best practices:
    - Translate the content with a LLM and give a bit of context in the prompt
    - Do not translate official names such as "AES: admission exceptionnelle au séjour", but provide extra explanation
      in English

### Best practices for localizing an existing application

- Copy-paste the configuation from a language your application already support
- Use a LLM
- No _ in locale

## Troubleshooting

- If you are not receiving the emails as you would expect, check `send_email` in tab `email_configuration` of the Excel
  Configuration File

