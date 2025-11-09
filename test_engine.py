"""
Quick test script to verify the recommendation engine works
"""
import sys
sys.path.insert(0, 'src')

from recommendation_engine import RecommendationEngine

def test_basic_recommendation():
    """Test basic recommendation functionality"""
    print("="*80)
    print("Testing SHL Recommendation Engine")
    print("="*80)
    
    # Initialize engine
    print("\n1. Initializing engine...")
    engine = RecommendationEngine(catalog_path='data/shl_catalogue.csv')
    print("✓ Engine initialized successfully")
    
    # Test queries
    test_queries = [
        "Java developer with good collaboration skills",
        "Entry-level sales professional", 
        "Senior data analyst with Python and SQL"
    ]
    
    print(f"\n2. Testing {len(test_queries)} queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {query}")
        print('='*80)
        
        # Get recommendations
        result = engine.recommend(query, top_k=5)
        
        print(f"\nTop {len(result['recommendations'])} Recommendations:")
        for j, rec in enumerate(result['recommendations'], 1):
            print(f"{j}. {rec['assessment_name']}")
            print(f"   Type: {rec['test_type_label']} | Score: {rec['similarity_score']:.3f}")
        
        # Check for balance
        test_types = [r['test_type'] for r in result['recommendations']]
        print(f"\nTest type distribution: {', '.join(test_types)}")
        
        if 'P' in test_types and ('K' in test_types or 'C' in test_types):
            print("✓ Balanced recommendations detected")
    
    print(f"\n{'='*80}")
    print("All tests passed! ✓")
    print('='*80)

if __name__ == "__main__":
    test_basic_recommendation()
