param(
  [string]$HeartProcessedUrl = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
  [string]$DiabetesUrl = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $root "backend\app\ml\data"
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

Write-Host "Downloading heart dataset (UCI processed.cleveland.data)..." -ForegroundColor Cyan
$tmpHeart = Join-Path $dataDir "heart_raw.data"
Invoke-WebRequest -Uri $HeartProcessedUrl -OutFile $tmpHeart

# Convert to heart.csv with header and binary target.
# Raw format: 14 columns, last is num (0-4). Missing values can be '?'.
$heartOut = Join-Path $dataDir "heart.csv"
$header = "age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,target"
$header | Set-Content -Encoding UTF8 $heartOut

Get-Content $tmpHeart | ForEach-Object {
  $line = $_.Trim()
  if (!$line) { return }
  $parts = $line.Split(',')
  if ($parts.Length -ne 14) { return }

  # Skip rows with missing values
  if ($parts -contains "?") { return }

  $num = [int]$parts[13]
  $parts[13] = $(if ($num -gt 0) { "1" } else { "0" })
  ($parts -join ',') | Add-Content -Encoding UTF8 $heartOut
}

Remove-Item $tmpHeart -Force

Write-Host "Downloading diabetes dataset (Pima Indians)..." -ForegroundColor Cyan
$tmp = Join-Path $dataDir "diabetes_raw.csv"
Invoke-WebRequest -Uri $DiabetesUrl -OutFile $tmp

$diabOut = Join-Path $dataDir "diabetes.csv"
$header2 = "Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age,Outcome"
$header2 | Set-Content -Encoding UTF8 $diabOut
Get-Content $tmp | Add-Content -Encoding UTF8 $diabOut
Remove-Item $tmp -Force

Write-Host "Done. Datasets saved to $dataDir" -ForegroundColor Green
