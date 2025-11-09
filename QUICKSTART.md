# 🚀 Quick Start Guide

## Get Up and Running in 5 Minutes

### Step 1: Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Key (Optional - 1 min)
Get free Gemini API key from: https://ai.google.dev/

Edit `.env` file:
```
GEMINI_API_KEY=your_actual_key_here
```

**Note**: System works without API key (will skip LLM explanations)

### Step 3: Start Everything (1 min)

**Windows:**
```bash
start_all.bat
```

**Linux/Mac:**
```bash
chmod +x start_all.sh
./start_all.sh
```

This launches:
- ✅ API at http://localhost:8000
- ✅ Web UI at http://localhost:8501

### Step 4: Test It! (2 min)

**Option A: Web UI** (Easiest)
1. Open http://localhost:8501
2. Enter query: "Java developer with collaboration skills"
3. Click "Get Recommendations"
4. See results!

**Option B: API** 
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Java developer with collaboration skills", "top_k": 5}'
```

**Option C: Python**
```python
import requests

response = requests.post(
    "http://localhost:8000/recommend",
    json={
        "query": "Java developer with collaboration skills",
        "top_k": 5
    }
)

print(response.json())
```

---

## Run Evaluation

```bash
python src/evaluate.py
```

This will:
- Calculate Mean Recall@10 on training set
- Generate test set predictions
- Save results to `outputs/`

---

## Project Structure

```
📁 aadi prject/
├── 📄 README.md              ← Full documentation
├── 📄 APPROACH.md            ← 2-page technical approach
├── 📄 requirements.txt       ← Dependencies
├── 📄 .env                   ← API keys (configure this!)
├── 📄 start_all.bat          ← Windows launcher
├── 📄 start_all.sh           ← Linux/Mac launcher
│
├── 📁 src/
│   ├── api.py               ← FastAPI backend
│   ├── app.py               ← Streamlit frontend
│   ├── recommendation_engine.py  ← Core logic
│   ├── scraper.py           ← Catalog scraper
│   └── evaluate.py          ← Evaluation script
│
├── 📁 data/
│   ├── shl_catalogue.csv    ← Assessment catalog
│   └── embeddings.pkl       ← Cached embeddings (auto-generated)
│
└── 📁 outputs/
    ├── training_evaluation.csv   ← Recall scores
    └── test_predictions.csv      ← Submission format
```

---

## Common Issues

**Problem**: `ModuleNotFoundError`
**Solution**: 
```bash
pip install -r requirements.txt
```

**Problem**: API won't start (port in use)
**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Problem**: No LLM explanations
**Solution**: Check `.env` has valid `GEMINI_API_KEY`. System still works without it!

**Problem**: Low similarity scores
**Solution**: The catalog is small (20 assessments). Add more in `src/scraper.py` → `create_sample_catalog()`

---

## Next Steps

1. **Customize Catalog**: Add more assessments in `src/scraper.py`
2. **Tune Balancing**: Adjust weights in `recommendation_engine.py`
3. **Deploy**: Follow deployment guides in `README.md`
4. **Evaluate**: Run `src/evaluate.py` and review metrics

---

## Sample Queries to Try

Copy-paste these into the UI:

1. "I am hiring for Java developers who can also collaborate effectively with my business teams."
2. "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript."
3. "Entry-level sales role requiring strong communication skills"
4. "Senior data analyst with 5 years of experience in business intelligence"
5. "Leadership position requiring strategic thinking and team management"

---

## API Endpoints

**Health Check:**
```bash
GET http://localhost:8000/health
```

**Get Recommendations:**
```bash
POST http://localhost:8000/recommend
Body: {"query": "your query here", "top_k": 10}
```

**Interactive Docs:**
```
http://localhost:8000/docs
```

---

## Need Help?

1. Check `README.md` for full documentation
2. Review `APPROACH.md` for technical details
3. Check console logs for error messages
4. Ensure all dependencies are installed

---

**You're all set! 🎉**

Start with the Web UI at http://localhost:8501 for the easiest experience.
