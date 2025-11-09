"""
Evaluation script to calculate Mean Recall@K on training set
and generate predictions for test set
"""
import pandas as pd
import numpy as np
from recommendation_engine import RecommendationEngine
from typing import List, Dict
import sys

class Evaluator:
    def __init__(self, engine: RecommendationEngine):
        self.engine = engine
    
    def calculate_recall_at_k(self, predicted_urls: List[str], 
                              ground_truth_urls: List[str], k: int = 10) -> float:
        """
        Calculate Recall@K for a single query
        
        Recall@K = (Number of relevant items in top-K) / (Total relevant items)
        """
        # Take top-k predictions
        predicted_top_k = set(predicted_urls[:k])
        ground_truth = set(ground_truth_urls)
        
        # Calculate recall
        relevant_in_top_k = len(predicted_top_k.intersection(ground_truth))
        total_relevant = len(ground_truth)
        
        if total_relevant == 0:
            return 0.0
        
        recall = relevant_in_top_k / total_relevant
        return recall
    
    def evaluate_training_set(self, train_file: str = 'Gen_AI Dataset.xlsx', k: int = 10) -> Dict:
        """
        Evaluate on the training set and calculate Mean Recall@K
        """
        print(f"Evaluating on training set (K={k})...")
        
        # Load training data
        df = pd.read_excel(train_file, sheet_name='Train-Set')
        
        # Group by query
        query_groups = df.groupby('Query')['Assessment_url'].apply(list).reset_index()
        
        recalls = []
        results = []
        
        for idx, row in query_groups.iterrows():
            query = row['Query']
            ground_truth_urls = row['Assessment_url']
            
            print(f"\n{idx + 1}. Query: {query[:80]}...")
            print(f"   Ground truth: {len(ground_truth_urls)} assessments")
            
            # Get predictions
            result = self.engine.recommend(query, top_k=k)
            predicted_urls = [rec['url'] for rec in result['recommendations']]
            
            # Calculate recall
            recall = self.calculate_recall_at_k(predicted_urls, ground_truth_urls, k)
            recalls.append(recall)
            
            print(f"   Predicted: {len(predicted_urls)} assessments")
            print(f"   Recall@{k}: {recall:.3f}")
            
            results.append({
                'query': query,
                'ground_truth_count': len(ground_truth_urls),
                'predicted_count': len(predicted_urls),
                f'recall@{k}': recall
            })
        
        # Calculate mean recall
        mean_recall = np.mean(recalls)
        
        print(f"\n{'='*80}")
        print(f"Mean Recall@{k}: {mean_recall:.4f}")
        print(f"{'='*80}")
        
        return {
            'mean_recall': mean_recall,
            'individual_recalls': recalls,
            'details': results
        }
    
    def generate_test_predictions(self, test_file: str = 'Gen_AI Dataset.xlsx', 
                                  output_file: str = 'outputs/test_predictions.csv',
                                  k: int = 10) -> pd.DataFrame:
        """
        Generate predictions for test set in required CSV format
        
        Format:
        Query | Assessment_url
        Query 1 | URL 1
        Query 1 | URL 2
        ...
        """
        print(f"\nGenerating predictions for test set...")
        
        # Load test data
        test_df = pd.read_excel(test_file, sheet_name='Test-Set')
        
        predictions = []
        
        for idx, row in test_df.iterrows():
            query = row['Query']
            print(f"\n{idx + 1}. Processing: {query[:80]}...")
            
            # Get recommendations
            result = self.engine.recommend(query, top_k=k)
            
            # Add each prediction as a row
            for rec in result['recommendations']:
                predictions.append({
                    'Query': query,
                    'Assessment_url': rec['url']
                })
        
        # Create DataFrame
        pred_df = pd.DataFrame(predictions)
        
        # Save to CSV
        pred_df.to_csv(output_file, index=False)
        print(f"\nSaved predictions to {output_file}")
        print(f"Total rows: {len(pred_df)}")
        
        return pred_df


def main():
    """Run evaluation and generate test predictions"""
    print("="*80)
    print("SHL Assessment Recommendation - Evaluation")
    print("="*80)
    
    # Initialize engine
    engine = RecommendationEngine(catalog_path='data/shl_catalogue.csv')
    evaluator = Evaluator(engine)
    
    # Evaluate on training set
    print("\n" + "="*80)
    print("TRAINING SET EVALUATION")
    print("="*80)
    
    eval_results = evaluator.evaluate_training_set(k=10)
    
    # Save evaluation results
    eval_df = pd.DataFrame(eval_results['details'])
    eval_df.to_csv('outputs/training_evaluation.csv', index=False)
    print(f"\nSaved evaluation details to outputs/training_evaluation.csv")
    
    # Generate test predictions
    print("\n" + "="*80)
    print("TEST SET PREDICTIONS")
    print("="*80)
    
    test_pred_df = evaluator.generate_test_predictions(k=10)
    
    # Show sample
    print("\nSample predictions:")
    print(test_pred_df.head(15))
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)
    print(f"Mean Recall@10: {eval_results['mean_recall']:.4f}")
    print(f"Test predictions saved to: outputs/test_predictions.csv")


if __name__ == "__main__":
    main()
