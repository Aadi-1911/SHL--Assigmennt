"""
Streamlit frontend for SHL Assessment Recommendation System
"""
import streamlit as st
import requests
import pandas as pd
from typing import Dict, List

# Page config
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="📋",
    layout="wide"
)

# API endpoint (configurable)
API_URL = st.sidebar.text_input("API Endpoint", value="http://localhost:8000")

# Title
st.title("📋 SHL Assessment Recommendation System")
st.markdown("Find the most relevant SHL assessments for your job requirements")

# Sidebar with instructions
with st.sidebar:
    st.header("ℹ️ How to Use")
    st.markdown("""
    1. Enter a job description or natural language query
    2. Specify number of recommendations (5-10)
    3. Click **Get Recommendations**
    4. Review results in table format
    
    **Example Queries:**
    - "Java developer with good collaboration skills"
    - "Entry-level sales professional"
    - "Senior data analyst with Python and SQL"
    """)
    
    st.divider()
    st.markdown("**Test Type Legend:**")
    st.markdown("""
    - 🧠 **Cognitive (C)**: Reasoning, aptitude
    - 👤 **Personality (P)**: Behavior, soft skills
    - 💻 **Knowledge (K)**: Technical skills
    - 📊 **General (G)**: Multi-purpose
    """)

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_area(
        "Job Description or Query",
        placeholder="E.g., I am hiring for Java developers who can also collaborate effectively with my business teams.",
        height=100
    )

with col2:
    num_recommendations = st.slider(
        "Number of Results",
        min_value=5,
        max_value=10,
        value=10,
        step=1
    )

# Submit button
if st.button("🔍 Get Recommendations", type="primary", use_container_width=True):
    if not query or len(query.strip()) < 10:
        st.error("Please enter a query with at least 10 characters")
    else:
        with st.spinner("Finding best assessments..."):
            try:
                # Call API
                response = requests.post(
                    f"{API_URL}/recommend",
                    json={"query": query, "top_k": num_recommendations},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display summary
                    st.success(f"✅ Found {result['total_results']} relevant assessments")
                    
                    # Best recommendation highlight
                    if result.get('best_recommendation'):
                        st.info(f"🏆 **Best Match:** {result['best_recommendation']}")
                    
                    # Recommendations table
                    st.subheader("📊 Recommended Assessments")
                    
                    # Convert to DataFrame
                    recommendations = result['recommendations']
                    df = pd.DataFrame([
                        {
                            'Rank': i + 1,
                            'Assessment Name': rec['assessment_name'],
                            'Test Type': rec.get('test_type', 'General'),
                            'Relevance Score': f"{rec.get('relevance_score', 0):.3f}",
                            'URL': rec['url']
                        }
                        for i, rec in enumerate(recommendations)
                    ])
                    
                    # Display table
                    st.dataframe(
                        df,
                        column_config={
                            "URL": st.column_config.LinkColumn("Assessment Link"),
                            "Relevance Score": st.column_config.ProgressColumn(
                                "Relevance",
                                format="%.3f",
                                min_value=0,
                                max_value=1,
                            ),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Test type distribution
                    st.subheader("📈 Test Type Distribution")
                    test_type_counts = df['Test Type'].value_counts()
                    st.bar_chart(test_type_counts)
                    
                    # LLM Explanation
                    if result.get('explanation'):
                        with st.expander("💡 Detailed Explanation", expanded=False):
                            st.markdown(result['explanation'])
                    
                    # Download CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results (CSV)",
                        data=csv,
                        file_name="shl_recommendations.csv",
                        mime="text/csv"
                    )
                
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to API at {API_URL}. Please ensure the API server is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Sample queries section
st.divider()
st.subheader("💡 Sample Queries to Try")

sample_queries = [
    "I am hiring for Java developers who can also collaborate effectively with my business teams.",
    "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript.",
    "I want to hire new graduates for a sales role in my company.",
    "Need a senior data analyst with 5 years of experience.",
    "Looking for a COO with strong leadership skills.",
]

cols = st.columns(len(sample_queries))
for i, sample in enumerate(sample_queries):
    with cols[i]:
        if st.button(f"Sample {i+1}", key=f"sample_{i}", use_container_width=True):
            st.rerun()

# Footer
st.divider()
st.caption("SHL Assessment Recommendation System | Powered by Sentence Transformers + Gemini")
