*********
* TODO.md
*********

# Priority 1
## Framework
- Solve issue with value returned by process_request in http mode
- Test with read_from_cache=False
- Polish
  - Complete exception handling on send email, call decision service, call OpenAI
  - Complete comments
  - Complete README.md
  - Complete parameterization, Manage port numbers for all the demos - including cors
  - Complete localization
  - use constants instead of string everywhere
- hallucinations on intentions
## Delphes
- Fix hardcoded decision service

# Priority 2
## Framework
- review logic of text_area: if changed manually and click send, will be overriden - Also issue with mode detailed

# Priority 3
## Framework
- pick scenarios in list
- Analyze several texts at once
- integer and float fields
- mandatory fields
- Show prompt