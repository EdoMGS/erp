# Runs basic security scans inside Docker
param(
    [string]$ComposeFile = "docker-compose.dev.yml"
)

Write-Host "Installing scan tools (container)..." -ForegroundColor Cyan
docker compose -f $ComposeFile run --rm web python -m pip install -q pip-audit bandit
if ($LASTEXITCODE -ne 0) { throw "pip install of scan tools failed" }

Write-Host "Bandit (security lint)..." -ForegroundColor Cyan
docker compose -f $ComposeFile run --rm web bandit -q -r .
if ($LASTEXITCODE -ne 0) { throw "Bandit findings present" }

Write-Host "pip-audit (vulns)..." -ForegroundColor Cyan
docker compose -f $ComposeFile run --rm web pip-audit -q
if ($LASTEXITCODE -ne 0) { throw "pip-audit found vulnerabilities" }

Write-Host "Scans passed." -ForegroundColor Green
