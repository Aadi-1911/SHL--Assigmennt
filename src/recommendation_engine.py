"""
Recommendation engine using embeddings + LLM for SHL assessments
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle
from typing import List, Dict, Tuple
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class RecommendationEngine:
    def __init__(self, catalog_path: str = 'data/shl_catalogue.csv'):
        """Initialize the recommendation engine"""
        print("Loading catalog...")
        self.df = pd.read_csv(catalog_path)
        
        # Load embedding model (lightweight for speed)
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_api_key_here':
            genai.configure(api_key=api_key)
            self.use_llm = True
        else:
            print("Warning: GEMINI_API_KEY not found. LLM explanations disabled.")
            self.use_llm = False
        
        # Create embeddings cache path in the same directory as catalog
        catalog_dir = os.path.dirname(os.path.abspath(catalog_path))
        self.embeddings_path = os.path.join(catalog_dir, 'embeddings.pkl')
        
        # Load or create embeddings
        self.embeddings = self.load_or_create_embeddings()
        
        print(f"Loaded {len(self.df)} assessments")
    
    def load_or_create_embeddings(self) -> np.ndarray:
        """Load embeddings from cache or create new ones"""
        if os.path.exists(self.embeddings_path):
            print("Loading cached embeddings...")
            with open(self.embeddings_path, 'rb') as f:
                return pickle.load(f)
        else:
            print("Creating embeddings...")
            return self.create_embeddings()
    
    def create_embeddings(self) -> np.ndarray:
        """Create embeddings for all assessments"""
        # Combine relevant fields for embedding
        texts = []
        for _, row in self.df.iterrows():
            text = f"{row['assessment_name']} {row['description']} {row['domain']} {row['test_type']}"
            texts.append(text)
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Cache embeddings
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(embeddings, f)
        
        return embeddings
    
    def retrieve_candidates(self, query: str, top_k: int = 20) -> List[Tuple[int, float]]:
        """
        Retrieve top-k candidate assessments based on semantic similarity
        Returns list of (index, score) tuples
        """
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(idx, similarities[idx]) for idx in top_indices]
    
    def balance_recommendations(self, candidates: List[Dict], query: str) -> List[Dict]:
        """
        Balance recommendations to include diverse test types
        Focus on balancing Personality (P) and Knowledge/Skills (K) when query mentions both
        """
        query_lower = query.lower()
        
        # Check if query needs balanced recommendations
        needs_personality = any(word in query_lower for word in 
                               ['collaborate', 'team', 'behavior', 'personality', 'communication', 
                                'leadership', 'soft skill', 'stakeholder'])
        needs_technical = any(word in query_lower for word in 
                             ['java', 'python', 'sql', 'javascript', 'coding', 'programming', 
                              'technical', 'developer', 'engineer', 'analyst', 'data'])
        needs_cognitive = any(word in query_lower for word in 
                             ['cognitive', 'reasoning', 'analytical', 'thinking', 'aptitude'])
        
        if (needs_personality and needs_technical) or (needs_personality and needs_cognitive):
            # Need balanced mix
            personality_tests = [c for c in candidates if c['test_type'] == 'P']
            technical_tests = [c for c in candidates if c['test_type'] in ['K', 'C']]
            
            # Aim for roughly equal split
            target = len(candidates) // 2
            balanced = personality_tests[:target] + technical_tests[:target]
            
            # Fill remaining with highest scored
            remaining_slots = len(candidates) - len(balanced)
            other_candidates = [c for c in candidates if c not in balanced]
            balanced.extend(other_candidates[:remaining_slots])
            
            return balanced[:len(candidates)]
        
        return candidates
    
    def generate_explanation(self, query: str, recommendations: List[Dict]) -> Dict:
        """Generate LLM explanation for recommendations"""
        if not self.use_llm:
            return {
                'explanation': 'Recommendations based on semantic similarity to query.',
                'best_recommendation': recommendations[0]['assessment_name'] if recommendations else None
            }
        
        try:
            # Create prompt
            prompt = f"""You are an HR assessment recommendation expert. 

Job Query: {query}

Top Recommended Assessments:
"""
            for i, rec in enumerate(recommendations[:5], 1):
                prompt += f"\n{i}. {rec['assessment_name']} (Type: {rec['test_type_label']})"
                prompt += f"\n   Description: {rec['description'][:150]}..."
            
            prompt += """

Task:
1. For each assessment, explain in 1-2 sentences why it's relevant for this role
2. Identify which ONE assessment is the best overall fit and explain why
3. If the role requires both technical and behavioral skills, ensure you recommend a balanced mix

Format your response as:
**Assessment 1: [Name]**
[Explanation]

**Assessment 2: [Name]**
[Explanation]

...

**Best Overall: [Name]**
[Brief reasoning why this is the best fit]
"""
            
            # Call Gemini
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            # Extract best recommendation
            best_rec = recommendations[0]['assessment_name']
            if 'Best Overall:' in response.text:
                best_line = [line for line in response.text.split('\n') if 'Best Overall:' in line]
                if best_line:
                    best_rec = best_line[0].split('Best Overall:')[1].strip().split('**')[0].strip()
            
            return {
                'explanation': response.text,
                'best_recommendation': best_rec
            }
            
        except Exception as e:
            print(f"LLM error: {e}")
            return {
                'explanation': f'Recommendations based on semantic similarity. Error generating detailed explanation: {str(e)}',
                'best_recommendation': recommendations[0]['assessment_name'] if recommendations else None
            }
    
    def recommend(self, query: str, top_k: int = 10) -> Dict:
        """
        Main recommendation function
        Returns top-k recommendations with explanations
        """
        # Retrieve candidates
        candidates = self.retrieve_candidates(query, top_k=min(top_k * 2, 30))
        
        # Convert to list of dicts
        recommendations = []
        for idx, score in candidates:
            row = self.df.iloc[idx]
            test_type_map = {
                'P': 'Personality & Behavior',
                'K': 'Knowledge & Skills',
                'C': 'Cognitive',
                'G': 'General'
            }
            recommendations.append({
                'assessment_name': row['assessment_name'],
                'url': row['url'],
                'description': row['description'],
                'test_type': row['test_type'],
                'test_type_label': test_type_map.get(row['test_type'], 'General'),
                'domain': row['domain'],
                'similarity_score': float(score)
            })
        
        # Balance recommendations
        recommendations = self.balance_recommendations(recommendations, query)
        
        # Take top-k after balancing
        recommendations = recommendations[:top_k]
        
        # Generate LLM explanation
        llm_result = self.generate_explanation(query, recommendations)
        
        return {
            'query': query,
            'recommendations': recommendations,
            'explanation': llm_result['explanation'],
            'best_recommendation': llm_result['best_recommendation'],
            'total_results': len(recommendations)
        }


def main():
    """Test the recommendation engine"""
    engine = RecommendationEngine()
    
    # Test query
    test_query = "I am hiring for Java developers who can also collaborate effectively with my business teams."
    
    print(f"\n{'='*80}")
    print(f"Query: {test_query}")
    print('='*80)
    
    result = engine.recommend(test_query, top_k=5)
    
    print(f"\nTop {len(result['recommendations'])} Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"\n{i}. {rec['assessment_name']}")
        print(f"   Type: {rec['test_type_label']} | Domain: {rec['domain']}")
        print(f"   Score: {rec['similarity_score']:.3f}")
        print(f"   URL: {rec['url']}")
    
    if result['explanation']:
        print(f"\n{'='*80}")
        print("LLM Explanation:")
        print('='*80)
        print(result['explanation'])


if __name__ == "__main__":
    main()
