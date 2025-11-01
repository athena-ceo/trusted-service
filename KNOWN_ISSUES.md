# Known Issues and Solutions

## 🔴 Critical: Pydantic Version Mismatch

### Issue Description

The codebase uses **Pydantic v2** syntax (`field_validator`), but the environment may have **Pydantic v1** installed (1.10.x), causing import errors:

```python
ImportError: cannot import name 'field_validator' from 'pydantic'
Did you mean: 'root_validator'?
```

### Why This Happens

- FastAPI 0.115.11 requires `pydantic` but doesn't pin a specific version
- If installed fresh, pip may install Pydantic v1.10.x for compatibility
- The source code at `src/common/config.py` uses Pydantic v2 syntax:
  ```python
  from pydantic import BaseModel, field_validator  # ← v2 syntax
  ```

### ✅ Solution 1: Update requirements.txt (Recommended)

**Status**: ✅ **FIXED** - requirements.txt now specifies Pydantic v2

The `requirements.txt` has been updated to explicitly require Pydantic v2:

```txt
pydantic>=2.9.0
```

**To apply the fix**:

```bash
# Reinstall with updated requirements
pip install -r requirements.txt --upgrade

# Or upgrade Pydantic directly
pip install 'pydantic>=2.9.0' --upgrade
```

### ✅ Solution 2: Manual Upgrade

If you already have the environment set up:

```bash
# Activate virtual environment
source .venv/bin/activate  # or tsvenv/bin/activate

# Upgrade Pydantic to v2
pip install --upgrade 'pydantic>=2.9.0'

# Verify version
pip show pydantic
# Should show: Version: 2.9.0 or higher
```

### Verification

After upgrading, verify the backend starts without errors:

```bash
python launcher_api.py ./runtime
```

You should see the server start successfully without import errors.

---

## 🟡 Moderate: SSL Certificate Warning (macOS)

### Issue Description

When installing packages, you may see SSL warnings:

```
WARNING: Retrying after connection broken by 'SSLError(SSLCertVerificationError('OSStatus -26276'))'
```

### Why This Happens

- macOS keychain certificate issues
- Does not prevent package installation (pip retries)
- Common on newer macOS versions

### ✅ Solution

**Option 1: Ignore (Recommended)**
- Warnings are informational
- Pip automatically retries
- Packages install successfully

**Option 2: Fix SSL Certificates**

```bash
# Install/update certificates
/Applications/Python\ 3.12/Install\ Certificates.command

# Or update pip
pip install --upgrade pip certifi
```

---

## 🟡 Moderate: Pip Cache Warning

### Issue Description

```
WARNING: The directory '/Users/.../Library/Caches/pip' is not owned or is not writable
```

### Why This Happens

- Permission issues with pip cache directory
- Does not affect functionality

### ✅ Solution

**Option 1: Ignore (Recommended)**
- Does not affect package installation
- Just disables caching

**Option 2: Fix Permissions**

```bash
# Fix cache directory permissions
sudo chown -R $USER ~/Library/Caches/pip

# Or disable cache
pip install --no-cache-dir -r requirements.txt
```

---

## 🟢 Minor: Backend Import Dependencies

### Issue Description

Backend requires all dependencies from `requirements.txt` to import successfully.

### ✅ Solution

Always install dependencies before running backend:

```bash
pip install -r requirements.txt
```

---

## 🟢 Minor: Frontend Tests Require Services

### Issue Description

Frontend smoke tests require both backend and frontend services to be running.

### ✅ Solution

**Option 1: Use test runner (Auto-starts services)**

```bash
python run_tests.py smoke --frontend
```

**Option 2: Manual service startup**

```bash
# Terminal 1: Backend
python launcher_api.py ./runtime

# Terminal 2: Frontend
cd apps/delphes/frontend && npm run dev

# Terminal 3: Tests
pytest tests/smoke/test_frontend.py
```

---

## 🟢 Minor: Playwright Browsers Not Installed

### Issue Description

```
Error: browserType.launch: Executable doesn't exist
```

### ✅ Solution

Install Playwright browsers:

```bash
playwright install chromium

# Or install all browsers
playwright install
```

---

## 🟢 Minor: Port Already in Use

### Issue Description

```
Error: Address already in use (port 8002 or 3000)
```

### ✅ Solution

**Option 1: Use Make helper**

```bash
make kill-servers
```

**Option 2: Manual cleanup**

```bash
# macOS/Linux
lsof -ti :8002 | xargs kill -9
lsof -ti :3000 | xargs kill -9

# Windows
netstat -ano | findstr :8002
taskkill /PID <PID> /F
```

---

## 📋 Compatibility Matrix

### Python Versions

| Version | Status | Notes |
|---------|--------|-------|
| 3.11 | ✅ Supported | Recommended |
| 3.12 | ✅ Supported | Current |
| 3.10 | ⚠️ Untested | Should work |
| 3.13 | ⚠️ Untested | May have issues |

### Pydantic Versions

| Version | Status | Notes |
|---------|--------|-------|
| 1.x | ❌ Not compatible | Code uses v2 syntax |
| 2.9+ | ✅ Required | Recommended |
| 2.0-2.8 | ⚠️ May work | Not tested |

### Operating Systems

| OS | Status | Notes |
|-----|--------|-------|
| macOS | ✅ Tested | Primary development |
| Linux | ✅ Supported | CI/CD tested |
| Windows | ⚠️ Should work | Use `run_tests.py` |

---

## 🔧 Troubleshooting Checklist

If you encounter issues, work through this checklist:

### 1. Environment Setup

```bash
# ✓ Check Python version
python3 --version  # Should be 3.11+

# ✓ Virtual environment active?
which python3  # Should point to venv

# ✓ Dependencies installed?
pip list | grep pydantic  # Should show 2.9+
pip list | grep fastapi   # Should show 0.115+
```

### 2. Pydantic Version

```bash
# ✓ Check Pydantic version
pip show pydantic

# ✗ If version is 1.x, upgrade:
pip install --upgrade 'pydantic>=2.9.0'
```

### 3. Backend Startup

```bash
# ✓ Try starting backend
python launcher_api.py ./runtime

# ✗ If import errors:
pip install -r requirements.txt --upgrade
```

### 4. Test Execution

```bash
# ✓ Try unit tests (no services needed)
pytest tests/unit/ -v

# ✓ Try smoke tests
python run_tests.py smoke --backend
```

---

## 🆘 Getting Help

If you still have issues:

1. **Check this document** for known solutions
2. **Review logs** for specific error messages
3. **Check GitHub Actions** logs if CI/CD fails
4. **Verify versions** match compatibility matrix
5. **Create an issue** with:
   - Python version (`python3 --version`)
   - Pydantic version (`pip show pydantic`)
   - Complete error message
   - Steps to reproduce

---

## 📝 Resolution Status

| Issue | Status | Priority | Resolution |
|-------|--------|----------|------------|
| Pydantic v1/v2 mismatch | ✅ Fixed | 🔴 Critical | Updated requirements.txt |
| SSL warnings | 📋 Documented | 🟡 Moderate | Ignore or fix certs |
| Pip cache warning | 📋 Documented | 🟡 Moderate | Ignore or fix perms |
| Port conflicts | 📋 Documented | 🟢 Minor | Use helpers |
| Playwright browsers | 📋 Documented | 🟢 Minor | Install browsers |

---

## ✅ Quick Fix Commands

```bash
# Fix Pydantic version (most common issue)
pip install --upgrade 'pydantic>=2.9.0'

# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# Install test dependencies
pip install -r tests/requirements.txt

# Install Playwright browsers
playwright install chromium

# Kill stuck servers
make kill-servers
```

---

*Last updated: November 1, 2025*

