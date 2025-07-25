*********
* TODO.md
*********

# ONGOING
- Remove app_name from API and put in frontend
- Show narrative about prompt and rule engine

- Rename notes alerts
- Python version, ssems that `other` is not correctly handled 
- read example in xls
- test with Calc
- Remove update_case_field_str

- ODM verbalization in English
- intention => intent
- si date pas trouvée dans texte => tableau des fragments de couleur noire

# Priority 1
## Framework
- Support for Open Office Calc
- Improve
  - Complete exception handling on send email, call decision service, call OpenAI
  - Complete comments
  - Complete parameterization, Manage port numbers for all the demos - including cors
  - Complete localization
  - use constants instead of string everywhere
  - Do not return fields associated with intent
- hallucinations on intentions
- Remove callbacks on all fields in Streamlit client
- response.raise_for_status()              # raise an error on 4xx/5xx
- In the task list only relevant attributes
## Delphes

# Priority 2
## Framework
- review logic of text_area: if changed manually and click send, will be overriden - Also issue with mode detailed
- Hallucinations in fragment : case insensitive search, remove "." at the and, Levenshtein distance.
- Remove scoring["intention_label"] and scoring["intention_fields"], clean FastAPi signature
- Pickstyle: https://www.youtube.com/watch?v=qccakpz9yRs

# Priority 3
## Framework
- pick scenarios in list
- Analyze several texts at once
- integer and float fields
- Show prompt
- Streamlit test client launcher
- Take default value of case fields of type Literal into account in Streamlit client
- Move app_name to frontend configuration