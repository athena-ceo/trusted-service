# Trusted Services Applications Catalog

This document describes all applications built on the Trusted Services framework, providing details for developers and users.

## 🌟 Overview

The Trusted Services framework is designed to support multiple independent applications. Each application:
- Has its own configuration in `runtime/apps/{app_name}/`
- Can use the generic test client or build a custom frontend
- Shares the same backend infrastructure
- Is independently deployable

---

## 🇫🇷 Delphes - French Prefecture System

### Description
**Delphes** modernizes the reception of foreign nationals at French prefectures, specifically piloted at the Yvelines prefecture.

### Status
✅ **Production** - Actively deployed and maintained

### Key Features
- AI-powered intent detection for residence permit requests
- Automatic case routing based on user situation
- Multilingual support (French, English)
- DSFR (French Government Design System) compliance
- RGAA accessibility standards
- Email distribution of responses

### Technical Stack
- **Backend**: Trusted Services framework (FastAPI + Python)
- **Frontend**: Custom Next.js 15 with React 19
- **Design**: DSFR 1.14.2
- **Decision Engine**: Python-based business rules
- **LLM**: Configurable (Ollama, OpenAI, Scaleway)

### Configuration Location
```
runtime/apps/delphes/
├── delphes.xlsx           # Intent definitions and field mappings
├── decision_engine.py     # Business rules for case handling
└── delphes-no-mail.xlsx   # Version without email distribution

apps/delphes/
├── frontend/              # Custom Next.js frontend
├── docker-compose.dev.yml # Development stack
└── docker-compose.prod.yml # Production stack
```

### Running Delphes
```bash
# Full stack (backend + frontend)
./docker-manage.sh start delphes

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8002
```

### Documentation
See [apps/delphes/README.md](apps/delphes/README.md) for detailed Delphes documentation including:
- User interface guide
- Configuration details
- Deployment instructions
- Customization guide

---

## 🇫🇮 AISA - Helsinki City Services

### Description
**AISA** (currently in development) provides intelligent assistance for Helsinki city government services. It helps citizens navigate city services and processes requests efficiently.

### Status
🚧 **In Development** - Configuration and testing phase

### Key Features
- Multi-language support (Finnish, English)
- Intent detection for various city services
- Automated case handling and routing
- Integration with Helsinki city systems (planned)

### Technical Stack
- **Backend**: Trusted Services framework
- **Frontend**: Generic Streamlit test client (custom frontend planned)
- **Decision Engine**: Python-based rules
- **Languages**: Finnish (fi), English (en)

### Configuration Location
```
runtime/apps/AISA/
├── AISA.xlsx              # Intent definitions (Finnish/English)
└── decision_engine.py     # Business logic for Helsinki services
```

### Running AISA
```bash
# Using generic test client
./docker-manage.sh start aisa

# Access:
# - Test Client: http://localhost:8501
# - Backend API: http://localhost:8002
```

### Current Limitations
- Uses generic test client (custom UI in planning)
- Still in configuration phase
- Limited integration with Helsinki backend systems

### Roadmap
- [ ] Complete intent and field configuration
- [ ] Develop custom React frontend
- [ ] Integrate with Helsinki city backend APIs
- [ ] Deploy pilot for specific city services

---

## 🧪 conneXion - Telecom Test Application

### Description
**conneXion** is a test application simulating a telecom operator's customer service system. It's used to validate framework capabilities and serve as a reference implementation.

### Status
🧪 **Test/Demo** - Used for framework validation

### Key Features
- Fictional telecom customer service scenarios
- Intent detection for common telecom requests (billing, technical support, etc.)
- Demonstrates framework flexibility
- Useful for testing and demonstrations

### Technical Stack
- **Backend**: Trusted Services framework
- **Frontend**: Generic Streamlit test client
- **Decision Engine**: Python rules
- **Purpose**: Testing and validation

### Configuration Location
```
runtime/apps/conneXion/
├── conneXion.xlsx         # Intent definitions for telecom scenarios
└── decision_engine.py     # Sample business rules
```

### Running conneXion
```bash
# Using generic test client
./docker-manage.sh start connexion

# Access:
# - Test Client: http://localhost:8501
# - Backend API: http://localhost:8002
```

### Use Cases
- Framework capability demonstrations
- New developer onboarding
- Testing new features before deploying to production apps
- Reference implementation for new applications

---

## 🆕 Building Your Own Application

### Prerequisites
- Understanding of the Trusted Services architecture
- Python 3.11+ for backend configuration
- Excel or JSON for intent/field definitions
- Optional: React/Next.js for custom frontend

### Step-by-Step Guide

#### 1. Create Application Configuration

Create your application directory:
```bash
mkdir -p runtime/apps/your_app_name
```

#### 2. Define Intents and Fields

Create `your_app_name.xlsx` with sheets:
- **intentions**: Define user intents your app should recognize
- **intentions_examples**: Provide training examples for each intent
- **champs** (fields): Define data fields to extract from user requests
- **definitions**: Term definitions for LLM context

Example intent structure:
| intention_id | intention_label | intention_scoring |
|--------------|-----------------|-------------------|
| request_info | Information Request | 0 |
| submit_claim | Submit Claim | 0 |

#### 3. Implement Business Rules

Create `decision_engine.py`:
```python
from backend.decision.decision import Decision

class YourAppDecision(Decision):
    """Business rules for your application"""
    
    def __init__(self, app_id: str, locale: str):
        super().__init__(app_id, locale)
    
    def execute_decision(self, case_request: dict) -> dict:
        """Process the case and return decision"""
        intention_id = case_request.get('intention_id')
        field_values = case_request.get('field_values', {})
        
        # Your business logic here
        if intention_id == 'request_info':
            return {
                'decision': 'provide_information',
                'message': 'Here is the information you requested...'
            }
        
        return {'decision': 'unknown', 'message': 'Unable to process'}
```

#### 4. Test with Generic Client

```bash
# Start framework with your app
./docker-manage.sh start framework

# Access test client
# Navigate to http://localhost:8501
# Select your app from dropdown
```

#### 5. (Optional) Build Custom Frontend

If you need a custom UI:
```bash
mkdir -p apps/your_app_name/frontend
cd apps/your_app_name/frontend

# Create Next.js app or React app
npx create-next-app@latest .
```

See Delphes frontend as reference: `apps/delphes/frontend/`

#### 6. Configure Docker Compose

Create `apps/your_app_name/docker-compose.dev.yml`:
```yaml
services:
  backend:
    extends:
      file: ../../docker-compose.yml
      service: backend
    container_name: your-app-backend-dev

  your-app-frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8002
    depends_on:
      backend:
        condition: service_healthy
```

#### 7. Update docker-manage.sh

Add your application to the script's application list.

#### 8. Test End-to-End

```bash
./docker-manage.sh start your_app_name
```

---

## 📊 Application Comparison

| Feature | Delphes | AISA | conneXion |
|---------|---------|------|-----------|
| **Status** | Production | In Dev | Test/Demo |
| **Frontend** | Custom Next.js | Generic (custom planned) | Generic |
| **Languages** | FR, EN | FI, EN | EN |
| **Decision Engine** | Python | Python | Python |
| **LLM Provider** | Configurable | Configurable | Configurable |
| **Custom Deployment** | Yes | Planned | No |
| **Email Distribution** | Yes | Planned | No |
| **Design System** | DSFR (French gov) | TBD | Generic |

---

## 🔌 Integration Patterns

### REST API Integration

All applications expose the same REST API endpoints:

```http
GET /trusted_services/v2/app_ids
# Returns: ["delphes", "AISA", "conneXion", ...]

GET /trusted_services/v2/apps/{app_id}/locales
# Returns: ["fr", "en"] or ["fi", "en"]

POST /trusted_services/v2/apps/{app_id}/{locale}/analyze
# Analyze user request and detect intent

POST /trusted_services/v2/apps/{app_id}/{locale}/handle_case
# Process case and return decision
```

### Custom Frontend Integration

Your custom frontend should:
1. Call `/analyze` with user's request text and field values
2. Present detected intents to user (or auto-select)
3. Collect additional required fields
4. Call `/handle_case` with complete case data
5. Display results to user

See `apps/delphes/frontend/` for complete React/Next.js example.

---

## 🚀 Deployment Patterns

### Pattern 1: Framework with Generic Client
**Use case**: Development, testing, simple applications
```bash
./docker-manage.sh start framework prod
```

### Pattern 2: Application with Custom Frontend
**Use case**: Production applications (like Delphes)
```bash
./docker-manage.sh start delphes prod
```

### Pattern 3: Shared Backend, Multiple Frontends
**Use case**: Multiple applications sharing backend
```bash
# Backend runs once, serves multiple apps
./docker-manage.sh start framework prod

# Multiple custom frontends connect to same backend
# Each frontend configured with NEXT_PUBLIC_API_URL
```

### Pattern 4: Fully Separated
**Use case**: Future - each app in its own repository
```bash
# Backend as library/service
# Each app deployed independently
# (Planned for future refactoring)
```

---

## 📝 Configuration Reference

### Intent Definition (Excel)

**Sheet: intentions**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| intention_id | string | Yes | Unique identifier |
| intention_label | string | Yes | Human-readable name |
| intention_scoring | number | No | Default score (usually 0) |

**Sheet: intentions_examples**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| intention_id | string | Yes | Links to intentions sheet |
| example_text | string | Yes | Example user input |

**Sheet: champs (fields)**
| Column | Type | Required | Description |
|--------|------|----------|-------------|
| field_id | string | Yes | Field identifier |
| field_label | string | Yes | Display label |
| field_type | string | Yes | text, date, boolean, etc. |
| required | boolean | No | Is field required? |
| intentions | string | No | Comma-separated list of applicable intents |

---

## 🤝 Contributing

### Adding a New Application
1. Create configuration in `runtime/apps/{app_name}/`
2. Test with generic client
3. (Optional) Build custom frontend
4. Update `docker-manage.sh` to include your app
5. Document in this file
6. Submit PR

### Improving Existing Applications
- See application-specific README files
- Test changes with generic client first
- Ensure backward compatibility
- Update documentation

---

## 📚 Additional Resources

- [Framework Architecture](README.md#-architecture)
- [API Documentation](http://localhost:8002/docs) (when backend running)
- [Delphes Documentation](apps/delphes/README.md)
- [Testing Guide](TESTING.md)
- [Deployment Guide](README.md#-deployment)

---

## 🔮 Future Roadmap

See [TODO.md](TODO.md) for complete roadmap including:
- React-based generic test client (replacing Streamlit)
- JSON-based configuration (replacing Excel)
- Application repository separation
- AISA custom frontend development
- Additional public service applications

