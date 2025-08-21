*********
* TODO.md
*********


#  Now
1) test avec et sans read
- test save
- les deux rubriques précédentes en mode REST
3) cursor
4) video vj + harley
5) Improve Assistant by providing a template xlsx
6) git

# Done
2) Update README

# Bugs
- localized_apps are nor reused => correct and check that text_analyzers are reused
- key of text_analyzer should be combination of text_config and llm_config
- click très rapides => validation error
- Mettre le prompt et le texte initial dans text analysis

# Improvement
- Error messages
- Save dans fichier hashé et msg d'erreur si fichier n'existe pas ou pas bon numéro de version
- add method to determine appdef from runtime directory
- Pas de référence de LocalizedApp dans TextAnalyzer, etc...
- Numéro de version dans les fichiers
- time processing

# Renaming
- Documenter APIs REST

# Avec Joël
- Test deux autres LLM
- Scaleway
- Test Préfecture

===
Détails
- intention => intent
- chercher tous les todo et tous les warnings et cas d'erreur
- cas d'erreur (app inconnue, locale non supportée)
- improve Error evaluating {departeme2nt} == 78
- Better manage the case where the cache file does not exist
- Manage Python code evaluation error in app-specific lists
- Manage gently config file absent or incorrect
- Erreur de connexion
- details => traces
- in Streamlit client, look for default value in list AFTER filtering
- Rename notes alerts
- String for date format should be localized
- test with Libre Office Calc
- Remove update_case_field_str

# Priority 1
## Framework
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