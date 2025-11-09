

**Project To-Do**

- [ ] **Catalogue & Crawling**: Scrape SHL “Individual Test Solutions” pages (skip “Pre-packaged Job Solutions”), capture name, URL, domain, job level, description; normalize into `data/shl_catalog.csv`.
- [ ] **Augment Training Data**: Load `Gn_AI Dataseet.xlsx` Train-Set (10 unique queries, 65 rows) and Test-Set (9 queries); clean duplicates, map assessments to scraped catalogue, flag any URLs missing in crawl.
- [ ] **Feature Engineering**: Create combined text representation per assessment (name + description + domain + level); experiment with additional tags (duration, competencies) if available; persist processed artefacts.
- [ ] **Embedding Pipeline**: Select embedding model (e.g., `sentence-transformers`), generate/store catalogue vectors, add query encoder utility, and plan for periodic refresh.
- [ ] **Retrieval Logic**: Implement similarity search with filters for level/domain; tune top-k (aim 5–10 results per spec); add safeguards against empty results.
- [ ] **LLM Reasoning Layer**: Design prompt template that cites matched assessments, requests per-item justification, and nominates a best pick; prototype with chosen LLM, enforce JSON-ish response for API.
- [ ] **Evaluation Loop**: Compute Recall@10 on labeled set; iterate on prompts/filters to improve; document baseline vs. tuned scores and tracing insights for the 2-page report.
- [ ] **Inference Outputs**: Produce required CSV (`query`, `predictions`) for provided Test-Set; validate format from Appendix 3 once available.
- [ ] **Service Layer**: Build FastAPI endpoint `/recommend` to accept query/JD payload (text or URL), run retrieval + LLM, return JSON with 5–10 items (name, URL, score, rationale, best pick).
- [ ] **Frontend**: Stand up Streamlit UI that accepts text/URL, calls API, displays ranked cards with explanations, highlights the top recommendation.
- [ ] **MLOps Utilities**: Add logging and optional tracing for each recommendation call; capture latency and prompt versions.
- [ ] **Packaging**: Create `requirements.txt`, optional Dockerfile, and repo structure aligned with modules (data, retrieval, genai, api, ui).
- [ ] **Documentation**: Draft README with setup/run steps, sample curl request, UI walkthrough; prepare 2-page approach document summarizing methodology, eval results, and optimization efforts.
- [ ] **Deployment Checks**: Ensure API endpoint and Streamlit app are accessible per submission form; host code on GitHub with instructions.
- [ ] **Submission Prep**: Assemble final deliverables—live API URL, GitHub repo, web app URL, formatted CSV, and concise report—for the referenced form.