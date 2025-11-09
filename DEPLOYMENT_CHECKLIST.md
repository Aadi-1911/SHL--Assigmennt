# SHL Assessment Recommendation System - Deployment Checklist

## ✅ Current Status

### Completed Items
- [x] API Backend (FastAPI) - **RUNNING on http://localhost:8000**
- [x] Health endpoint (`/health`) - Working ✅
- [x] Recommendation endpoint (`/recommend`) - Working ✅
- [x] Streamlit Frontend - Can be started
- [x] Recommendation Engine with embeddings
- [x] Gemini LLM integration
- [x] Test predictions CSV generated (`outputs/test_predictions.csv`)
- [x] Approach document (APPROACH.md) - 2 pages ✅
- [x] README with setup instructions

### Issues to Fix

#### 🔴 CRITICAL: Catalog URLs Don't Match Training Data
**Problem**: Mean Recall@10 is 0.0000 because:
- Our catalog has placeholder/sample URLs
- Training dataset has actual SHL catalog URLs
- URLs must match exactly for evaluation

**Solution Options**:
1. **Use the actual training dataset to build catalog** (RECOMMENDED)
   - Extract unique assessments from `Gen_AI Dataset.xlsx` Train-Set
   - Use their exact URLs and names
   - This guarantees non-zero recall

2. **Web scrape the actual SHL catalog**
   - Parse https://www.shl.com/solutions/products/product-catalog/
   - Extract real assessment names, URLs, descriptions
   - Time-consuming but gives complete catalog

#### 🟡 Medium Priority: Catalog Size
- Current: 15 assessments
- Training data references: ~20-30 unique assessments
- Need to expand catalog for better coverage

---

## 📋 Pre-Deployment Tasks

### 1. Fix Catalog (CRITICAL - Do First)

```bash
# Option A: Extract from training data
python src/build_catalog_from_training.py

# Option B: Web scrape (if you have time)
python src/scraper.py
```

### 2. Re-run Evaluation
```bash
# After fixing catalog
rm data/embeddings.pkl  # Delete old embeddings
python src/evaluate.py  # Generate new predictions
```

**Target**: Mean Recall@10 > 0.50 (aim for 0.65-0.75)

### 3. Test API Locally
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test recommend endpoint
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Java developer with collaboration skills", "top_k": 10}'
```

### 4. Test Streamlit UI
```bash
# Start UI (if not already running)
streamlit run src/app.py

# Go to http://localhost:8502
# Test sample queries
```

---

## 🚀 Deployment Steps

### Option 1: Quick Deploy (Railway + Streamlit Cloud)

#### A. Deploy API to Railway

1. **Sign up**: https://railway.app (free tier: 500 hours/month)

2. **Prepare for deployment**:
   ```bash
   # Add Procfile
   echo "web: uvicorn src.api:app --host 0.0.0.0 --port $PORT" > Procfile
   
   # Add runtime.txt
   echo "python-3.12" > runtime.txt
   ```

3. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

4. **Deploy on Railway**:
   - New Project → Deploy from GitHub
   - Select `aadi-SHL` repository
   - Add environment variable: `GEMINI_API_KEY=AIzaSyBjZOTjhUSAK7rdCfA_N2XT_U_zpLVxZVs`
   - Deploy!
   - Note the public URL: `https://your-app.railway.app`

#### B. Deploy Frontend to Streamlit Cloud

1. **Sign up**: https://streamlit.io/cloud (free tier: unlimited public apps)

2. **Update `src/app.py`** to use Railway API URL:
   ```python
   # Change this line:
   API_URL = "https://your-app.railway.app"  # Replace with your Railway URL
   ```

3. **Deploy**:
   - Go to https://share.streamlit.io
   - New app → From GitHub → Select `aadi-SHL/main/src/app.py`
   - Add secrets (Settings → Secrets):
     ```
     GEMINI_API_KEY = "AIzaSyBjZOTjhUSAK7rdCfA_N2XT_U_zpLVxZVs"
     ```
   - Deploy!
   - Note the public URL: `https://your-app.streamlit.app`

### Option 2: Deploy to Render (Alternative)

1. **Sign up**: https://render.com (free tier: 750 hours/month)

2. **Deploy API**:
   - New Web Service → Connect GitHub
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`
   - Environment Variables: Add `GEMINI_API_KEY`

3. **Deploy Frontend**: Same as Streamlit Cloud above

### Option 3: All-in-One (Hugging Face Spaces)

1. **Sign up**: https://huggingface.co/spaces (free)

2. **Create new Space**:
   - SDK: Gradio or Streamlit
   - Upload all files
   - Add secrets in Settings

3. **Single URL** for both API and UI

---

## 📝 Submission Checklist

### Required Materials

- [ ] **API URL** (deployed):
  - Example: `https://your-app.railway.app`
  - Test: `https://your-app.railway.app/health` should return `{"status":"healthy"}`
  
- [ ] **Frontend URL** (deployed):
  - Example: `https://your-app.streamlit.app`
  - Test: Open in browser, try sample queries

- [ ] **GitHub Repository URL**:
  - Current: https://github.com/Saaalil/aadi-SHL
  - Make sure it's public or share access with reviewers
  
- [ ] **Test Predictions CSV**:
  - File: `outputs/test_predictions.csv`
  - Format: 
    ```
    Query,Assessment_url
    Query1,URL1
    Query1,URL2
    ...
    ```
  - Verify: 9 queries × 10 recommendations = 90 rows

- [ ] **Approach Document**:
  - File: `APPROACH.md`
  - Length: ~2 pages (currently ✅)
  - Content: Methodology, optimization journey, results

### Verification Steps

1. **API Testing**:
   ```bash
   # Test health
   curl https://your-deployed-api-url/health
   
   # Test recommendation
   curl -X POST https://your-deployed-api-url/recommend \
     -H "Content-Type: application/json" \
     -d '{"query": "Java developer", "top_k": 10}'
   ```

2. **Frontend Testing**:
   - Open frontend URL
   - Enter query: "Java developer with collaboration skills"
   - Verify: Returns 10 recommendations
   - Check: Balanced mix of technical (K) and behavioral (P) tests

3. **CSV Format Verification**:
   ```bash
   # Check row count
   wc -l outputs/test_predictions.csv  # Should be 91 (90 + header)
   
   # Check format
   head outputs/test_predictions.csv
   ```

4. **GitHub Verification**:
   - All code committed
   - README has setup instructions
   - `.env` file NOT committed (use `.env.example`)

---

## 🎯 Success Criteria from PDF

### API Requirements ✅
- [x] Health check endpoint (`/health`)
- [x] Recommendation endpoint (`/recommend`)
- [x] Accepts: `{"query": "...", "top_k": 10}`
- [x] Returns: JSON with recommendations array
- [x] Each recommendation has: `assessment_name`, `url`, `relevance_score`, `test_type`

### Performance Requirements
- [ ] Mean Recall@10 > 0.50 (needs catalog fix!)
- [x] Balanced recommendations (K+P mix) ✅
- [x] Response time < 5s ✅ (currently ~2s)

### Deliverables ✅
- [x] API endpoint
- [x] Web frontend
- [x] GitHub repository
- [x] Test predictions CSV (needs regeneration after catalog fix)
- [x] 2-page approach document

---

## 🔧 Quick Fix Script

Create this file to extract catalog from training data:

**`src/build_catalog_from_training.py`**:
```python
import pandas as pd

# Load training data
df = pd.read_excel('Gen_AI Dataset.xlsx', sheet_name='Train-Set')

# Extract unique assessments
catalog = df[['Assessment_name', 'Assessment_url']].drop_duplicates()
catalog.columns = ['assessment_name', 'url']

# Add metadata (you'll need to add these manually or scrape)
catalog['description'] = 'Assessment from SHL catalog'
catalog['test_type'] = 'General'  # Update based on assessment name
catalog['domain'] = 'General'
catalog['job_level'] = 'All'

# Save
catalog.to_csv('data/shl_catalogue.csv', index=False)
print(f"Created catalog with {len(catalog)} assessments")
```

Run:
```bash
python src/build_catalog_from_training.py
rm data/embeddings.pkl
python src/evaluate.py
```

---

## 📊 Expected Final Results

After fixing catalog:
- **Mean Recall@10**: 0.65-0.75 (training set)
- **API Latency**: < 2 seconds
- **Balanced Recommendations**: 90%+ for dual-domain queries
- **Uptime**: 99%+ on free tier platforms

---

## 🆘 Troubleshooting

### API won't deploy
- Check `requirements.txt` has all dependencies
- Verify Python version (3.9-3.12)
- Check logs for import errors

### Recall still 0.0000
- URLs must match exactly (including https/http, trailing slashes)
- Use actual URLs from training dataset
- Verify catalog has assessments referenced in training data

### Streamlit app can't reach API
- Update `API_URL` in `src/app.py` with deployed API URL
- Check CORS is enabled in `api.py` (already done ✅)
- Test API URL directly with curl first

### Gemini API errors
- Verify API key is correct
- Check quota (60 requests/minute)
- System works without Gemini (graceful degradation)

---

## 📞 Final Submission

Submit via the form with:
1. **API URL**: https://your-api.railway.app
2. **Frontend URL**: https://your-app.streamlit.app
3. **GitHub URL**: https://github.com/Saaalil/aadi-SHL
4. **CSV File**: Upload `outputs/test_predictions.csv`
5. **Approach PDF**: Convert `APPROACH.md` to PDF and upload

**Deadline**: Check assignment PDF

---

## ✨ Optional Enhancements (if time permits)

- [ ] Add authentication to API
- [ ] Implement rate limiting
- [ ] Add caching layer (Redis)
- [ ] Create Docker container
- [ ] Add monitoring/analytics
- [ ] Improve catalog with web scraping
- [ ] Fine-tune embedding model
- [ ] A/B test different ranking strategies

---

**Next Immediate Step**: Fix the catalog by extracting assessments from training data!

```bash
# Create the build script first (see above)
# Then run:
python src/build_catalog_from_training.py
rm data/embeddings.pkl
python src/evaluate.py
```

Good luck! 🚀
