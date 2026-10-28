# Install ScholarForge into any Agent Skills host (Windows PowerShell).
# Produces a LEAN skill folder: runtime files only, no build tools or archives.
param(
  [string]$Target = "$HOME\.claude\skills\scholar-forge"
)
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path
$Parent = Split-Path -Parent $Target
New-Item -ItemType Directory -Force -Path $Parent | Out-Null
if (Test-Path $Target) { Write-Host "[warn] $Target already exists; merging" }
New-Item -ItemType Directory -Force -Path $Target | Out-Null

foreach ($item in @("SKILL.md", "LICENSE", "NOTICE.md")) {
  Copy-Item -Path (Join-Path $Src $item) -Destination (Join-Path $Target $item) -Force
}
foreach ($dir in @("references", "scripts", "templates", "config", "data", "tests", "evals")) {
  $srcDir = Join-Path $Src $dir
  $dstDir = Join-Path $Target $dir
  New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
  Get-ChildItem -Path $srcDir -Recurse -File |
    Where-Object { $_.FullName -notmatch '__pycache__' -and $_.Extension -ne '.pyc' } |
    ForEach-Object {
      $rel = $_.FullName.Substring($srcDir.Length + 1)
      $dst = Join-Path $dstDir $rel
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
      Copy-Item -Path $_.FullName -Destination $dst -Force
    }
}
Write-Host "[ok] copied lean skill to $Target"
Write-Host "The target directory name must be 'scholar-forge' (Agent Skills spec)."
& python "$Target\scripts\scholarforge.py" doctor
& python "$Target\scripts\scholarforge.py" validate
Write-Host "Skill ready: $Target\SKILL.md"
