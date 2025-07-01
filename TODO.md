*********
* TODO.md
*********

# ONGOING
- In case_field move options in attribute dedicated to options and put type=str
- Put label of options in model
- Define type and options as attribute
- Remove update_case_field_str

# Priority 1
## Framework
- Improve
  - Complete exception handling on send email, call decision service, call OpenAI
  - Complete comments
  - Complete parameterization, Manage port numbers for all the demos - including cors
  - Complete localization
  - use constants instead of string everywhere
- hallucinations on intentions
- Remove callbacks on all fields in Streamlit client
## Delphes

# Priority 2
## Framework
- review logic of text_area: if changed manually and click send, will be overriden - Also issue with mode detailed
- Hallucinations in fragment : case insensitive search, remove "." at the and, Levenshtein distance.

# Priority 3
## Framework
- pick scenarios in list
- Analyze several texts at once
- integer and float fields
- mandatory fields
- Show prompt
- Streamlit test client launcher
- Take default value of case fields of type Literal into account in Streamlit client