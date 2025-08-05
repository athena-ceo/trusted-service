*********
* TODO.md
*********

# Ongoing
Server
- Create REST for all
- Test Préfecture
- git push
- Vidéos
- 
- Créer branche
- Faire le launcher client rest (config tech) et le launcher server rest (config tech et appdef files)
- 
- Corriger l'API REST
- Faire marcher avec portail Préfecture
- Décider quel modèle depuis le client
- Variables calculées
- 

CLEAN
- Les trois classes de la hierarchie doivent implémenter l'interface
- typage SupportedLocale
- Vérifier la logique des callbacks
- intention => intent
- simplifier le code de ces deux constructeurs
- chercher tous les todo et tous les warnings et cas d'erreur
- README
- Nom des classes postfix
- Rzevoier les __init__ des trois composants en cascade
- config => def
- loc => locale
- cas d'erreur (app inconnue, locale non supportée)
- improve Error evaluating {departeme2nt} == 78
- Better manage the case where the cache file does not exist
- True / False in display of booleans
- Manage Python code evaluation error in app-specific lists
- Manage gently config file absent or incorrect
- Erreur de connexion

---------------------------------------------------------------- 
- nom de fichier json de cachingcontient app et loc
- changer les api rest


# ONGOING
- in Streamlit client, look for default value in list AFTER filtering

- Rename notes alerts
- String for date format
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