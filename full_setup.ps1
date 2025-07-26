<#
  init_apps.ps1  – automatski:
    • pronađe sve direktorije koji imaju apps.py
    • ubaci ih u INSTALLED_APPS (erp_system/settings/base.py)
    • docker compose exec web:
        - makemigrations
        - migrate
        - collectstatic
    • restart web + worker

  Pokretanje:
      .\init_apps.ps1
#>

function Abort($txt) { Write-Error $txt; exit 1 }

# ------------------------------------------------------------
# A) Popis lokalnih app-ova (folder s apps.py)
# ------------------------------------------------------------
$appDirs = Get-ChildItem -Directory | Where-Object {
    Test-Path "$($_.FullName)\apps.py"
} | Select-Object -ExpandProperty Name

if (-not $appDirs) { Abort "Nisam pronašao niti jedan direktorij s apps.py" }

Write-Host "Pronađene aplikacije:" ($appDirs -join ", ")

# ------------------------------------------------------------
# B) Upis u INSTALLED_APPS
# ------------------------------------------------------------
$settings = ".\erp_system\settings\base.py"
if (-not (Test-Path $settings)) { Abort "Ne mogu naći $settings" }

$txt = Get-Content $settings -Raw
# lociraj kraj INSTALLED_APPS []
$pattern = '(?ms)(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'
$appsBlock = ($txt -replace $pattern, '$2')

# postojeće app-ove u settingsu:
$already = ($appsBlock -split ',' | % { $_.Trim(" '""") }) -ne ''

# dodaj nove koji nisu već upisani
$new = $appDirs | Where-Object { $already -notcontains $_ }
if ($new) {
    $inserts = $new | % { "    '$_'," } | Out-String
    $txt = [regex]::Replace($txt, $pattern, "`$1`$2$inserts`$3")
    $txt | Set-Content $settings
    Write-Host "Dodano u INSTALLED_APPS: $($new -join ', ')"
} else {
    Write-Host "Svi app-ovi su već u INSTALLED_APPS."
}

# ------------------------------------------------------------
# C) Docker: makemigrations + migrate + collectstatic
# ------------------------------------------------------------
Write-Host "Pokrećem makemigrations ..."
docker compose exec web python manage.py makemigrations --noinput
Write-Host "Pokrećem migrate ..."
docker compose exec web python manage.py migrate --noinput
Write-Host "Pokrećem collectstatic ..."
docker compose exec web python manage.py collectstatic --noinput

# ------------------------------------------------------------
# D) Restart servisa
# ------------------------------------------------------------
docker compose restart web worker
Write-Host "`n✔︎ Gotovo – app-ovi aktivirani i baze ažurirane."
