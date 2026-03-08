# Production Deployment -- Synthetic Student Generator

How to deploy and operate the application on Google Cloud Platform.

---

## GCP Resources

<!-- TODO: Fill in once infrastructure is provisioned -->

| Resource | Service | Details |
|----------|---------|---------|
| Backend API | Cloud Run | `synthetic-student-generator` in `us-central1` |
| Frontend | Firebase Hosting | Static SPA served via CDN |
| LLM | Vertex AI | Gemini 2.5 Flash (`gemini-2.5-flash`) |
| Container Registry | Artifact Registry | Docker images for Cloud Run |

### Required IAM Roles

<!-- TODO: Document service account and IAM configuration -->

- Cloud Run service account needs **Vertex AI User** role for Gemini access

---

## Docker Build

<!-- TODO: Add Docker build commands once Dockerfile is created -->

```bash
cd backend

# Build the container image
docker build -t ssg-backend .

# Test locally
docker run -p 8000:8000 \
  -e GCP_PROJECT_ID=your-project-id \
  -e GCP_REGION=us-central1 \
  ssg-backend

# Tag and push to Artifact Registry
# docker tag ssg-backend us-central1-docker.pkg.dev/<project>/ssg/backend:latest
# docker push us-central1-docker.pkg.dev/<project>/ssg/backend:latest
```

---

## Cloud Run Deployment

<!-- TODO: Add deployment commands once Cloud Run service is configured -->

```bash
# Deploy from source (simplest approach)
gcloud run deploy synthetic-student-generator \
  --source ./backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=your-project-id,GCP_REGION=us-central1"

# Verify deployment
curl https://synthetic-student-generator-<hash>-uc.a.run.app/api/v1/health
```

---

## Firebase Hosting Deployment

<!-- TODO: Add Firebase hosting setup and deploy commands -->

```bash
cd frontend

# Build the production frontend
VITE_API_URL=https://synthetic-student-generator-<hash>-uc.a.run.app npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

### Firebase Configuration

<!-- TODO: Document firebase.json and hosting config -->
<!-- The frontend/firebase.json should configure dist/ as the public directory with SPA rewrite rules -->

---

## Firebase Function Setup

<!-- TODO: Determine if a Firebase Function proxy is needed for this project -->
<!-- If the backend requires API key injection (like diagram-as-code-architect), document the function setup here -->
<!-- Otherwise, remove this section -->

---

## Verification

<!-- TODO: Add post-deployment verification checklist -->

1. **Backend health:** `curl https://<cloud-run-url>/api/v1/health` returns 200
2. **Templates endpoint:** `curl https://<cloud-run-url>/api/v1/templates` returns template list
3. **Generate endpoint:** POST to `/api/v1/generate` returns a student sample
4. **Frontend:** Firebase Hosting URL loads the React app
5. **End-to-end:** Submit a generation request through the frontend and verify the sample displays

---

## Troubleshooting

<!-- TODO: Add production troubleshooting steps -->

| Issue | Solution |
|-------|----------|
| Cloud Run returns 500 | Check Cloud Run logs: `gcloud run services logs read synthetic-student-generator` |
| CORS errors | Verify backend CORS config includes the Firebase Hosting domain |
| Gemini auth failure | Confirm service account has Vertex AI User role |
| Firebase deploy fails | Run `firebase use <project-id>` to set the active project |
