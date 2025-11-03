# Future Refactoring Roadmap

This document outlines planned future refactorings for the Trusted Services framework to improve maintainability, developer experience, and application independence.

## 🎯 Strategic Vision

**Goal**: Enable complete separation of applications from the framework while maintaining the current easy development experience.

**Timeline**: These are planned enhancements, not current requirements. They will be implemented as the framework matures and application needs grow.

---

## 📋 Planned Refactorings

### Phase A: React Generic Test Client

**Current State**: Generic test client uses Streamlit (`launcher_testclient.py`)

**Future State**: Replace with React-based generic test client

#### Motivation
- Modern web tech stack (React + TypeScript)
- Better UI/UX capabilities
- Easier for frontend developers to understand
- Consistent with application frontends (Delphes uses React)
- Better integration testing capabilities

#### Implementation Plan

1. **Create React Test Client**
   ```
   apps/test-client/
   ├── src/
   │   ├── components/
   │   │   ├── AppSelector.tsx       # Select application
   │   │   ├── LocaleSelector.tsx    # Select language
   │   │   ├── AnalyzeForm.tsx      # Test analyze endpoint
   │   │   ├── CaseHandlerForm.tsx  # Test case handling
   │   │   └── ResponseViewer.tsx   # Display results
   │   ├── App.tsx
   │   └── index.tsx
   ├── Dockerfile
   └── package.json
   ```

2. **Features**
   - Dropdown to select application (delphes, AISA, conneXion)
   - Dropdown to select locale (based on app)
   - Form to test `analyze` endpoint
   - Form to test `handle_case` endpoint
   - JSON response viewer
   - Request/response history
   - Dark mode support

3. **Docker Integration**
   ```yaml
   # docker-compose.dev.yml (framework)
   services:
     react-test-client:
       build: ./apps/test-client
       ports:
         - "3001:3000"
       environment:
         - REACT_APP_API_URL=http://backend:8002
   ```

4. **Migration Path**
   - Keep Streamlit client available during transition
   - Run both in parallel for compatibility
   - Update documentation gradually
   - Deprecate Streamlit once React client is stable

#### Benefits
- ✅ Modern, responsive UI
- ✅ Better developer experience
- ✅ TypeScript type safety
- ✅ Easier to extend with new features
- ✅ Consistent technology across project

#### Estimated Effort
2-3 weeks for initial implementation + 1 week testing

---

### Phase B: JSON-Based Configuration Management

**Current State**: Applications use Excel files (`.xlsx`) for configuration

**Future State**: JSON-based configuration with web UI for editing

#### Motivation
- Version control friendly (clear diffs)
- Easier programmatic manipulation
- No Excel dependency
- Better CI/CD integration
- Enable configuration validation/linting

#### Implementation Plan

1. **Define JSON Schema**
   ```json
   {
     "app_id": "delphes",
     "locales": ["fr", "en"],
     "intents": [
       {
         "id": "renouvellement_titre_sejour",
         "label": "Residence Permit Renewal",
         "examples": [
           "Je veux renouveler mon titre de séjour",
           "Mon titre expire bientôt"
         ],
         "fields": ["nom", "prenom", "date_naissance", "numero_AGDREF"]
       }
     ],
     "fields": [
       {
         "id": "nom",
         "type": "text",
         "label": "Nom de famille",
         "required": true,
         "validation": "^[A-Za-zÀ-ÿ\\s-]+$"
       }
     ],
     "definitions": [
       {
         "term": "titre de séjour",
         "definition": "Document permettant de résider en France"
       }
     ]
   }
   ```

2. **Configuration Loader Refactoring**
   ```python
   # src/backend/backend/config_loader.py
   class ConfigLoader:
       def load_config(self, app_id: str) -> AppConfig:
           """Load config from JSON or Excel (backward compat)"""
           json_path = f"runtime/apps/{app_id}/config.json"
           excel_path = f"runtime/apps/{app_id}/{app_id}.xlsx"
           
           if os.path.exists(json_path):
               return self._load_json(json_path)
           elif os.path.exists(excel_path):
               return self._load_excel(excel_path)
           else:
               raise ConfigNotFoundError(app_id)
   ```

3. **Configuration Web UI**
   ```
   apps/config-editor/
   ├── src/
   │   ├── pages/
   │   │   ├── AppList.tsx          # List applications
   │   │   ├── IntentEditor.tsx     # Edit intents
   │   │   ├── FieldEditor.tsx      # Edit fields
   │   │   ├── ExamplesEditor.tsx   # Edit training examples
   │   │   └── Preview.tsx          # Preview changes
   │   └── components/
   │       ├── JsonViewer.tsx
   │       ├── ValidationErrors.tsx
   │       └── ImportExport.tsx
   ```

4. **Features**
   - Visual editor for intents and fields
   - Import from Excel (one-time migration)
   - Export to Excel (compatibility)
   - Real-time validation
   - Git-friendly JSON format
   - Preview before save

5. **Migration Strategy**
   - Support both formats during transition
   - Provide Excel → JSON converter tool
   - Update one application at a time
   - Keep Excel support for backward compatibility
   - Eventually deprecate Excel (years, not months)

#### Benefits
- ✅ Better version control
- ✅ Easier collaboration
- ✅ No Excel dependency
- ✅ Configuration validation
- ✅ Programmatic config generation

#### Estimated Effort
4-6 weeks (schema + loader + web UI + migration)

---

### Phase C: AISA Custom Frontend

**Current State**: AISA uses generic test client

**Future State**: Custom React frontend for AISA application

#### Motivation
- Production-ready UI for Helsinki deployment
- Finnish design system compliance
- AISA-specific workflows and features
- Better UX for end users

#### Implementation Plan

1. **Frontend Structure**
   ```
   apps/AISA/frontend/
   ├── src/
   │   ├── app/
   │   │   ├── fi/                # Finnish locale pages
   │   │   ├── en/                # English locale pages
   │   │   └── layout.tsx         # Root layout
   │   ├── components/
   │   │   ├── ServiceSelector.tsx
   │   │   ├── CitizenForm.tsx
   │   │   └── Helsinki/          # Helsinki-specific components
   │   └── styles/
   │       └── helsinki-theme.css # Helsinki design system
   ├── Dockerfile
   └── docker-compose.dev.yml
   ```

2. **Design System**
   - Comply with Helsinki city design guidelines
   - Accessibility (WCAG 2.1 AA)
   - Finnish and English translations
   - Mobile-first responsive design

3. **Integration**
   ```yaml
   # apps/AISA/docker-compose.dev.yml
   services:
     backend:
       extends:
         file: ../../docker-compose.yml
         service: backend
     
     aisa-frontend:
       build: ./frontend
       ports:
         - "3000:3000"
       environment:
         - NEXT_PUBLIC_API_URL=http://backend:8002
   ```

4. **Update docker-manage.sh**
   - Add AISA-specific commands
   - Support AISA development mode
   - Production deployment config

#### Benefits
- ✅ Production-ready AISA deployment
- ✅ Helsinki-specific UX
- ✅ Professional appearance
- ✅ Better end-user experience

#### Estimated Effort
6-8 weeks (design + implementation + testing)

---

### Phase D: Application Repository Separation

**Current State**: All applications in monorepo

**Future State**: Each application in its own repository

#### Motivation
- Clear ownership boundaries
- Independent versioning
- Easier external contributions
- Simpler deployment pipelines
- Reduced repository size

#### Target Structure

```
# Repository 1: Framework
github.com/trusted-services/framework
└── Trusted Services core backend + test client

# Repository 2: Delphes Application
github.com/prefecture-yvelines/delphes
└── Delphes config + custom frontend
└── Depends on: trusted-services/framework

# Repository 3: AISA Application
github.com/helsinki-city/aisa
└── AISA config + custom frontend
└── Depends on: trusted-services/framework

# Repository 4: conneXion (example)
github.com/trusted-services/connexion-example
└── Example test application
└── Depends on: trusted-services/framework
```

#### Implementation Plan

1. **Framework as Library/Service**
   ```python
   # Framework published as pip package
   pip install trusted-services-framework
   
   # Or as Docker image
   docker pull ghcr.io/trusted-services/backend:latest
   ```

2. **Application Structure**
   ```
   delphes/
   ├── config/
   │   ├── delphes.json          # App config
   │   └── decision_engine.py    # Business rules
   ├── frontend/                  # Custom frontend
   ├── docker-compose.yml         # Full stack
   ├── requirements.txt           # Dependencies
   └── README.md                  # Delphes docs
   ```

3. **Docker Compose Integration**
   ```yaml
   # apps/{app}/docker-compose.yml
   services:
     backend:
       image: ghcr.io/trusted-services/backend:latest
       volumes:
         - ./config:/app/runtime/apps/{app}
     
     frontend:
       build: ./frontend
       environment:
         - API_URL=http://backend:8002
   ```

4. **CI/CD per Application**
   - Each app has its own GitHub Actions
   - Independent deployment pipelines
   - Application-specific testing
   - Version tagging per app

5. **Migration Path**
   - Extract framework to separate repo first
   - Migrate Delphes as pilot
   - Migrate AISA after custom frontend ready
   - Keep conneXion as example in framework repo
   - Update all documentation and links

#### Challenges
- Coordinating framework version updates
- Maintaining backward compatibility
- Documentation synchronization
- Cross-repository testing

#### Benefits
- ✅ Clear separation of concerns
- ✅ Independent versioning
- ✅ Easier collaboration
- ✅ Smaller, focused repositories
- ✅ Better deployment isolation

#### Estimated Effort
8-12 weeks (careful planning + migration + CI/CD setup)

---

## 🗓️ Recommended Sequence

### Short Term (Next 3-6 months)
1. ✅ Phase 1-2: Docker restructuring (COMPLETED)
2. ✅ Phase 3: Documentation updates (COMPLETED)
3. **Phase A**: React Test Client (Start soon - improves dev experience)

### Medium Term (6-12 months)
4. **Phase B**: JSON Configuration (After React client stable)
5. **Phase C**: AISA Custom Frontend (Parallel with Phase B)

### Long Term (12-24 months)
6. **Phase D**: Repository Separation (After all other phases complete)

---

## 📝 Notes on Backward Compatibility

### Critical Principles
- **Never break existing applications mid-project**
- **Always support legacy formats during transition**
- **Provide clear migration guides and tools**
- **Give ample warning before deprecating features**

### Deprecation Process
1. Announce deprecation with timeline (6-12 months notice)
2. Provide migration tools and documentation
3. Support both old and new during overlap period
4. Mark as deprecated in code with warnings
5. Remove only after all applications migrated

---

## 🧪 Testing During Refactoring

### Before Each Refactoring
- [ ] All existing tests passing
- [ ] Full backup of configurations
- [ ] Migration scripts tested in isolation

### During Refactoring
- [ ] Maintain test coverage > 80%
- [ ] Run integration tests daily
- [ ] Test backward compatibility
- [ ] Verify each application still works

### After Each Refactoring
- [ ] Update all documentation
- [ ] Verify performance unchanged or improved
- [ ] Confirm all applications deployed successfully
- [ ] Gather feedback from users

---

## 🤝 Contribution Guidelines for Future Work

### For Framework Developers
- Maintain framework application-agnostic
- Keep APIs stable and well-documented
- Consider backward compatibility always
- Write comprehensive tests

### For Application Developers
- Follow framework conventions
- Don't modify framework core for app-specific needs
- Share reusable components back to framework
- Document app-specific requirements

---

## 📚 Related Documentation

- [TODO.md](TODO.md) - Current project tasks
- [README.md](README.md) - Framework overview
- [APPLICATIONS.md](APPLICATIONS.md) - Application catalog
- [TESTING.md](TESTING.md) - Testing guide

---

## ⚠️ Important Reminders

1. **These are PLANS, not commitments**: Priorities may change based on user needs
2. **Backward compatibility is sacred**: Never break existing applications
3. **Incremental changes are better**: Small, tested steps over big bang rewrites
4. **User feedback drives priorities**: Listen to framework and application users
5. **Document everything**: Future developers will thank you

---

*Last updated: November 2025*
*Review and update quarterly*

