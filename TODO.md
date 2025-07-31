*********
* TODO.md
*********

# ONGOING
- in Streamlit client, look for default value in list AFTER filtering
- Move logic to set allowed_values outside Application & make indep from Excel
- remove idlabconfig
- improve Error evaluating {departeme2nt} == 78
- More elegant way to replace placeholders
- 
- Rename notes alerts
- String for date format
- liste dynamique
- solve issue with FastAPI
- test with Calc
- Remove update_case_field_str
- FastAPI call

- intention => intent

# Priority 1
## Framework
- Dynamic list of values, for instance arrondissements
- Improve
  - Complete exception handling on send email, call decision service, call OpenAI
  - use constants instead of string everywhere
  - Do not return fields associated with intent
- hallucinations on intentions - https://chatgpt.com/share/68874b59-2764-800d-a763-7fb2cc053af1
- Remove callbacks on all fields in Streamlit client
- response.raise_for_status()              # raise an error on 4xx/5xx
- In the prompt show in the task list only relevant attributes (see)
- in system promp list only fragments that are asked (use highlight_fragments)

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
- Take default value of case fields of type Literal into account in Streamlit client
- Move app_name to frontend configuration