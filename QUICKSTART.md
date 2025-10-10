# 🚀 Avaire Quick Start Guide

**Last Updated:** October 11, 2025

---

## ⚡ TL;DR - Get Running in 3 Commands

```powershell
# 1. Setup prerequisites
.\setup.ps1

# 2. Start application
.\start.ps1

# 3. Access at http://localhost:3000
```

**First run:** 20-30 minutes (downloads ML models)  
**Subsequent runs:** 2-3 minutes

---

## 📋 Prerequisites

### Required Software
- **Docker Desktop** (latest version)
  - Download: https://www.docker.com/products/docker-desktop/
  - **Important:** Start Docker Desktop before running setup
  
- **Node.js 18+** (for setup script)
  - Download: https://nodejs.org/
  - Only needed for initial `package-lock.json` generation

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB free

**Recommended:**
- CPU: 8+ cores (faster ML processing)
- RAM: 16 GB (ML models are memory-intensive)
- Disk: 50 GB SSD
- GPU: NVIDIA with CUDA (optional, 10x faster)

### Docker Resource Allocation

Set in **Docker Desktop → Settings → Resources:**
```
CPUs: 4-6
Memory: 8-12 GB
Swap: 2 GB
Disk Image Size: 50 GB
```

---

## 🎯 Step-by-Step Setup

### Step 1: Clone Repository (if not done)
```powershell
git clone <repository-url>
cd avaire
```

### Step 2: Run Setup Script
```powershell
.\setup.ps1
```

**What it does:**
- ✅ Checks Docker installation
- ✅ Generates `frontend/package-lock.json`
- ✅ Creates storage directories
- ✅ Validates disk space
- ✅ Shows Docker resource recommendations

**Expected Output:**
```
🔧 Avaire Pre-Deployment Setup
================================

📦 Checking Node.js installation...
   ✓ Node.js v18.17.0 found

🐳 Checking Docker installation...
   ✓ Docker found
   ✓ Docker is running

📄 Checking frontend dependencies...
   ✓ package-lock.json exists

📁 Checking storage directories...
   ✓ storage exists
   ✓ storage/uploads exists
   ✓ storage/tryon_results exists
   ✓ storage/processed exists

💾 Checking disk space...
   ✓ Sufficient disk space: 45.32GB free

✅ Setup Complete - Ready to Deploy!
```

---

### Step 3: Start Application
```powershell
.\start.ps1
```

**Timeline (first run):**
```
00:00 → Building containers
15:00 → Backend build complete (ML dependencies)
17:00 → Frontend build complete
18:00 → Starting services
18:30 → PostgreSQL ready
19:00 → Backend downloading ML models
25:00 → All services healthy ✅
```

**Expected Output:**
```
🚀 Starting Avaire Application...

✓ Docker is running

🧹 Cleaning up existing containers...
🔨 Building containers...
🚀 Starting services...
⏳ Waiting for services to be ready...

📊 Service Status:
NAME                 STATUS
avaire_postgres      Up (healthy)
avaire_backend       Up (healthy)
avaire_frontend      Up

✅ Avaire is ready!

🌐 Access your application at:
   Frontend: http://localhost:3000
   Backend API: http://localhost:8000
   API Docs: http://localhost:8000/docs
   PostgreSQL: localhost:5432
```

---

## 🌐 Accessing the Application

### Frontend (User Interface)
```
URL: http://localhost:3000

Features:
- Homepage with hero carousel
- Product catalog browsing
- Virtual try-on studio
- Style DNA questionnaire
- User profile dashboard
```

### Backend API (Developer Interface)
```
URL: http://localhost:8000/docs

Interactive Swagger UI:
- Test all endpoints
- View request/response schemas
- Try authentication
- Upload test images
```

### Database (Direct Access)
```powershell
# Connect to PostgreSQL
docker exec -it avaire_postgres psql -U avaire_user -d avaire_db

# Run queries
SELECT * FROM users;
SELECT * FROM style_dna;

# Exit
\q
```

---

## 📊 Monitoring & Logs

### View All Logs (Live)
```powershell
docker-compose logs -f
```

### View Specific Service
```powershell
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres
```

### Check Service Health
```powershell
# All services status
docker-compose ps

# Backend health endpoint
curl http://localhost:8000/api/health
```

**Healthy Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "ml_pipeline": "initialized"
}
```

---

## 🛠️ Common Commands

### Stop Application
```powershell
docker-compose down
```

### Stop and Remove All Data
```powershell
docker-compose down -v
```
⚠️ **Warning:** This deletes the database!

### Restart Services
```powershell
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Rebuild After Code Changes
```powershell
# Rebuild all
docker-compose up --build -d

# Rebuild specific service
docker-compose up --build -d backend
```

### View Resource Usage
```powershell
docker stats
```

---

## 🧪 Testing the Deployment

### 1. Frontend Accessibility
```
Open: http://localhost:3000
Expected: Homepage with "Avaire | Fashion AI for Gen Z" title
```

### 2. Backend API
```powershell
# Health check
curl http://localhost:8000/api/health

# API documentation
# Open: http://localhost:8000/docs
```

### 3. Database Connection
```powershell
docker exec -it avaire_postgres psql -U avaire_user -d avaire_db -c "SELECT database_initialized();"

# Expected output:
#      database_initialized
# -----------------------------------------
#  Avaire database initialized successfully
```

### 4. ML Pipeline (After First Load)
```powershell
# Check backend logs for model downloads
docker-compose logs backend | Select-String "model"

# Expected (after ~10 minutes):
# "Downloading u2net model..."
# "Model loaded successfully"
```

---

## 🐛 Troubleshooting

### Issue: "Docker is not running"
**Solution:**
1. Open Docker Desktop
2. Wait for Docker engine to start
3. Run `.\setup.ps1` again

---

### Issue: Backend fails with "ModuleNotFoundError"
**Cause:** Python dependencies not installed

**Solution:**
```powershell
# Rebuild backend
docker-compose build backend --no-cache
docker-compose up -d backend
```

---

### Issue: Frontend shows "API connection failed"
**Cause:** Backend not ready or CORS issue

**Solution:**
```powershell
# Check backend health
curl http://localhost:8000/api/health

# Check backend logs
docker-compose logs backend | Select-String "ERROR"

# Restart if needed
docker-compose restart backend
```

---

### Issue: "Port 3000 is already in use"
**Cause:** Another application using port 3000

**Solution:**
```powershell
# Option 1: Stop other application
# Find process using port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess

# Option 2: Change Avaire port
# Edit docker-compose.yml → frontend → ports:
#   - "3001:3000"  # Use 3001 instead
```

---

### Issue: ML models keep re-downloading
**Cause:** Model cache not persisting

**Check:**
```yaml
# docker-compose.yml should have:
backend:
  volumes:
    - model-cache:/root/.cache  # ← This line

volumes:
  model-cache:  # ← This section
```

**Solution:**
Already fixed in latest docker-compose.yml ✅

---

### Issue: Database connection refused
**Cause:** PostgreSQL not ready yet

**Solution:**
```powershell
# Wait 30 seconds, then check
docker-compose logs postgres | Select-String "ready"

# Should see: "database system is ready to accept connections"

# Restart backend after postgres is ready
docker-compose restart backend
```

---

### Issue: Out of disk space during build
**Cause:** ML dependencies are large (~5-10 GB)

**Solution:**
```powershell
# Clean Docker cache
docker system prune -a

# Remove unused volumes
docker volume prune

# Free up at least 20 GB before retrying
```

---

## 📁 Project Structure

```
avaire/
├── backend/              # FastAPI Python backend
│   ├── main.py          # Application entry point
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy ORM models
│   ├── requirements.txt # Python dependencies
│   ├── Dockerfile       # Backend container config
│   ├── routers/         # API endpoints
│   └── services/        # Business logic
│
├── frontend/            # Next.js React app
│   ├── app/            # Next.js App Router
│   ├── components/     # React components
│   ├── lib/            # Utilities & API client
│   ├── package.json    # Node dependencies
│   └── Dockerfile      # Frontend container config
│
├── ml/                 # ML/AI pipeline
│   ├── pipeline.py     # Main ML orchestrator
│   ├── preprocessing.py # Image preprocessing
│   ├── recommendation.py # Recommendation engine
│   └── tryon.py        # Virtual try-on
│
├── data/               # Database initialization
│   ├── init.sql        # PostgreSQL setup
│   └── *_seed.json     # Sample data
│
├── storage/            # File storage (auto-created)
│   ├── uploads/        # User uploads
│   ├── tryon_results/  # Generated try-on images
│   └── processed/      # Processed images
│
├── docker-compose.yml  # Container orchestration
├── setup.ps1          # Pre-deployment setup
├── start.ps1          # Application launcher
├── README.md          # Project documentation
└── DEPLOYMENT_ANALYSIS.md  # Technical analysis
```

---

## 🔐 Security Notes

### Development (Current Setup)
✅ Acceptable for local development:
- Hardcoded credentials
- No HTTPS
- Debug mode enabled
- Wide-open CORS

### Production Checklist
❌ **DO NOT deploy to production without:**
- [ ] Secure password generation
- [ ] Environment variable management
- [ ] HTTPS with SSL certificates
- [ ] Restricted CORS origins
- [ ] Rate limiting
- [ ] Input validation
- [ ] Proper JWT implementation
- [ ] Database backups
- [ ] Monitoring & logging
- [ ] Resource limits

---

## 📚 Additional Resources

### Documentation
- **API Docs:** http://localhost:8000/docs
- **Technical Analysis:** [DEPLOYMENT_ANALYSIS.md](DEPLOYMENT_ANALYSIS.md)
- **Project README:** [README.md](README.md)

### Technology Docs
- **FastAPI:** https://fastapi.tiangolo.com/
- **Next.js:** https://nextjs.org/docs
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Docker:** https://docs.docker.com/

### ML/AI Models
- **PyTorch:** https://pytorch.org/docs/
- **Transformers:** https://huggingface.co/docs/transformers/
- **Diffusers:** https://huggingface.co/docs/diffusers/

---

## 💡 Pro Tips

### Speed Up Subsequent Builds
```powershell
# Use build cache
docker-compose build

# Only rebuild what changed
docker-compose up -d --build <service-name>
```

### Free Up Space
```powershell
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes (⚠️ deletes data!)
docker volume prune
```

### Development Workflow
```powershell
# Code change in backend
docker-compose restart backend  # Fast restart

# Code change in frontend
docker-compose restart frontend

# Database schema change
docker-compose down -v  # Delete DB
docker-compose up -d    # Recreate
```

---

## 🎯 Next Steps After Deployment

1. **Seed Database** (optional)
   ```powershell
   # Load sample data
   python data/generate_sample_data.py
   ```

2. **Test Virtual Try-On**
   - Upload test images
   - Process through ML pipeline
   - Check results in `/storage/`

3. **Explore API**
   - Visit http://localhost:8000/docs
   - Try different endpoints
   - Test authentication

4. **Monitor Performance**
   ```powershell
   # Watch resource usage
   docker stats
   
   # Check logs for errors
   docker-compose logs -f | Select-String "ERROR"
   ```

---

## 📞 Support

### Check Logs First
```powershell
docker-compose logs -f | Select-String "ERROR|WARN"
```

### Common Log Files
- Backend: `docker-compose logs backend`
- Frontend: `docker-compose logs frontend`
- Database: `docker-compose logs postgres`

### Health Checks
- Backend: http://localhost:8000/api/health
- Frontend: http://localhost:3000
- Database: `docker-compose ps postgres`

---

**Happy Coding! 🚀**

---

## Changelog

**October 11, 2025:**
- ✅ Created Dockerfiles for backend and frontend
- ✅ Added model cache volume
- ✅ Created setup.ps1 and start.ps1 scripts
- ✅ Updated Next.js config for standalone mode
- ✅ Created init.sql for PostgreSQL
- ✅ Added comprehensive documentation
