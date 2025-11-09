"""
Build SHL catalog from training dataset
This ensures URLs match the ground truth for proper evaluation
"""
import pandas as pd
import re

def infer_test_type(name):
    """Infer test type from assessment name"""
    name_lower = name.lower()
    
    # Personality & Behavior (P)
    if any(word in name_lower for word in ['opq', 'personality', 'motivation', 'behavioral', 'values', 'teamwork', 'communication']):
        return 'P'
    
    # Knowledge & Skills (K)
    if any(word in name_lower for word in ['programming', 'java', 'python', 'javascript', 'sql', 'coding', 'technical', 'mechanical', 'excel']):
        return 'K'
    
    # Cognitive (C)
    if any(word in name_lower for word in ['verify', 'reasoning', 'numerical', 'verbal', 'inductive', 'deductive', 'aptitude', 'cognitive']):
        return 'C'
    
    # General (G)
    return 'G'

def infer_domain(name):
    """Infer domain from assessment name"""
    name_lower = name.lower()
    
    if 'leadership' in name_lower or 'manager' in name_lower:
        return 'Leadership'
    elif 'sales' in name_lower or 'customer' in name_lower:
        return 'Sales & Customer Service'
    elif any(word in name_lower for word in ['programming', 'java', 'python', 'sql', 'technical', 'developer']):
        return 'Technology'
    elif 'admin' in name_lower or 'clerical' in name_lower:
        return 'Administrative'
    elif 'graduate' in name_lower or 'trainee' in name_lower:
        return 'Graduate & Entry-Level'
    else:
        return 'General'

def infer_job_level(name):
    """Infer job level from assessment name"""
    name_lower = name.lower()
    
    if 'graduate' in name_lower or 'entry' in name_lower or 'trainee' in name_lower:
        return 'Entry'
    elif 'senior' in name_lower or 'leadership' in name_lower or 'manager' in name_lower:
        return 'Senior'
    else:
        return 'Mid'

def create_description(name, test_type, domain):
    """Generate a description based on assessment name and metadata"""
    type_descriptions = {
        'P': 'personality and behavioral',
        'K': 'knowledge and technical skills',
        'C': 'cognitive abilities and reasoning',
        'G': 'general aptitude'
    }
    
    type_desc = type_descriptions.get(test_type, 'professional')
    
    return f"This assessment evaluates {type_desc} relevant to {domain.lower()} roles. {name} helps identify candidates with the right competencies and potential for success."

def extract_name_from_url(url):
    """Extract assessment name from URL"""
    # Extract the last part of the URL path
    parts = url.rstrip('/').split('/')
    name_slug = parts[-1]
    
    # Convert slug to readable name
    # Replace hyphens with spaces and capitalize
    name = name_slug.replace('-', ' ').title()
    
    # Clean up common patterns
    name = name.replace('Shl', 'SHL').replace('Opq', 'OPQ')
    
    return name

def main():
    print("Building catalog from training dataset...")
    print("="*80)
    
    # Load training data
    df = pd.read_excel('Gen_AI Dataset.xlsx', sheet_name='Train-Set')
    print(f"Loaded {len(df)} training examples")
    
    # Extract unique assessment URLs
    catalog = df[['Assessment_url']].drop_duplicates()
    print(f"Found {len(catalog)} unique assessment URLs")
    
    # Extract names from URLs
    catalog['assessment_name'] = catalog['Assessment_url'].apply(extract_name_from_url)
    
    # Rename columns to match expected format
    catalog.columns = ['url', 'assessment_name']
    catalog = catalog[['assessment_name', 'url']]  # Reorder
    
    # Infer metadata
    print("\nInferring metadata...")
    catalog['test_type'] = catalog['assessment_name'].apply(infer_test_type)
    catalog['domain'] = catalog['assessment_name'].apply(infer_domain)
    catalog['job_level'] = catalog['assessment_name'].apply(infer_job_level)
    catalog['description'] = catalog.apply(
        lambda row: create_description(row['assessment_name'], row['test_type'], row['domain']), 
        axis=1
    )
    
    # Add full test type labels for display
    test_type_labels = {
        'P': 'Personality & Behavior',
        'K': 'Knowledge & Skills',
        'C': 'Cognitive',
        'G': 'General'
    }
    catalog['test_type_label'] = catalog['test_type'].map(test_type_labels)
    
    # Reorder columns
    catalog = catalog[['assessment_name', 'url', 'description', 'test_type', 'test_type_label', 'domain', 'job_level']]
    
    # Save to CSV
    output_file = 'data/shl_catalogue.csv'
    catalog.to_csv(output_file, index=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Catalog saved to: {output_file}")
    print(f"   Total assessments: {len(catalog)}")
    print(f"\nTest type distribution:")
    print(catalog['test_type_label'].value_counts())
    print(f"\nDomain distribution:")
    print(catalog['domain'].value_counts())
    print(f"\n{'='*80}")
    print("\nSample entries:")
    print(catalog[['assessment_name', 'test_type_label', 'domain']].head(10).to_string(index=False))
    print(f"\n{'='*80}")
    print("\n✅ Next steps:")
    print("1. Delete old embeddings: rm data/embeddings.pkl")
    print("2. Restart API server (if running)")
    print("3. Run evaluation: python src/evaluate.py")
    print("4. Check Mean Recall@10 score (should be > 0.5 now)")

if __name__ == "__main__":
    main()
