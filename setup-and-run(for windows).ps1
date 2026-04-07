# setup-and-run.ps1
# Run in Administrator PowerShell:
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\setup-and-run.ps1

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host "`n==== $msg ====`n" -ForegroundColor Cyan
}

function Command-Exists($cmd) {
    return $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

Write-Step "Checking for winget"
if (-not (Command-Exists "winget")) {
    throw "winget not found. Please install App Installer from Microsoft Store, or install Node.js and MongoDB manually."
}

Write-Step "Installing Node.js LTS (includes npm)"
if (-not (Command-Exists "node")) {
    winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
} else {
    Write-Host "Node.js already installed: $(node -v)"
}

# Refresh PATH for this session as much as possible
$env:Path += ";C:\Program Files\nodejs\"

Write-Step "Checking npm"
if (-not (Command-Exists "npm")) {
    throw "npm still not found after Node.js installation. Close PowerShell and rerun this script."
} else {
    Write-Host "npm version: $(npm -v)"
}

Write-Step "Installing MongoDB Community Server"
# Package id can vary by source; this one is common on winget.
# If it fails in your environment, install MongoDB manually from the official MSI.
try {
    winget install MongoDB.Server --accept-source-agreements --accept-package-agreements
} catch {
    Write-Warning "winget install MongoDB.Server failed. You may need to install MongoDB Community Server manually from the official installer."
}

Write-Step "Starting MongoDB service if available"
try {
    $service = Get-Service -Name "MongoDB" -ErrorAction Stop
    if ($service.Status -ne "Running") {
        Start-Service -Name "MongoDB"
        Write-Host "MongoDB service started."
    } else {
        Write-Host "MongoDB service already running."
    }
} catch {
    Write-Warning "MongoDB Windows service was not found. If MongoDB was installed without a service, start mongod manually."
}

Write-Step "Creating .env from .env.example if needed"
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host ".env created from .env.example"
    } else {
        Write-Warning ".env.example not found. Create .env manually."
    }
} else {
    Write-Host ".env already exists."
}

Write-Step "Installing project dependencies"
npm install

Write-Step "Running database seed"
try {
    npm run seed
} catch {
    Write-Warning "Seed failed. Check your MONGODB_URI in .env and confirm MongoDB is running."
    throw
}

Write-Step "Starting development server"
npm run dev