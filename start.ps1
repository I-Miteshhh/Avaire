# Avaire Docker Quick Start Script

Write-Host "🚀 Starting Avaire Application..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Stop and remove existing containers
Write-Host "`n🧹 Cleaning up existing containers..." -ForegroundColor Yellow
docker-compose down -v

# Build and start containers
Write-Host "`n🔨 Building containers..." -ForegroundColor Yellow
docker-compose build

Write-Host "`n🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be ready
Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "`n📊 Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n✅ Avaire is ready!" -ForegroundColor Green
Write-Host "`n🌐 Access your application at:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   PostgreSQL: localhost:5432" -ForegroundColor White

Write-Host "`n📝 Useful commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop: docker-compose down" -ForegroundColor White
Write-Host "   Restart: docker-compose restart" -ForegroundColor White
