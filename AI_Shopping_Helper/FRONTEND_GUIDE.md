# 🎨 How to Run Frontend

## ⚠️ Important: Frontend Location

**Frontend is ONLY in the `main` branch!**
- ✅ **main branch** = Frontend (Next.js)
- ✅ **feature branch** = Backend/AI only

---

## 🚀 Quick Start (Easiest Way)

### **Option 1: Double-Click**
1. Double-click: `START_FRONTEND.bat`
2. Wait for dependencies to install (first time only)
3. Frontend opens at: **http://localhost:3000**

### **Option 2: Manual Steps**
```powershell
# 1. Switch to main branch
git checkout main

# 2. Go to frontend folder
cd frontend-nextjs

# 3. Install dependencies (first time only)
npm install

# 4. Run frontend
npm run dev
```

---

## 🎯 Run Both Backend + Frontend

### **Terminal 1: Backend**
```powershell
# Stay on feature branch
git checkout feature/complete-hypelens-system

# Run backend
python run_project.py
```
Backend at: **http://localhost:8000**

### **Terminal 2: Frontend**
```powershell
# Switch to main branch
git checkout main

# Go to frontend
cd frontend-nextjs

# Run frontend
npm run dev
```
Frontend at: **http://localhost:3000**

---

## 🆘 Troubleshooting

### "Frontend folder not found"
You're on the wrong branch!
```powershell
git checkout main
```

### "npm: command not found"
Node.js not installed!
- Download from: https://nodejs.org/
- Install Node.js 18+
- Restart terminal

### "EPERM: operation not permitted"
Close VS Code or other apps using the folder, then:
```powershell
cd frontend-nextjs
Remove-Item node_modules -Recurse -Force
npm install
```

### Port 3000 already in use
Another app is using the port:
```powershell
# Find process
netstat -ano | findstr :3000

# Kill it (replace XXXX with PID)
taskkill /PID XXXX /F
```

---

## ✅ Success Looks Like:

```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
event - compiled client and server successfully
```

Then open: **http://localhost:3000**

---

## 📋 Complete Setup Checklist

- [ ] Backend running on port 8000
- [ ] Switch to main branch: `git checkout main`
- [ ] Frontend folder exists: `frontend-nextjs/`
- [ ] Node.js installed: `node --version`
- [ ] Dependencies installed: `npm install`
- [ ] Frontend running on port 3000
- [ ] Both accessible in browser ✅

---

**Backend**: http://localhost:8000 (feature branch)  
**Frontend**: http://localhost:3000 (main branch)
