# Test Client Architecture

## Overview

The React Test Client is a modern, type-safe web application that provides a beautiful UI for testing all Trusted Services applications. It replaces the Python Streamlit test client with a full-featured React application.

## Technology Stack

### Core Framework
- **Next.js 15**: React framework with App Router
- **React 19**: UI library
- **TypeScript**: Type safety throughout

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Custom Components**: Modern UI components built from scratch

### State Management
- **Zustand**: Lightweight state management
- **React Query**: Server state & caching

### API Communication
- **Axios**: HTTP client
- **TypeScript Types**: Full type safety matching backend Pydantic models

### Development
- **ESLint**: Code linting
- **Turbopack**: Fast development bundler (Next.js 15)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (Client)                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           React Test Client (Next.js)                │  │
│  │                                                      │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐   │  │
│  │  │  Pages     │  │ Components │  │  UI Layer  │   │  │
│  │  │  (Routes)  │  │  (Logic)   │  │  (Styled)  │   │  │
│  │  └─────┬──────┘  └─────┬──────┘  └────────────┘   │  │
│  │        │                │                           │  │
│  │        └────────┬───────┘                           │  │
│  │                 │                                   │  │
│  │        ┌────────▼────────┐                          │  │
│  │        │  Zustand Store  │                          │  │
│  │        └────────┬────────┘                          │  │
│  │                 │                                   │  │
│  │        ┌────────▼────────┐                          │  │
│  │        │  React Query    │                          │  │
│  │        └────────┬────────┘                          │  │
│  │                 │                                   │  │
│  │        ┌────────▼────────┐                          │  │
│  │        │   API Client    │                          │  │
│  │        │   (axios)       │                          │  │
│  │        └────────┬────────┘                          │  │
│  └─────────────────┼──────────────────────────────────┘  │
└────────────────────┼─────────────────────────────────────┘
                     │
                     │ HTTP REST API
                     │ (JSON)
                     │
┌────────────────────▼─────────────────────────────────────┐
│              Backend (FastAPI + Python)                  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │   Trusted Services Framework                       │ │
│  │   - Text Analysis                                  │ │
│  │   - Decision Engine                                │ │
│  │   - Distribution                                   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │   Applications                                     │ │
│  │   - Delphes (French prefecture)                   │ │
│  │   - AISA (Finnish municipalities)                 │ │
│  │   - conneXion (Asylum seekers)                    │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Application Initialization

```
User Opens App
     │
     ├─► React Query: Fetch app_ids
     │        │
     │        └─► API Client: GET /trusted_services/v2/app_ids
     │                 │
     │                 └─► Backend: Returns ["delphes", "AISA", "conneXion"]
     │                          │
     │                          └─► React: Display app cards
     │
     └─► Zustand: Initialize store with default state
```

### 2. App Selection

```
User Selects App (e.g., "delphes")
     │
     ├─► Zustand: Update selectedAppId
     │
     ├─► React Query: Fetch metadata
     │        ├─► GET /apps/delphes/locales → ["fr", "en"]
     │        ├─► GET /apps/delphes/llm_config_ids → ["default", "scaleway1"]
     │        └─► GET /apps/delphes/decision_engine_config_ids → ["tests"]
     │
     └─► React Query: Fetch app-specific data
              ├─► GET /apps/delphes/fr/app_name → "Delphes"
              ├─► GET /apps/delphes/fr/app_description → "..."
              ├─► GET /apps/delphes/fr/sample_message → "..."
              └─► GET /apps/delphes/fr/case_model → CaseModel
```

### 3. Text Analysis (Stage 1 → 2)

```
User Enters Text + Fills Fields + Clicks "Analyze"
     │
     ├─► Zustand: Update requestText, fieldValues
     │
     ├─► API Client: POST /apps/delphes/fr/analyze
     │        │
     │        ├─► Request Body: {
     │        │     field_values: {...},
     │        │     text: "...",
     │        │     read_from_cache: true,
     │        │     llm_config_id: "default"
     │        │   }
     │        │
     │        └─► Backend: LLM processes text
     │                 │
     │                 └─► Returns: {
     │                       scorings: [
     │                         {intention_id: "...", score: 0.95, ...}
     │                       ],
     │                       highlighted_text: "...",
     │                       extracted_fields: {...}
     │                     }
     │
     └─► React: Display analysis results
              ├─► Intent rankings with scores
              ├─► Extracted field values
              └─► Highlighted text
```

### 4. Case Handling (Stage 2 → 3)

```
User Selects Intent + Clicks "Handle Case"
     │
     ├─► Zustand: Update selectedIntentionId
     │
     ├─► API Client: POST /apps/delphes/fr/handle_case
     │        │
     │        ├─► Request Body: {
     │        │     intention_id: "renouvellement_titre",
     │        │     field_values: {...},
     │        │     decision_engine_config_id: "tests"
     │        │   }
     │        │
     │        └─► Backend: Decision engine processes case
     │                 │
     │                 ├─► Rule evaluation
     │                 ├─► Decision making
     │                 └─► Response generation
     │                          │
     │                          └─► Returns: {
     │                                case_handling_decision_output: {
     │                                  handling: "AUTO"
     │                                },
     │                                case_handling_response: {
     │                                  acknowledgement: "...",
     │                                  case_handling_report: [...]
     │                                }
     │                              }
     │
     └─► React: Display final results
              ├─► Decision outcome (AUTO/AGENT/DEFLECTION)
              ├─► Generated emails
              └─► Complete case report
```

## File Structure

```
apps/test-client/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout with metadata
│   ├── page.tsx                 # Home page (main UI)
│   ├── providers.tsx            # React Query provider setup
│   └── globals.css              # Global Tailwind styles
│
├── components/                   # React components
│   ├── ui/                      # Reusable UI components
│   │   ├── button.tsx          # Button with variants
│   │   ├── card.tsx            # Card container components
│   │   ├── input.tsx           # Text input
│   │   ├── label.tsx           # Form label
│   │   ├── textarea.tsx        # Multi-line text input
│   │   └── badge.tsx           # Status badge
│   │
│   └── test-client/             # Application-specific components
│       ├── sidebar.tsx          # App/locale selector (planned)
│       ├── workflow-stepper.tsx # Progress indicator (planned)
│       ├── field-input.tsx      # Dynamic field renderer (planned)
│       ├── analysis-stage.tsx   # Stage 1 UI (planned)
│       ├── selection-stage.tsx  # Stage 2 UI (planned)
│       └── results-stage.tsx    # Stage 3 UI (planned)
│
├── lib/                          # Core application logic
│   ├── api/                     # API communication
│   │   ├── client.ts           # Axios-based API client
│   │   └── types.ts            # TypeScript interfaces (Pydantic models)
│   │
│   ├── store/                   # State management
│   │   └── useTestClientStore.ts # Zustand store
│   │
│   └── utils/                   # Utility functions
│       └── cn.ts               # Tailwind class merger
│
├── public/                       # Static assets
│   └── (images, fonts, etc.)
│
├── Dockerfile                    # Production container build
├── docker-compose.dev.yml        # Dev stack (planned)
├── next.config.ts               # Next.js configuration
├── tailwind.config.ts           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── package.json                 # Dependencies
├── README.md                    # User documentation
└── ARCHITECTURE.md              # This file
```

## State Management

### Zustand Store

The `useTestClientStore` manages all application state:

```typescript
{
  // Selection state
  selectedAppId: string | null,
  selectedLocale: SupportedLocale | null,
  selectedLlmConfigId: string | null,
  selectedDecisionEngineConfigId: string | null,

  // App metadata (from API)
  appName: string | null,
  appDescription: string | null,
  sampleMessage: string | null,
  caseModel: CaseModel | null,

  // User input
  fieldValues: CaseFieldValues,     // Dynamic field values
  requestText: string,               // User's text input

  // Settings
  readFromCache: boolean,
  showDetails: boolean,

  // Workflow progress
  currentStage: 1 | 2 | 3,
  analysisResponse: AnalysisResponse | null,
  selectedIntentionId: string | null,
  caseHandlingResponse: CaseHandlingDetailedResponse | null,

  // Actions (setters)
  setSelectedApp(appId, locale?): void,
  setSelectedLocale(locale): void,
  // ... (all other actions)
}
```

### React Query Cache

React Query handles server state with automatic caching:

```typescript
{
  queries: {
    ['appIds']: string[],                           // All available apps
    ['locales', appId]: SupportedLocale[],          // Available locales
    ['llmConfigIds', appId]: string[],              // LLM configs
    ['decisionEngineConfigIds', appId]: string[],   // Decision configs
    ['appName', appId, locale]: string,             // Localized app name
    ['appDescription', appId, locale]: string,      // App description
    ['sampleMessage', appId, locale]: string,       // Example message
    ['caseModel', appId, locale]: CaseModel,        // Field definitions
  },
  
  mutations: {
    analyze: AnalysisResponse,
    handleCase: CaseHandlingDetailedResponse,
    saveCache: void,
  }
}
```

## Type Safety

All API responses are strongly typed using TypeScript interfaces that match the backend Pydantic models:

```typescript
// Example: CaseModel from backend
// Python (Pydantic)
class CaseField(BaseModel):
    id: str
    label: str
    type: Literal["str", "date", "bool", "int", "float"]
    scope: Literal["CONTEXT", "REQUEST"]
    mandatory: bool
    # ...

// TypeScript
interface CaseField {
  id: string;
  label: string;
  type: "str" | "date" | "bool" | "int" | "float";
  scope: "CONTEXT" | "REQUEST";
  mandatory: boolean;
  // ...
}
```

This ensures compile-time safety and prevents runtime errors from API mismatches.

## Performance Optimizations

### 1. React Query Caching
- **Default stale time**: 1 minute
- **Automatic refetch**: On window focus (disabled)
- **Cache persistence**: In-memory

### 2. Next.js Optimizations
- **Code splitting**: Automatic per-route
- **Image optimization**: Next.js Image component (when used)
- **Font optimization**: Automatic Google Fonts optimization

### 3. Tailwind CSS
- **PurgeCSS**: Removes unused styles in production
- **JIT mode**: Generates only needed utilities
- **Minimal bundle**: Only classes actually used

### 4. Docker Build
- **Multi-stage build**: Reduces final image size
- **Standalone output**: No node_modules in production
- **Alpine base**: Minimal Linux distribution

## Security Considerations

### API Communication
- **CORS**: Backend must whitelist frontend origin
- **HTTPS**: Use in production (not enforced in dev)
- **No authentication**: Currently open API (add if needed)

### Input Validation
- **Client-side**: TypeScript types prevent type errors
- **Server-side**: Backend validates all inputs (Pydantic)
- **Sanitization**: Backend escapes HTML in responses

### Docker
- **Non-root user**: Container runs as `nextjs:nodejs`
- **Read-only filesystem**: Only writable dirs needed
- **No secrets in image**: Environment variables only

## Deployment Options

### 1. Docker Container (Recommended)
```bash
docker build -t test-client:latest .
docker run -p 3001:3000 \
  -e BACKEND_INTERNAL_URL=http://backend:8002 \
  test-client:latest
```

### 2. Node.js Server
```bash
npm run build
npm run start
```

### 3. Static Export (Limited)
```bash
npm run build
# Serve .next/out directory
```

Note: Static export doesn't support all Next.js features (no API routes, no dynamic SSR).

## Future Enhancements

### Short-term (Current Sprint)
- [ ] Complete 3-stage workflow UI
- [ ] Dynamic field rendering based on CaseModel
- [ ] Intent selection with scoring visualization
- [ ] Results display with syntax-highlighted JSON

### Medium-term
- [ ] Dark mode support
- [ ] Multilingual UI (fr/en/fi)
- [ ] Export results (PDF, JSON, CSV)
- [ ] Advanced filtering and search
- [ ] Keyboard shortcuts

### Long-term
- [ ] Real-time collaboration
- [ ] Test case management
- [ ] Diff viewer for comparing runs
- [ ] Performance monitoring dashboard
- [ ] A/B testing for LLM configs

## Testing Strategy

### Unit Tests (Planned)
- Component rendering
- Store actions
- API client methods
- Utility functions

### Integration Tests (Planned)
- Complete workflow (Stage 1 → 2 → 3)
- API error handling
- State persistence

### E2E Tests (Planned)
- User journeys with Playwright
- Cross-browser testing
- Accessibility testing (WCAG 2.1)

## Contributing

When adding features:

1. **Follow TypeScript strictly**: No `any` types
2. **Use existing patterns**: Match component structure
3. **Keep UI consistent**: Use design tokens from Tailwind config
4. **Document complex logic**: Inline comments for non-obvious code
5. **Test with all apps**: Verify with Delphes, AISA, and conneXion

## Resources

- **Next.js Docs**: https://nextjs.org/docs
- **React Query**: https://tanstack.com/query/latest
- **Zustand**: https://zustand-demo.pmnd.rs/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **TypeScript**: https://www.typescriptlang.org/docs

