# Ruleflow Editor

Visual editor for decision engine ruleflows in the Trusted Services framework.

## Features

- Browse and select runtime directories
- Create new runtime directories
- List and select applications
- Create new applications with decision engines
- Visual ruleflow editor with:
  - Package management (add, delete, reorder)
  - Package condition editing
  - Rule management (add, delete, reorder, edit)
  - Rule condition editing
  - Code editing with syntax highlighting

## Setup

1. Install dependencies:
```bash
cd config-rule
npm install
```

2. Set up the backend API endpoint in `next.config.ts` (update the proxy URL if needed)

3. Run the development server:
```bash
npm run dev
```

4. Open http://localhost:3001 in your browser

## Backend Integration

The frontend communicates with the FastAPI backend through the `/api/v1/ruleflow` endpoints. Make sure the backend is running and the ruleflow API router is included in the main FastAPI app.

The ruleflow API is automatically included in the backend when you import `src.backend.ruleflow.ruleflow_api` in the main FastAPI application.

## Environment Variables

- `TRUSTED_SERVICES_BASE_DIR`: Base directory for runtime directories (default: `/Users/joel/Documents/Dev/Athena/trusted-service`)

## Project Structure

```
config-rule/
├── app/
│   ├── components/          # React components
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main page
│   └── providers.tsx        # React Query provider
├── src/
│   └── backend/
│       └── ruleflow/        # Backend Python code (moved to src/backend/ruleflow/)
└── package.json             # Node.js dependencies
```

## Usage

1. Select a runtime directory from the dropdown
2. Select an application from the dropdown (or create a new one)
3. Edit the ruleflow structure:
   - Add/remove/reorder packages
   - Edit package conditions
   - Add/remove/reorder rules within packages
   - Edit rule code and conditions
4. Changes are automatically saved to the `decision_engine.py` file



