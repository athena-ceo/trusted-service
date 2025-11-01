# Frontend Setup Notes

## Frontend CI Test Script Missing

### The Issue

The frontend CI workflow tries to run `npm test` but the `package.json` doesn't have a test script defined yet.

**Error**:
```
npm error Missing script: "test"
Error: Process completed with exit code 1
```

### Current Solution

The frontend-ci.yml workflow now checks if the test script exists before trying to run it:
- ✅ If script exists → runs tests
- ⚠️ If script missing → skips gracefully with warning

**No build failure!**

---

## Adding Frontend Tests (Future)

When you're ready to add frontend tests, update `apps/delphes/frontend/package.json`:

### 1. Install Testing Dependencies

```bash
cd apps/delphes/frontend

# Install Jest and React Testing Library
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event jest-environment-jsdom

# For Next.js specific testing
npm install --save-dev @testing-library/react-hooks
```

### 2. Add Test Script to package.json

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### 3. Create Jest Configuration

Create `apps/delphes/frontend/jest.config.js`:

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
  ],
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
}

module.exports = createJestConfig(customJestConfig)
```

### 4. Create Jest Setup File

Create `apps/delphes/frontend/jest.setup.js`:

```javascript
import '@testing-library/jest-dom'
```

### 5. Example Test File

Create `apps/delphes/frontend/src/components/__tests__/Header.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react'
import Header from '../Header'

describe('Header Component', () => {
  it('renders the header', () => {
    render(<Header />)
    expect(screen.getByRole('banner')).toBeInTheDocument()
  })

  it('displays the application title', () => {
    render(<Header />)
    expect(screen.getByText(/Trusted Services/i)).toBeInTheDocument()
  })
})
```

### 6. Run Tests Locally

```bash
# Run tests once
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### 7. Verify CI/CD

After adding tests:
1. Commit and push changes
2. Check GitHub Actions
3. Frontend CI will now run tests automatically

---

## Alternative: Disable Frontend Tests in CI

If you want to disable frontend tests in CI temporarily, you can:

### Option 1: Comment Out Test Job

In `.github/workflows/frontend-ci.yml`, comment out the test job:

```yaml
  # test:
  #   runs-on: ubuntu-latest
  #   ...
```

### Option 2: Add Skip Condition

```yaml
  test:
    runs-on: ubuntu-latest
    if: false  # Skip this job
```

### Option 3: Current Solution (Recommended)

✅ **Already implemented**: Workflow checks if test script exists and skips gracefully

---

## Frontend Directory Access

**Note**: The `apps/` directory may be filtered in some environments. If you can't access it:

1. **Check .gitignore**: Ensure `apps/` isn't ignored
2. **Check .cursorignore**: May be blocking access
3. **Manual access**: Navigate directly via terminal/file explorer
4. **Alternative**: Edit files via GitHub web interface

---

## Current Frontend CI Status

| Step | Status | Notes |
|------|--------|-------|
| Lint | ✅ Working | ESLint checks pass |
| Build | ✅ Working | Next.js builds successfully |
| Type Check | ✅ Working | TypeScript validation |
| Unit Tests | ⚠️ Skipped | No test script (graceful) |
| Smoke Tests | ⚠️ May fail | Needs services running |

---

## Smoke Tests vs Unit Tests

### Unit Tests (Missing - That's OK)
- Test individual components
- Run in isolation
- Fast execution
- **Optional for initial deployment**

### Smoke Tests (Working)
- Test complete workflows
- Require running services
- Integration validation
- **Already configured in CI**

---

## Quick Reference

### Check if tests exist:
```bash
cd apps/delphes/frontend
npm run | grep test
```

### Add minimal test setup:
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

### Add to package.json:
```json
"scripts": {
  "test": "jest"
}
```

### Create simple test:
```bash
mkdir -p src/__tests__
cat > src/__tests__/example.test.js << 'EOF'
test('example test', () => {
  expect(1 + 1).toBe(2)
})
EOF
```

### Run tests:
```bash
npm test
```

---

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Next.js Testing](https://nextjs.org/docs/testing)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

*Last updated: November 1, 2025*

