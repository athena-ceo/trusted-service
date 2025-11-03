# Trusted Services Studio

The comprehensive UI for the Trusted Services **framework**. Studio provides testing, configuration, and management capabilities for all applications built on the framework. Built with Next.js, TypeScript, and Tailwind CSS, it replaces the legacy Streamlit test client with a modern, extensible interface.

**Note**: Studio is framework-level infrastructure, not an application. It resides at the root level alongside `src/`, `apps/`, and `runtime/`.

**Copyright © 2025 Athena Decision Systems. All rights reserved.**

## Features

### Current (v1.0 - Testing)
- ✅ **Full API Coverage**: Connects to all Trusted Services v2 endpoints
- 🎨 **Modern UI**: Built with Next.js 15, React 19, Tailwind CSS
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🔄 **Real-time Updates**: React Query for efficient data fetching
- 🎯 **Type-Safe**: Full TypeScript support matching backend models
- 🚀 **Fast & Efficient**: Optimized performance with caching
- 🦉 **Athena Branding**: Professional UI with company logo and favicon

### Planned (Future)
- 🔧 **Configuration UI**: Visual editor for application settings
- 📊 **Analytics Dashboard**: Performance and usage metrics
- 👥 **User Management**: Access control and permissions
- 🔌 **Plugin System**: Extensible architecture for custom tools

## Architecture

```
┌──────────────────────────┐
│  Trusted Services Studio │  Port 3001
│  (Framework UI)          │
└──────────┬───────────────┘
           │ REST API
           ▼
┌──────────────────────────┐
│  FastAPI Backend         │  Port 8002
│  (Framework Core)        │
└──────────┬───────────────┘
           │
           ├─► Delphes (French prefecture)
           ├─► AISA (Finnish municipalities)
           └─► conneXion (Asylum seekers)
```

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack React Query (React Query)
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **UI Components**: Custom components with Tailwind

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Set environment variables
echo "NEXT_PUBLIC_API_URL=http://localhost:8002" > .env.local

# Start development server
npm run dev

# Open browser
open http://localhost:3000
```

### With Docker

```bash
# From project root
docker compose -f studio/docker-compose.dev.yml up -d

# Access at http://localhost:3001
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8002` |
| `NEXT_TELEMETRY_DISABLED` | Disable Next.js telemetry | `1` |

## Project Structure

```
studio/  # Framework UI (Testing + Configuration + Management)
├── app/                      # Next.js app directory
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── providers.tsx        # React Query provider
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── ui/                  # Base UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── textarea.tsx
│   │   └── badge.tsx
│   └── test-client/         # Application-specific components
├── lib/                     # Core logic
│   ├── api/                 # API client & types
│   │   ├── client.ts       # API client with all endpoints
│   │   └── types.ts        # TypeScript types matching backend
│   ├── store/              # State management
│   │   └── useTestClientStore.ts
│   └── utils/              # Utilities
│       └── cn.ts           # Class name utility
├── public/                  # Static assets
├── Dockerfile              # Production Docker image
├── docker-compose.dev.yml  # Development stack
└── package.json            # Dependencies
```

## API Client

The API client (`lib/api/client.ts`) provides methods for all backend endpoints:

```typescript
import { apiClient } from "@/lib/api/client";

// Get all available applications
const apps = await apiClient.getAppIds();

// Analyze text
const result = await apiClient.analyze({
  appId: "delphes",
  locale: "fr",
  fieldValues: {},
  text: "Je souhaite renouveler mon titre de séjour",
  readFromCache: false,
  llmConfigId: "default"
});

// Handle case
const response = await apiClient.handleCase(
  "delphes",
  "fr",
  caseRequest
);
```

## State Management

Global state is managed with Zustand:

```typescript
import { useTestClientStore } from "@/lib/store/useTestClientStore";

function MyComponent() {
  const { selectedAppId, setSelectedApp } = useTestClientStore();
  
  return (
    <button onClick={() => setSelectedApp("delphes")}>
      Select Delphes
    </button>
  );
}
```

## Development

### Available Scripts

```bash
npm run dev          # Start development server (port 3000)
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Adding New Components

1. Create component in `components/ui/` or `components/test-client/`
2. Use TypeScript for type safety
3. Style with Tailwind CSS
4. Export from component file

### Type Safety

All API responses are typed using interfaces in `lib/api/types.ts` that match the backend Pydantic models.

## Docker Deployment

### Build Image

```bash
docker build -t test-client:latest .
```

### Run Container

```bash
docker run -p 3001:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8002 \
  test-client:latest
```

## Comparison with Streamlit Client

| Feature | Streamlit | React (This App) |
|---------|-----------|------------------|
| **Technology** | Python + Streamlit | TypeScript + Next.js |
| **Performance** | Server-rendered | Client-side + SSR |
| **UI/UX** | Basic Streamlit widgets | Modern, custom components |
| **Responsiveness** | Limited | Fully responsive |
| **Type Safety** | Python hints | Full TypeScript |
| **State Management** | Session state | Zustand |
| **Deployment** | Python server | Static export or Node.js |

## Future Enhancements

- [ ] Complete 3-stage workflow UI
- [ ] Dynamic field rendering based on case model
- [ ] Intent scoring visualization (bar charts, confidence meters)
- [ ] Syntax-highlighted JSON viewer for responses
- [ ] Export results (PDF, JSON)
- [ ] Dark mode support
- [ ] Multilingual UI (fr/en/fi)
- [ ] Advanced filtering and search
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements (WCAG 2.1)

## Troubleshooting

### Cannot connect to backend

```
Error: connect ECONNREFUSED 127.0.0.1:8002
```

**Solution**: Ensure the backend is running:
```bash
cd /path/to/trusted-service
python launcher_api.py ./runtime
```

### Port already in use

```
Error: Port 3000 is already in use
```

**Solution**: Use a different port:
```bash
PORT=3001 npm run dev
```

## Contributing

When adding features:

1. Maintain type safety
2. Follow existing component patterns
3. Update this README
4. Test with multiple applications (Delphes, AISA, conneXion)

## License

Copyright © 2025 Athena Decision Systems. All rights reserved.

This software is proprietary to Athena Decision Systems. Unauthorized copying, modification, distribution, or use of this software, via any medium, is strictly prohibited without the express written permission of Athena Decision Systems.
