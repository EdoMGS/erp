# Runs full test suite inside Docker using docker-compose.dev.yml
param(
    [string]$ComposeFile = "docker-compose.dev.yml"
)

Write-Host "Building image..." -ForegroundColor Cyan
docker compose -f $ComposeFile build web
if ($LASTEXITCODE -ne 0) { throw "Build failed" }

Write-Host "Running pytest..." -ForegroundColor Cyan
docker compose -f $ComposeFile run --rm web python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }

Write-Host "flake8 lint..." -ForegroundColor Cyan
docker compose -f $ComposeFile run --rm web flake8 . -q
if ($LASTEXITCODE -ne 0) { throw "Lint failed" }

Write-Host "All tests passed." -ForegroundColor Green
