# speakease-api
speakease backend

## Dev
---
poetry run uvicorn app.main:app --reload

$env:TEST_ENV="dev"; pytest tests/test_main.py -v -s


## Docker Locally
---
poetry export -f requirements.txt --without-hashes -o requirements.txt

### Build and run
docker-compose up --build


## Docker GCP
---


Build and deploy using Cloud Build:

1. authenticate with Google Cloud:
gcloud auth login
gcloud auth application-default login

2. Configure Docker to use Google Cloud credentials:
gcloud auth configure-docker us-docker.pkg.dev


gcloud projects get-iam-policy gcpxmlb25

3) build and push image

Change to Artifact Registry
docker build -t us-docker.pkg.dev/gcpxmlb25/speakease/speakease-api .
docker push us-docker.pkg.dev/gcpxmlb25/speakease/speakease-api

gcloud projects add-iam-policy-binding gcpxmlb25 --member="user:gubo2012v@gmail.com" --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding gcpxmlb25 --member="user:gubo2012v@gmail.com" --role="roles/storage.objectCreator"


gcloud artifacts repositories add-iam-policy-binding speakease `
    --location=us `
    --member="user:gubo2012v@gmail.com" `
    --role="roles/artifactregistry.writer"



4) gcloud builds submit --config=cloudbuild-deploy.yaml


Use this one to run 
gcloud run services describe speakease-api --region us-central1 --project=gcpxmlb25

$env:TEST_ENV="gcp"; pytest tests/test_main.py -v -s