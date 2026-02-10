# ═════════════════════════════════════════════════════════════════════
# CyberGuardX — Docker Quick Start Script (Windows PowerShell)
# ═════════════════════════════════════════════════════════════════════
# Usage: .\start-docker.ps1 [dev|prod|stop|rebuild]
# ═════════════════════════════════════════════════════════════════════

param(
    [Parameter(Position=0)]
    [ValidateSet('dev', 'prod', 'stop', 'rebuild', 'logs', 'status', 'clean')]
    [string]$Command = 'dev'
)

# Colors for output
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"
$ErrorColor = "Red"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-Banner {
    Write-ColorOutput "`n═══════════════════════════════════════════════════" $InfoColor
    Write-ColorOutput "   🛡️  CyberGuardX — Docker Deployment" $InfoColor
    Write-ColorOutput "═══════════════════════════════════════════════════`n" $InfoColor
}

function Test-DockerInstalled {
    try {
        $null = docker --version
        return $true
    } catch {
        Write-ColorOutput "❌ Error: Docker is not installed or not in PATH" $ErrorColor
        Write-ColorOutput "   Download from: https://www.docker.com/products/docker-desktop" $InfoColor
        return $false
    }
}

function Test-DockerRunning {
    try {
        $null = docker ps 2>&1
        return $true
    } catch {
        Write-ColorOutput "❌ Error: Docker is not running" $ErrorColor
        Write-ColorOutput "   Please start Docker Desktop and try again" $InfoColor
        return $false
    }
}

function Start-Development {
    Write-ColorOutput "🚀 Starting CyberGuardX in DEVELOPMENT mode..." $InfoColor
    Write-ColorOutput "   - Hot-reload enabled" $SuccessColor
    Write-ColorOutput "   - Source code mounted as volume" $SuccessColor
    Write-ColorOutput "   - Logs visible in console`n" $SuccessColor
    
    docker-compose up
}

function Start-Production {
    Write-ColorOutput "🚀 Starting CyberGuardX in PRODUCTION mode..." $InfoColor
    Write-ColorOutput "   - 8 Uvicorn workers" $SuccessColor
    Write-ColorOutput "   - Resource limits enforced" $SuccessColor
    Write-ColorOutput "   - Running in background`n" $SuccessColor
    
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    Write-ColorOutput "`n✅ Services started successfully!" $SuccessColor
    Write-ColorOutput "`nAccess your application:" $InfoColor
    Write-ColorOutput "   Frontend: http://localhost:3000" $SuccessColor
    Write-ColorOutput "   Backend:  http://localhost:8000" $SuccessColor
    Write-ColorOutput "   API Docs: http://localhost:8000/docs" $SuccessColor
    Write-ColorOutput "`nView logs: .\start-docker.ps1 logs" $InfoColor
}

function Stop-Services {
    Write-ColorOutput "🛑 Stopping CyberGuardX services..." $WarningColor
    docker-compose down
    Write-ColorOutput "✅ Services stopped successfully!" $SuccessColor
}

function Rebuild-Services {
    Write-ColorOutput "🔨 Rebuilding CyberGuardX containers..." $InfoColor
    docker-compose build --no-cache
    Write-ColorOutput "✅ Rebuild complete!" $SuccessColor
    Write-ColorOutput "`nStart services with:" $InfoColor
    Write-ColorOutput "   .\start-docker.ps1 dev   (development)" $SuccessColor
    Write-ColorOutput "   .\start-docker.ps1 prod  (production)" $SuccessColor
}

function Show-Logs {
    Write-ColorOutput "📋 Showing container logs (Ctrl+C to exit)..." $InfoColor
    docker-compose logs -f
}

function Show-Status {
    Write-ColorOutput "📊 Container Status:`n" $InfoColor
    docker-compose ps
    
    Write-ColorOutput "`n💾 Volume Usage:" $InfoColor
    docker volume ls | Select-String "cyberguardx"
    
    Write-ColorOutput "`n📈 Resource Usage:" $InfoColor
    docker stats --no-stream cyberguardx-backend cyberguardx-frontend 2>$null
}

function Clean-Environment {
    Write-ColorOutput "🧹 Cleaning up Docker environment..." $WarningColor
    Write-ColorOutput "   This will remove containers, volumes, and images." $ErrorColor
    $confirm = Read-Host "Are you sure? (type 'yes' to confirm)"
    
    if ($confirm -eq 'yes') {
        docker-compose down -v
        docker system prune -f
        Write-ColorOutput "✅ Cleanup complete!" $SuccessColor
    } else {
        Write-ColorOutput "❌ Cleanup cancelled" $InfoColor
    }
}

function Show-Help {
    Write-ColorOutput "Usage: .\start-docker.ps1 [COMMAND]`n" $InfoColor
    Write-ColorOutput "Commands:" $InfoColor
    Write-ColorOutput "  dev      Start in development mode (default)" $SuccessColor
    Write-ColorOutput "  prod     Start in production mode" $SuccessColor
    Write-ColorOutput "  stop     Stop all services" $WarningColor
    Write-ColorOutput "  rebuild  Rebuild containers from scratch" $InfoColor
    Write-ColorOutput "  logs     View container logs" $InfoColor
    Write-ColorOutput "  status   Show container and resource status" $InfoColor
    Write-ColorOutput "  clean    Remove all containers and volumes" $ErrorColor
    Write-ColorOutput "`nExamples:" $InfoColor
    Write-ColorOutput "  .\start-docker.ps1              # Start development" $SuccessColor
    Write-ColorOutput "  .\start-docker.ps1 prod         # Start production" $SuccessColor
    Write-ColorOutput "  .\start-docker.ps1 status       # Check status" $SuccessColor
}

# ═════════════════════════════════════════════════════════════════════
# Main Script
# ═════════════════════════════════════════════════════════════════════

Show-Banner

# Check prerequisites
if (-not (Test-DockerInstalled)) {
    exit 1
}

if (-not (Test-DockerRunning)) {
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-ColorOutput "⚠️  Warning: .env file not found" $WarningColor
    Write-ColorOutput "   Creating from template..." $InfoColor
    Copy-Item ".env.example" ".env"
    Write-ColorOutput "✅ Created .env file. Please review and update if needed.`n" $SuccessColor
}

# Execute command
switch ($Command) {
    'dev'     { Start-Development }
    'prod'    { Start-Production }
    'stop'    { Stop-Services }
    'rebuild' { Rebuild-Services }
    'logs'    { Show-Logs }
    'status'  { Show-Status }
    'clean'   { Clean-Environment }
    default   { Show-Help }
}
