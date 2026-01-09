# Trusted Services - TODO and Roadmap

## 📋 Current Tasks

### Docker & Architecture Restructuring (COMPLETED ✅)

- [X] Phase 1: Framework Docker Infrastructure
  - [X] Create deploy/compose/docker-compose.trusted-services-backend.yml (framework backend only)
  - [X] Create Dockerfile.streamlit (generic test client)
  - [X] Update deploy/compose/docker-compose.trusted-services-dev.yml (framework + test client)
  - [X] Update deploy/compose/docker-compose.trusted-services-backend.yml (framework production)
  - [X] Create deploy/compose/docker-compose.delphes-integration.yml
  - [X] Create deploy/compose/docker-compose.delphes-frontend-prod.yml
- [X] Phase 2: Update docker-manage.sh
  - [X] Support multiple targets (framework, delphes, aisa, connexion)
  - [X] Support dev/prod environments
  - [X] Add list-apps command
  - [X] Update help documentation
- [X] Phase 3: Documentation Restructuring
  - [X] Update README.md (framework vs applications, new Quick Start)
  - [X] Create APPLICATIONS.md (complete application catalog + dev guide)
  - [X] Create apps/delphes/README.md (Delphes-specific documentation)
  - [X] Update TESTING.md (application-specific testing sections)
- [X] Phase 4: CI/CD Updates
  - [X] Update integration-tests.yml (clarify framework testing)
  - [X] Update deploy.yml (clarify deployment targets)
  - [X] Update backend-ci.yml (add scope comments)
  - [X] Update frontend-ci.yml (clarify Delphes-specific)
- [X] Phase 5: Future Planning Documentation
  - [X] Create FUTURE_REFACTORING.md (comprehensive roadmap)

---

## 🏗️ Framework vs Applications Architecture

### Current State (After Phase 1-2)

```
Trusted Services Framework (Generic)
├── Backend (FastAPI) - Serves ALL applications
├── Test Client (Streamlit) - Generic testing interface
└── Applications:
    ├── Delphes (French Prefecture System)
    │   ├── Config: runtime/apps/delphes/
    │   ├── Frontend: apps/delphes/frontend/ (Next.js)
    │   └── Compose: deploy/compose/docker-compose.delphes-*.yml
    ├── AISA (Helsinki City Services)
    │   ├── Config: runtime/apps/AISA/
    │   ├── Frontend: Generic test client (for now)
    │   └── Compose: Uses framework compose files
    └── conneXion (Telecom Test App)
        ├── Config: runtime/apps/conneXion/
        ├── Frontend: Generic test client
        └── Compose: Uses framework compose files
```

### Running Different Configurations

```bash
# Framework with test client
./deploy/compose/docker-manage.sh start framework

# Delphes full stack
./deploy/compose/docker-manage.sh start delphes

# AISA (uses test client)
./deploy/compose/docker-manage.sh start aisa

# List all applications
./deploy/compose/docker-manage.sh list-apps
```

---

## 🚀 Future Refactoring Roadmap

### Phase A: React Generic Test Client (PRIORITY: HIGH)

**Goal**: Replace Streamlit with modern React test client**Timeline**: Next phase after current Docker restructuring

- [ ] Design React test client UI/UX
- [ ] Implement test client features:
  - [ ] Application selection (delphes, AISA, conneXion)
  - [ ] Text analysis interface
  - [ ] Case handling interface
  - [ ] Configuration viewer
  - [ ] LLM config selection
  - [ ] Cache management
- [ ] Create Dockerfile.test-client (React)
- [ ] Update docker-compose files to use React client
- [ ] Remove launcher_testclient.py and Dockerfile.streamlit
- [ ] Update documentation

### Phase B: Excel → JSON Configuration Migration (PRIORITY: HIGH)

**Goal**: Replace Excel-based configs with JSON + config management UI
**Timeline**: After React test client

Current: Each application has .xlsx file with:

- Intentions
- Features
- Field definitions
- Decision engine configs
- etc.

Future: JSON-based configuration with management frontend

- [ ] Define JSON schema for application configuration
- [ ] Create JSON→Excel migration tool (backward compatibility)
- [ ] Implement configuration management UI (part of test client)
  - [ ] Visual intention editor
  - [ ] Feature definition manager
  - [ ] Field schema editor
  - [ ] Decision engine config
  - [ ] Export/import configurations
- [ ] Update framework to support JSON configs
- [ ] Maintain Excel support for transition period
- [ ] Migrate existing applications to JSON
- [ ] Document configuration format and migration

**Benefits**:

- Version control friendly (text-based)
- No Excel dependency
- Better validation
- Integrated development workflow
- Easier programmatic manipulation

### Phase C: AISA Custom Frontend (PRIORITY: MEDIUM)

**Goal**: Create AISA-specific frontend similar to Delphes**Timeline**: After config migration

- [ ] Design AISA frontend requirements
- [ ] Create apps/AISA/frontend/ (React/Next.js)
- [ ] Implement AISA-specific UI in Finnish/English
- [ ] Create apps/AISA/docker-compose.*.yml
- [ ] Create apps/AISA/README.md
- [ ] Update docker-manage.sh for AISA target
- [ ] Deploy AISA production

### Phase D: Application Repository Separation (PRIORITY: MEDIUM)

**Goal**: Extract applications into independent repositories
**Timeline**: After AISA frontend complete

Current Structure:

```
trusted-service/
├── src/                    # Framework
├── apps/                   # Applications
└── runtime/apps/           # App configs
```

Target Structure:

```
trusted-services/           # Framework repository
├── src/                    # Framework code
├── Published as:
│   ├── PyPI package
│   ├── Docker image
│   └── npm package (test client)

delphes/                    # Delphes repository
├── frontend/
├── config/
└── docker-compose.yml

aisa/                       # AISA repository
├── frontend/
├── config/
└── docker-compose.yml
```

**Steps**:

- [ ] Define framework API contract
- [ ] Create framework PyPI package
- [ ] Publish framework Docker image
- [ ] Create application repository template
- [ ] Extract Delphes to separate repo
- [ ] Extract AISA to separate repo
- [ ] Update CI/CD for multi-repo workflow
- [ ] Document application development guide

---

## 📝 Completed Tasks (Archive)

### September 2024 - Munich and Paris Events

- [X] PPTX Presentation 1
- [X] Deployment on Scaleway: Trusted Services
- [X] Deployment on Scaleway: Trusted Services generic client 1

### October-November 2024 - CI/CD and Testing

- [X] CI/CD Setup (GitHub Actions)
- [X] Backend smoke tests
- [X] Frontend smoke tests
- [X] Integration tests
- [X] Docker ARM64 support (Apple Silicon)
- [X] Unified docker-manage.sh script
- [X] Documentation simplification

### November 2024 - Code Quality

- [X] Translate framework code comments to English
- [X] SSH authentication setup
- [X] Pydantic version consistency

---

## 🔧 Technical Debt & Improvements

### Code Quality

- [ ] Gestion clean de toutes les erreurs: consistency xlsx
- [ ] Logs techniques structured logging
- [ ] Feedback log system
- [ ] In app_def, put locale as a column everywhere + default locale

### Infrastructure

- [ ] Deployment flow optimization
- [ ] Reorganization of runtime directory structure
- [ ] Architecture diagram (update with new structure)
- [ ] Script de déploiement d'une application

### Documentation

- [X] README restructuring (in progress - Phase 3)
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Developer guide
- [ ] Deployment guide for each application

---

## 🤔 To Be Decided

### API Evolution

- [X] Passer à l'API V2 uniformément
  - Currently mixing v1 and v2 endpoints
  - Create consistent API facade
  - Deprecate old endpoints gracefully

### Configuration

- [ ] Define configuration versioning strategy
- [ ] Backward compatibility policy for configs
- [ ] Configuration validation framework

### Multi-tenancy

- [X] Support multiple apps in single deployment
- [ ] Application isolation strategy
- [ ] Resource allocation per application

---

## 📞 Questions for Review

1. **React Test Client Scope**: Should it include configuration management UI or separate tool?
2. **JSON Schema**: Should we use JSON Schema standard or custom validation?
3. **Application Template**: What should be included in application template repo?
4. **Framework Versioning**: Semantic versioning strategy for framework?
5. **Deployment Strategy**: Continue with Docker or add Kubernetes support?

---

## 📚 Related Documentation

- `README.md` - Main project documentation (framework-first structure) ✅
- `APPLICATIONS.md` - Application catalog and development guide ✅
- `TESTING.md` - Testing guide with application-specific sections ✅
- `INTEGRATION_TESTS.md` - Integration testing guide ✅
- `FUTURE_REFACTORING.md` - Comprehensive refactoring roadmap ✅
- `apps/delphes/README.md` - Delphes-specific documentation ✅

---

**Last Updated**: November 2024
**Current Phase**: Docker & Architecture Restructuring (Phases 1-5 COMPLETE ✅)
**Next Phase**: Future Refactoring - Phase A (React Test Client)
