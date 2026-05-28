# Native Windows PowerShell Deployment Script for Social Media Factory
# Allows direct deployment to GCP from Windows without needing WSL or Linux bash.

$ErrorActionPreference = "Stop"

$REGION = "asia-south1"
$SERVICE_NAME = "social-media-factory"
$SA_NAME = "reels-factory-runner"
$REPOSITORY_NAME = "reels-factory"
$SCHEDULER_JOB_NAME = "instagram-reels-trigger"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting Social Media Factory GCP Windows Deployment    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Load Local .env Configuration
if (Test-Path .env) {
    Write-Host "Loading environment configurations from .env..." -ForegroundColor Green
    Get-Content .env | ForEach-Object {
        $line = $_.Trim()
        # Parse non-empty, non-comment lines
        if ($line -and -not $line.StartsWith("#")) {
            $parts = $line.Split('=', 2)
            if ($parts.Length -eq 2) {
                $key = $parts[0].Trim()
                $value = $parts[1].Trim()
                # Set in Process scope
                [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::Process)
            }
        }
    }
} else {
    Write-Error "Local '.env' file not found. Please create it using '.env.example' first."
    exit 1
}

$PROJECT_ID = [System.Environment]::GetEnvironmentVariable("GCP_PROJECT_ID", [System.EnvironmentVariableTarget]::Process)
$BUCKET_NAME = [System.Environment]::GetEnvironmentVariable("GCP_GCS_BUCKET_NAME", [System.EnvironmentVariableTarget]::Process)

if (-not $PROJECT_ID -or -not $BUCKET_NAME) {
    Write-Error "GCP_PROJECT_ID and GCP_GCS_BUCKET_NAME must be set in your .env file."
    exit 1
}

# Fetch other secrets to deploy
$GEMINI_API_KEY = [System.Environment]::GetEnvironmentVariable("GEMINI_API_KEY", [System.EnvironmentVariableTarget]::Process)
$PEXELS_API_KEY = [System.Environment]::GetEnvironmentVariable("PEXELS_API_KEY", [System.EnvironmentVariableTarget]::Process)
$INSTAGRAM_BUSINESS_ACCOUNT_ID = [System.Environment]::GetEnvironmentVariable("INSTAGRAM_BUSINESS_ACCOUNT_ID", [System.EnvironmentVariableTarget]::Process)
$META_USER_ACCESS_TOKEN = [System.Environment]::GetEnvironmentVariable("META_USER_ACCESS_TOKEN", [System.EnvironmentVariableTarget]::Process)

# 2. Verify Google Cloud SDK Installation
try {
    $null = Get-Command gcloud
} catch {
    Write-Error "gcloud command not found. Please make sure Google Cloud SDK is installed and added to your PATH environment variable."
    exit 1
}

# 3. Configure GCloud Project Context
Write-Host "Configuring Google Cloud project context to: $PROJECT_ID..." -ForegroundColor Yellow
gcloud config set project "$PROJECT_ID"

# 4. Enable Required Service APIs
Write-Host "Enabling Google Cloud Service APIs..." -ForegroundColor Yellow
gcloud services enable `
  run.googleapis.com `
  artifactregistry.googleapis.com `
  cloudbuild.googleapis.com `
  cloudscheduler.googleapis.com `
  iam.googleapis.com `
  storage.googleapis.com

# 5. Create Artifact Registry Repository (if not existing)
Write-Host "Checking Artifact Registry Repository..." -ForegroundColor Yellow
$repos = gcloud artifacts repositories list --location="$REGION" --format="value(name)"
if ($repos -notcontains $REPOSITORY_NAME) {
    Write-Host "Creating Artifact Registry repository '$REPOSITORY_NAME' in '$REGION'..." -ForegroundColor Green
    gcloud artifacts repositories create "$REPOSITORY_NAME" `
      --repository-format=docker `
      --location="$REGION" `
      --description="Registry for autonomous social media generation factory images"
} else {
    Write-Host "Artifact Registry repository already exists." -ForegroundColor Green
}

# 6. Build and Push Container using Google Cloud Build
$IMAGE_TAG = "$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:latest"
Write-Host "Submitting code build to Google Cloud Build. This will package your container..." -ForegroundColor Yellow
gcloud builds submit --tag "$IMAGE_TAG" .

# 7. Create GCS Storage Bucket (if not existing)
Write-Host "Checking Google Cloud Storage Bucket 'gs://$BUCKET_NAME'..." -ForegroundColor Yellow
$bucketExists = $false
try {
    $null = gsutil ls -b "gs://$BUCKET_NAME"
    $bucketExists = $true
} catch {
    # gsutil errors out if bucket doesn't exist
}

if (-not $bucketExists) {
    Write-Host "Creating GCS storage bucket in $REGION..." -ForegroundColor Green
    gsutil mb -c standard -l "$REGION" "gs://$BUCKET_NAME"
} else {
    Write-Host "GCS Bucket already exists." -ForegroundColor Green
}

# 8. Create Service Account for Runner
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
Write-Host "Checking service account '$SA_EMAIL'..." -ForegroundColor Yellow
$saExists = $false
try {
    $null = gcloud iam service-accounts describe "$SA_EMAIL"
    $saExists = $true
} catch {}

if (-not $saExists) {
    Write-Host "Creating Service Account..." -ForegroundColor Green
    gcloud iam service-accounts create "$SA_NAME" `
      --description="Service account for executing video production and social posting pipeline" `
      --display-name="Social Media Factory Runner"
} else {
    Write-Host "Service Account already exists." -ForegroundColor Green
}

# Bind GCS Object Admin role
Write-Host "Binding GCS storage object admin permissions..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding "$PROJECT_ID" `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/storage.objectAdmin" `
  --quiet

# Bind Token Creator role for signed URLs
Write-Host "Binding IAM Service Account Token Creator role for GCS Signed URL creation..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding "$PROJECT_ID" `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/iam.serviceAccountTokenCreator" `
  --quiet

# 9. Deploy to Google Cloud Run
Write-Host "Deploying serverless engine to Google Cloud Run..." -ForegroundColor Yellow
gcloud run deploy "$SERVICE_NAME" `
  --image "$IMAGE_TAG" `
  --region "$REGION" `
  --platform managed `
  --no-allow-unauthenticated `
  --service-account "$SA_EMAIL" `
  --timeout 600 `
  --memory 2Gi `
  --cpu 1 `
  --max-instances 1 `
  --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY",PEXELS_API_KEY="$PEXELS_API_KEY",GCP_GCS_BUCKET_NAME="$BUCKET_NAME",INSTAGRAM_BUSINESS_ACCOUNT_ID="$INSTAGRAM_BUSINESS_ACCOUNT_ID",META_USER_ACCESS_TOKEN="$META_USER_ACCESS_TOKEN"

# Extract Cloud Run Service URL
$SERVICE_URL = gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)'
Write-Host "Service deployed successfully! Trigger Endpoint: $SERVICE_URL" -ForegroundColor Green

# 10. Setup Cloud Scheduler Trigger
Write-Host "Configuring Google Cloud Scheduler cron triggers..." -ForegroundColor Yellow

# Delete existing job to prevent conflict
try {
    $null = gcloud scheduler jobs describe "$SCHEDULER_JOB_NAME" --location="$REGION"
    Write-Host "Removing existing Scheduler job to refresh schedule config..." -ForegroundColor Green
    gcloud scheduler jobs delete "$SCHEDULER_JOB_NAME" --location="$REGION" --quiet
} catch {}

# Create Cloud Scheduler job triggered 3 times a day (9:00 AM, 2:00 PM, and 7:00 PM IST)
gcloud scheduler jobs create http "$SCHEDULER_JOB_NAME" `
  --location="$REGION" `
  --schedule="0 9,14,19 * * *" `
  --time-zone="Asia/Kolkata" `
  --uri="$SERVICE_URL/run" `
  --http-method=POST `
  --oidc-service-account-email="$SA_EMAIL" `
  --oidc-token-audience="$SERVICE_URL" `
  --headers="Content-Type=application/json" `
  --description="Triggers the serverless social media generation factory 3 times a day."

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " WINDOWS POWER-SHELL DEPLOYMENT COMPLETED SUCCESSFULLY!  " -ForegroundColor Green
Write-Host "                                                          " -ForegroundColor Green
Write-Host " Cloud Run Service:  $SERVICE_URL                         " -ForegroundColor Green
Write-Host " Scheduler Cron:     0 9,14,19 * * * (Asia/Kolkata)       " -ForegroundColor Green
Write-Host " GCS Storage Bucket: gs://$BUCKET_NAME                   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
