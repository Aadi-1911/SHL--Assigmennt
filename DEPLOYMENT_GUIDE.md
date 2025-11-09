# Deployment Guide - SHL Assessment Recommendation System

## ✅ Your Project Status

### What's Ready:
1. ✅ **API Backend**: Running locally, fully compliant with Appendix 2 requirements
2. ✅ **Test Predictions CSV**: Generated with 90 rows (9 queries × 10 recommendations)
3. ✅ **Catalog**: 54 assessments from training data
4. ✅ **Documentation**: APPROACH.md (2-page technical document)
5. ✅ **GitHub**: Code at https://github.com/Saaalil/aadi-SHL

### API Compliance Checklist ✅

Per Appendix 2 requirements:

- [x] **Health Check Endpoint** (`GET /health`)
  ```json
  {"status": "healthy", "message": "SHL Assessment Recommendation API is running", "version": "1.0.0"}
  ```

- [x] **Recommendation Endpoint** (`POST /recommend`)
  - Accepts: `{"query": "...", "top_k": 10}`
  - Returns: JSON with recommendations array
  - Each recommendation has:
    - `assessment_name` ✅
    - `url` ✅
    - `relevance_score` ✅
    - `test_type` ✅
    - `explanation` ✅ (LLM-generated)

- [x] **HTTP/HTTPS accessible** ✅
- [x] **Proper HTTP status codes** ✅
- [x] **JSON format** ✅
- [x] **CORS enabled** ✅

---

## 🚀 Deployment Steps

### Option 1: Streamlit Cloud (UI Only) + Railway (API)

This is the **recommended** approach:

#### Step 1: Deploy API to Railway

1. **Go to**: https://railway.app
2. **Sign in** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `Saaalil/aadi-SHL`
5. **Add Environment Variable**:
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyBjZOTjhUSAK7rdCfA_N2XT_U_zpLVxZVs`
6. Railway will auto-detect the `Procfile` and deploy
7. **Copy the public URL**: e.g., `https://aadi-shl-production.up.railway.app`

#### Step 2: Update Streamlit App with API URL

Edit `src/app.py` line 9:
```python
API_URL = "https://your-railway-url.railway.app"  # Replace with your Railway URL
```

Push to GitHub:
```bash
git add src/app.py
git commit -m "Update API URL for deployment"
git push origin main
```

#### Step 3: Deploy Frontend to Streamlit Cloud

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub
3. **New app**:
   - Repository: `Saaalil/aadi-SHL`
   - Branch: `main`
   - Main file path: `src/app.py`
4. **Advanced settings** → **Secrets**:
   ```toml
   GEMINI_API_KEY = "AIzaSyBjZOTjhUSAK7rdCfA_N2XT_U_zpLVxZVs"
   ```
5. **Deploy!**
6. **Copy the public URL**: e.g., `https://aadi-shl.streamlit.app`

---

### Option 2: Render (Alternative to Railway)

1. **Go to**: https://render.com
2. **Sign in** with GitHub
3. **New** → **Web Service**
4. **Connect** `Saaalil/aadi-SHL`
5. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add `GEMINI_API_KEY`
6. **Deploy** and copy the URL

---

## 📝 Final Submission Checklist

### What to Submit:

1. **API URL** (from Railway/Render):
   - Example: `https://aadi-shl-production.up.railway.app`
   - Test before submitting:
     ```bash
     curl https://your-api-url/health
     curl -X POST https://your-api-url/recommend \
       -H "Content-Type: application/json" \
       -d '{"query": "Java developer", "top_k": 10}'
     ```

2. **GitHub URL**:
   - ✅ https://github.com/Saaalil/aadi-SHL

3. **Frontend URL** (from Streamlit Cloud):
   - Example: `https://aadi-shl.streamlit.app`

4. **Test Predictions CSV**:
   - ✅ File: `outputs/test_predictions.csv`
   - ✅ Format: `Query,Assessment_url` (90 rows)
   - ✅ Upload this file to the submission form

5. **Approach Document**:
   - ✅ File: `APPROACH.md`
   - ✅ Length: 2 pages
   - Convert to PDF if needed:
     - Open APPROACH.md in VS Code
     - Right-click → "Open Preview"
     - Print → Save as PDF

---

## 🧪 Testing Before Submission

### Test API Locally (Already Working ✅)
```bash
curl http://localhost:8000/health
```

### Test API After Deployment
```bash
# Health check
curl https://your-railway-url.railway.app/health

# Recommendation test
curl -X POST https://your-railway-url.railway.app/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Java developer with collaboration skills", "top_k": 10}'
```

### Test Frontend
1. Open your Streamlit URL
2. Enter query: "Java developer with collaboration skills"
3. Verify: Returns 10 recommendations with balanced K+P test types

---

## 📊 Your Current Results

### Test Predictions CSV ✅
- **Location**: `outputs/test_predictions.csv`
- **Rows**: 90 (9 queries × 10 recommendations)
- **Format**: Correct ✅

### API Performance
- **Response Time**: ~2 seconds
- **Catalog Size**: 54 assessments
- **Test Types**: K (11), P (6), C (4), G (33)

---

## 🆘 Quick Troubleshooting

### Railway deployment fails
- Check `requirements.txt` includes all packages
- Verify `Procfile` is in root directory
- Check Railway logs for specific errors

### Streamlit can't connect to API
- Verify you updated `API_URL` in `src/app.py`
- Test Railway API URL directly with curl first
- Check Railway app is running (not sleeping)

### API returns 503 errors
- Engine initialization might have failed
- Check Railway logs for startup errors
- Verify `data/shl_catalogue.csv` is in the repository

---

## 📦 Files Included for Deployment

- ✅ `Procfile` - Railway/Render startup command
- ✅ `runtime.txt` - Python version specification
- ✅ `requirements.txt` - All dependencies
- ✅ `src/api.py` - FastAPI backend (Appendix 2 compliant)
- ✅ `src/app.py` - Streamlit frontend
- ✅ `data/shl_catalogue.csv` - Assessment catalog
- ✅ `outputs/test_predictions.csv` - Submission file
- ✅ `APPROACH.md` - Technical document

---

## ✨ Summary

**Your project is 100% ready for deployment!**

**Next steps (15-20 minutes)**:
1. Deploy API to Railway (5 min)
2. Update `src/app.py` with Railway URL (1 min)
3. Deploy frontend to Streamlit Cloud (5 min)
4. Test both URLs (5 min)
5. Submit all URLs + CSV + PDF (5 min)

**Good luck! 🚀**
