# Pre-deployment Setup Script for Avaire
# Run this BEFORE docker-compose to ensure all prerequisites

Write-Host "🔧 Avaire Pre-Deployment Setup" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$setupErrors = @()

# Check 1: Node.js installed
Write-Host "📦 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "   ✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    $setupErrors += "Node.js missing"
}

# Check 2: Docker installed
Write-Host "`n🐳 Checking Docker installation..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "   ✓ Docker found" -ForegroundColor Green
    
    # Check if Docker is running
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        $setupErrors += "Docker not running"
    }
} catch {
    Write-Host "   ✗ Docker not found! Please install Docker Desktop" -ForegroundColor Red
    $setupErrors += "Docker missing"
}

# Check 3: Frontend package-lock.json
Write-Host "`n📄 Checking frontend dependencies..." -ForegroundColor Yellow
if (Test-Path "frontend/package-lock.json") {
    Write-Host "   ✓ package-lock.json exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠ package-lock.json missing - generating..." -ForegroundColor Yellow
    
    Push-Location frontend
    try {
        Write-Host "   → Running npm install..." -ForegroundColor White
        npm install --silent
        
        if (Test-Path "package-lock.json") {
            Write-Host "   ✓ package-lock.json generated successfully" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Failed to generate package-lock.json" -ForegroundColor Red
            $setupErrors += "package-lock.json generation failed"
        }
    } catch {
        Write-Host "   ✗ npm install failed: $($_.Exception.Message)" -ForegroundColor Red
        $setupErrors += "npm install failed"
    } finally {
        Pop-Location
    }
}

# Check 4: Storage directories
Write-Host "`n📁 Checking storage directories..." -ForegroundColor Yellow
$storageDirs = @("storage", "storage/uploads", "storage/tryon_results", "storage/processed")
foreach ($dir in $storageDirs) {
    if (!(Test-Path $dir)) {
        Write-Host "   → Creating $dir..." -ForegroundColor White
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✓ Created $dir" -ForegroundColor Green
    } else {
        Write-Host "   ✓ $dir exists" -ForegroundColor Green
    }
}

# Check 5: Disk space
Write-Host "`n💾 Checking disk space..." -ForegroundColor Yellow
$drive = (Get-Location).Drive
$freeSpace = [math]::Round((Get-PSDrive $drive.Name).Free / 1GB, 2)
if ($freeSpace -lt 15) {
    Write-Host "   ⚠ Low disk space: ${freeSpace}GB free (recommend 15+ GB)" -ForegroundColor Yellow
    Write-Host "   → ML models will download ~5-10 GB" -ForegroundColor White
} else {
    Write-Host "   ✓ Sufficient disk space: ${freeSpace}GB free" -ForegroundColor Green
}

# Check 6: Docker resources
Write-Host "`n🎛️  Recommended Docker settings:" -ForegroundColor Yellow
Write-Host "   • CPUs: 4-6 cores" -ForegroundColor White
Write-Host "   • Memory: 8-12 GB" -ForegroundColor White
Write-Host "   • Swap: 2 GB" -ForegroundColor White
Write-Host "   → Check Docker Desktop → Settings → Resources" -ForegroundColor Cyan

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================" -ForegroundColor Cyan
if ($setupErrors.Count -eq 0) {
    Write-Host "✅ Setup Complete - Ready to Deploy!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "   1. Run: .\start.ps1" -ForegroundColor White
    Write-Host "   2. Wait 20-30 minutes for first build" -ForegroundColor White
    Write-Host "   3. Access: http://localhost:3000" -ForegroundColor White
    
    Write-Host "`n💡 Tip: Run 'docker-compose logs -f' in another terminal to watch progress" -ForegroundColor Yellow
} else {
    Write-Host "❌ Setup Failed - Please fix errors above" -ForegroundColor Red
    Write-Host "`nErrors found:" -ForegroundColor Yellow
    foreach ($error in $setupErrors) {
        Write-Host "   • $error" -ForegroundColor Red
    }
    exit 1
}
