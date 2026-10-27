# Install ScholarForge into any Agent Skills host (Windows PowerShell).
param(
  [string]$Target = "$HOME\.claude\skills\scholar-forge"
)
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
if (Test-Path $Target) { Write-Host "[warn] $Target already exists; replacing" }
Copy-Item -Path $Src -Destination $Target -Recurse -Force -Exclude @(".git", "__pycache__")
Write-Host "[ok] copied ScholarForge to $Target"
& python "$Target\scripts\scholarforge.py" doctor
Write-Host "Skill ready: $Target\SKILL.md"
