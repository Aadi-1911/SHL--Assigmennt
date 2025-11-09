Great — here’s a **detailed development plan** for your coding agent to build the web-based **GenAI + RAG assessment recommendation** project, scoped for a working MVP (not full-scale). You’ll be able to hit “deliverable” status without going into enterprise grade.

---

## 🎯 Project Goal

Build a web application that:

* Takes as input a job role (title + description + domain + level)
* Uses a small catalogue of assessments (from SHL) as a knowledge-base
* Implements a RAG style pipeline (retrieve relevant assessments + generate explanation)
* Returns the top 3-5 recommended assessments with reasoning
* Is web-accessible and working (UI + backend)
* **Important**: Focus on a simple working pipeline (minimum viable) rather than full production.
* Use GenAI (LLM) to generate explanation.

---

## 🗂 Development Plan (Agent Task List)

### Phase A: Setup & Data

1. **Catalogue data creation (Day 1)**

   * Manually create a small CSV (e.g., 20–30 entries) of SHL assessments. Include columns: `assessment_id`, `name`, `category`, `job_levels` (entry/mid/senior), `domain`, `description`.
   * Store under `data/shl_catalogue.csv`.
   * Make sure the description is concise but meaningful.

2. **Preprocessing & embedding setup (Day 2)**

   * Write `preprocessing.py` to load the catalogue CSV and create a combined text field (e.g., `name + description + domain + job_levels`).
   * Choose an embedding model (e.g., from `sentence-transformers`).
   * Generate embeddings for each assessment row, save them (e.g., `embeddings.npy` or pickle).
   * Write utility function to compute embedding for a user input.

### Phase B: Retrieval & Recommendation Logic

3. **Retrieval module (Day 3)**

   * Write `recommendation.py` which takes user input (`job_title`, `job_description`, `domain`, `job_level`)
   * Preprocess the input into a text string (e.g., “Software Engineer mid-level in domain IT: {description}”).
   * Compute embedding of user input.
   * Compute cosine similarity against the assessment embeddings.
   * Filter candidate assessments:

     * Only ones where `job_level` matches (or is acceptable)
     * If domain is provided, prefer same domain (or fallback if none)
   * Sort by similarity score.
   * Select top 3 recommendations.
   * Return list with `assessment_id`, `name`, `category`, `score`.

### Phase C: GenAI Explanation Module

4. **LLM explanation module (Day 4)**

   * Write `genai.py` which:

     * Accepts user input (job info) + list of top recommendations (with assessment metadata).
     * Constructs a prompt template to pass to an LLM API (e.g., from OpenAI).
     * E.g. prompt:

       ```
       You are an HR assessment recommendation assistant.
       Job role: {job_title}, domain: {domain}, level: {job_level}.
       Here are candidate assessments:
       1. {assessment_name1} — {description1}
       2. {assessment_name2} — {description2}
       3. {assessment_name3} — {description3}

       For each assessment, explain:
       - why it suits this job role
       - what key competencies or skills it measures
       - how it aligns with the job level and domain

       Then recommend the best one among them and give reasoning.
       ```
     * Send prompt, get response text, parse (if needed) into structured format: list of explanations + final recommendation.
   * Integrate with recommendation module: after retrieving top 3, call explanation module and merge response.

### Phase D: Web API + UI

5. **Backend API (Day 5)**

   * Build `app.py` with `FastAPI` (or Flask) that exposes endpoint `/recommend` (POST).
   * Input JSON: `{ "job_title": "...", "job_description": "...", "domain": "...", "job_level": "entry|mid|senior" }`
   * Endpoint logic:

     * Call retrieval module to get top recommendations
     * Call genAI module to get explanations
     * Return JSON: list of recommendations each with `name`, `category`, `score`, `explanation`, plus maybe `best_recommendation`.
   * Add simple error handling (e.g., missing fields).

6. **Frontend UI (Day 6)**

   * Use `Streamlit` for simplicity.
   * Fields: job title (text), job description (text area), domain (text or dropdown), job level (dropdown).
   * On “Recommend” click: call backend via HTTP POST.
   * Display results: For each recommendation show: assessment name, category, match score (maybe a bar or %), explanation. Highlight “Best recommendation”.
   * Minimal styling is OK. No need for production UI.

### Phase E: Testing, Wrap-up & Delivery

7. **Testing & sample inputs (Day 7)**

   * Create 3-5 sample job roles (with domain + description) and test the system end-to-end.
   * Verify that recommendations make sense manually.
   * Fix any obvious mismatches (e.g., job level filter too strict).
   * Add simple logging (console) of each request and result for visibility.

8. **Documentation & packaging**

   * Add `README.md` with instructions: prerequisites, environment setup (`requirements.txt`), how to run backend and UI.
   * Include sample input JSON in README.
   * Package everything in a GitHub repo folder structure.
   * (Optional) Dockerfile for containerized run (not required if just working demo).

---

## ⚙ Minimum Deliverables Summary

* A working web app (frontend + backend) accessible locally (or deployed if possible).
* Ability to input job role details and get top 3 assessment recommendations with explanations.
* Simple but clean codebase with modules as above.
* Documentation for setup and run.
* Enough sample catalogue data to demonstrate the system works.

---

## 🔍 Why This Approach Works

* Uses the RAG architecture pattern: retrieval from catalogue + generation of explanation via LLM. ([NVIDIA Developer][1])
* Scoped to MVP so deliverable is feasible in short time.
* Clear modular breakdown so your agent can work task by task.
* Web UI ensures demonstration ready.

---

If you like, I can generate a **task list with checkboxes** for the agent (spread across days) ready to assign, along with a **repository skeleton** (folder structure + empty files) and **requirements.txt**. Would you like me to create that?

[1]: https://developer.nvidia.com/blog/rag-101-demystifying-retrieval-augmented-generation-pipelines/?utm_source=chatgpt.com "RAG 101: Demystifying Retrieval-Augmented Generation Pipelines"
