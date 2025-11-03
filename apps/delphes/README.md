# Delphes - French Prefecture Reception System

[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-black)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.1.0-blue)](https://reactjs.org/)
[![DSFR](https://img.shields.io/badge/DSFR-1.14.2-blue)](https://www.systeme-de-design.gouv.fr/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://typescriptlang.org/)

> 🇫🇷 **AI-powered reception system for French prefecture services**

## 📋 Overview

**Delphes** is a production application built on the Trusted Services framework that modernizes the reception of foreign nationals at French prefectures. It was piloted at the Yvelines prefecture to streamline residence permit request processing.

### Key Features

- **🤖 AI-Powered Intent Detection**: Automatically understand user requests
- **📝 Intelligent Form**: Dynamic fields based on detected intent
- **🌍 Multilingual**: French and English support
- **♿ RGAA Accessible**: Meets French government accessibility standards
- **🎨 DSFR Compliant**: Uses French government design system
- **📧 Email Distribution**: Automatic response generation and delivery
- **⚡ High Performance**: Next.js 15 with React 19 and Turbopack

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# From repository root
./docker-manage.sh start delphes

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8002
```

### Manual Development Setup

```bash
# 1. Start backend (from repository root)
python -m venv tsvenv
source tsvenv/bin/activate
pip install -r requirements.txt
python launcher_api.py ./runtime

# 2. Start frontend (in another terminal)
cd apps/delphes/frontend
npm install
npm run dev

# Access frontend at: http://localhost:3000
```

---

## 🏗️ Architecture

### Application Stack

```
┌─────────────────────────────────────┐
│     Delphes Next.js Frontend        │
│  (Custom UI with DSFR components)   │
└──────────────┬──────────────────────┘
               │ HTTP
               ▼
┌─────────────────────────────────────┐
│   Trusted Services Backend (API)    │
│  - Intent detection                 │
│  - Case handling                    │
│  - Decision engine                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Delphes Configuration            │
│  - delphes.xlsx (intents/fields)    │
│  - decision_engine.py (rules)       │
└─────────────────────────────────────┘
```

### User Flow

1. **Contact Form** (`/accueil-etrangers`)
   - User enters basic information and request message
   - Form validates data

2. **Analysis** (`/analysis`)
   - AI analyzes request and detects intent
   - System extracts relevant information
   - Dynamic form displays based on detected intent
   - User completes required fields

3. **Case Handling** (`/handle-case`)
   - System processes complete case
   - Decision engine applies business rules
   - Watson Orchestrate integration (if configured)
   - Response generated

4. **Confirmation** (`/confirmation`)
   - User receives confirmation
   - Email sent with detailed response
   - Case reference provided

---

## 📁 Project Structure

```
apps/delphes/
├── frontend/                       # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Home (redirects)
│   │   │   ├── accueil-etrangers/ # Contact form
│   │   │   │   └── page.tsx
│   │   │   ├── analysis/          # AI analysis + dynamic form
│   │   │   │   └── page.tsx
│   │   │   ├── handle-case/       # Case processing
│   │   │   │   └── page.tsx
│   │   │   ├── confirmation/      # Confirmation page
│   │   │   │   └── page.tsx
│   │   │   ├── api/[...path]/     # API proxy to backend
│   │   │   │   └── route.ts
│   │   │   ├── layout.tsx         # Root layout
│   │   │   └── globals.css        # Global styles
│   │   ├── components/
│   │   │   ├── ContactForm.tsx    # Reusable form
│   │   │   ├── Header.tsx         # DSFR header
│   │   │   ├── Footer.tsx         # DSFR footer
│   │   │   └── Spinner.css       # Loading spinner
│   │   └── utils/
│   │       ├── convertDateToISO.ts
│   │       └── convertISOToDate.ts
│   ├── public/                    # Static assets
│   ├── Dockerfile                 # Frontend container
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.ts
│
├── docker-compose.dev.yml         # Dev environment
├── docker-compose.prod.yml        # Production environment
└── README.md                      # This file

runtime/apps/delphes/              # Configuration (in root)
├── delphes.xlsx                   # Intent/field definitions
├── decision_engine.py             # Business rules
└── delphes-no-mail.xlsx          # No-email version
```

---

## 🎨 Frontend Technologies

### Core Stack
- **Next.js 15.5.4**: React framework with App Router
- **React 19.1.0**: UI library
- **TypeScript 5.0+**: Type safety
- **Turbopack**: Ultra-fast bundler

### UI & Styling
- **DSFR 1.14.2**: French government design system (@gouvfr/dsfr)
- **React DSFR 1.28.0**: React components (@codegouvfr/react-dsfr)
- **TailwindCSS 4.0+**: Utility-first CSS
- **Custom CSS**: DSFR-compliant styles

### HTTP & State
- **Axios 1.12.2**: HTTP client for API calls
- **SWR 2.3.6**: Data fetching and caching
- **localStorage**: Client-side state persistence

### Key Features Implementation

#### Date Handling
French format (DD/MM/YYYY) ↔ ISO format (YYYY-MM-DD)
```typescript
// utils/convertDateToISO.ts
export const convertDateToISO = (frenchDate: string): string => {
  const [day, month, year] = frenchDate.split('/');
  return `${year}-${month}-${day}`;
};
```

#### Dynamic Form Fields
Forms adapt based on detected intent:
```typescript
// Render fields based on intention
{intentionDetails.intention_fields?.map((champ: string) => (
  <div key={champ} className="fr-input-group">
    <label htmlFor={champ}>{getFieldLabel(champ)}</label>
    <input 
      type={getFieldType(champ)} 
      name={champ} 
      defaultValue={getFieldValue(champ)}
    />
  </div>
))}
```

#### API Proxy
Next.js API routes proxy requests to Python backend:
```typescript
// app/api/[...path]/route.ts
export async function POST(request: Request, { params }: Props) {
  const apiUrl = process.env.BACKEND_API_URL || 'http://localhost:8002';
  const response = await fetch(`${apiUrl}/${path}`, {
    method: 'POST',
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json' }
  });
  return response;
}
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env.local` in `frontend/`:
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8002

# Optional: Disable telemetry
NEXT_TELEMETRY_DISABLED=1
```

### Application Configuration

Main configuration files (in `runtime/apps/delphes/`):

#### delphes.xlsx

**Sheet: intentions**
Defines user intents:
- Residence permit renewal
- First-time residence permit
- Work permit
- Family reunification
- Status information
- etc.

**Sheet: intentions_examples**
Training examples for each intent:
```
intention_id: renouvellement_titre_sejour
example: "Je souhaite renouveler mon titre de séjour"
example: "Mon titre expire bientôt"
```

**Sheet: champs (fields)**
Data fields to extract:
- nom (last name)
- prenom (first name)
- date_naissance (birth date)
- nationalite (nationality)
- numero_AGDREF (ID number)
- date_expiration_titre_sejour (permit expiration)
- etc.

**Sheet: definitions**
Term definitions for LLM context

#### decision_engine.py

Business rules for case handling:
```python
from backend.decision.decision import Decision

class DelphesDecision(Decision):
    def execute_decision(self, case_request: dict) -> dict:
        intention_id = case_request.get('intention_id')
        field_values = case_request.get('field_values', {})
        
        # Apply prefecture-specific business rules
        if intention_id == 'renouvellement_titre_sejour':
            return self._handle_renewal(field_values)
        # ... more rules
```

---

## 🧪 Testing

### Run Tests

```bash
# In frontend directory
npm test                 # Unit tests (if configured)
npm run lint            # TypeScript and ESLint checks
npm run build           # Production build test
```

### Smoke Tests

```bash
# From repository root (requires Docker)
make test-smoke-frontend
```

### Manual Testing Checklist

- [ ] Contact form validation
- [ ] French date format handling (DD/MM/YYYY)
- [ ] Intent detection with various messages
- [ ] Dynamic field rendering
- [ ] Boolean field handling (checkboxes)
- [ ] Multi-page flow (localStorage state)
- [ ] Mobile responsiveness
- [ ] Accessibility (keyboard navigation)
- [ ] Error handling (API failures)
- [ ] Email confirmation generation

---

## 📦 Deployment

### Docker Deployment (Recommended)

#### Development
```bash
./docker-manage.sh start delphes dev
```

#### Production
```bash
./docker-manage.sh start delphes prod
```

### Manual Deployment

#### Build Frontend
```bash
cd apps/delphes/frontend
npm run build
npm start
```

#### Environment Configuration
Set `NEXT_PUBLIC_API_URL` to your backend URL:
```bash
export NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

### Docker Images

Build images:
```bash
# Backend (from repository root)
docker build -t delphes-backend -f Dockerfile.backend .

# Frontend
cd apps/delphes/frontend
docker build -t delphes-frontend .
```

---

## 🌍 Localization

### Supported Languages
- 🇫🇷 French (fr) - Primary
- 🇬🇧 English (en) - Secondary

### Implementation

Localization is managed through:
1. **Backend**: `src/backend/text_analysis/text_analysis_localization.py`
2. **Frontend**: DSFR components + custom locale handling

#### Adding Translations

**Frontend** (example with i18n):
```typescript
const translations = {
  fr: {
    'form.firstName': 'Prénom',
    'form.lastName': 'Nom'
  },
  en: {
    'form.firstName': 'First Name',
    'form.lastName': 'Last Name'
  }
};
```

**Backend**: Update Excel sheets with translated intent labels and field names

---

## 🔧 Customization

### Adding New Intent

1. **Update Configuration** (`delphes.xlsx`)
   - Add intent to `intentions` sheet
   - Add examples to `intentions_examples` sheet
   - Add required fields to `champs` sheet

2. **Update Business Rules** (`decision_engine.py`)
   ```python
   if intention_id == 'your_new_intent':
       return self._handle_new_intent(field_values)
   ```

3. **Test with Generic Client First**
   ```bash
   ./docker-manage.sh start framework
   # Test at http://localhost:8501
   ```

4. **Update Frontend** (if needed)
   - Add intent-specific UI in `analysis/page.tsx`
   - Add validation rules

### Styling Customization

All styles follow DSFR guidelines. To customize:

1. **Global Styles**: Edit `src/app/globals.css`
2. **Component Styles**: Use DSFR classes or Tailwind
3. **Theme**: Configure in DSFR provider

```tsx
<DsfrProvider defaultColorScheme="light">
  {/* Your app */}
</DsfrProvider>
```

---

## 🐛 Troubleshooting

### Common Issues

#### Frontend can't reach backend
**Symptom**: API calls fail with network errors

**Solution**:
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend is running: `curl http://localhost:8002/api/health`
- Check Docker network if using containers

#### Date conversion errors
**Symptom**: Invalid date format errors

**Solution**:
- Ensure dates are in DD/MM/YYYY format in form
- Check `convertDateToISO` utility is called
- Verify backend expects ISO format (YYYY-MM-DD)

#### Intent not detected
**Symptom**: AI doesn't recognize user's request

**Solution**:
- Add more examples to `intentions_examples` sheet
- Check LLM configuration and API keys
- Verify cache is not serving stale results
- Test with `read_from_cache=false`

#### Missing dynamic fields
**Symptom**: Form doesn't show expected fields

**Solution**:
- Check `intention_fields` in `delphes.xlsx`
- Verify field definitions in `champs` sheet
- Clear localStorage: `localStorage.clear()`

### Debug Mode

Enable detailed logging:

**Backend**:
```bash
export LOG_LEVEL=DEBUG
python launcher_api.py ./runtime
```

**Frontend**:
Add to component:
```typescript
useEffect(() => {
  console.log('Field values:', fieldValues);
  console.log('Selected intention:', selectedIntention);
}, [fieldValues, selectedIntention]);
```

---

## 📞 Support & Contact

### For Developers
- See main [README.md](../../README.md) for framework documentation
- Check [APPLICATIONS.md](../../APPLICATIONS.md) for integration guide
- Review [TESTING.md](../../TESTING.md) for test procedures

### For Users
- Contact your prefecture's digital services team
- Report accessibility issues to DINUM

---

## 📝 License

See [LICENSE](../../LICENSE) in repository root.

---

## 🙏 Acknowledgments

- **DSFR Team**: French government design system
- **Yvelines Prefecture**: Pilot project sponsor
- **Trusted Services Team**: Framework development
