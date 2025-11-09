"""
Web scraper to extract SHL assessment data from their product catalog
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict

class SHLScraper:
    def __init__(self):
        self.base_url = "https://www.shl.com/solutions/products/product-catalog/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_catalog(self) -> pd.DataFrame:
        """
        Scrape the SHL product catalog page
        Returns DataFrame with assessment details
        """
        print("Scraping SHL catalog...")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            assessments = []
            
            # Find all assessment cards/links (adjust selectors based on actual HTML structure)
            # This is a simplified approach - you may need to adjust based on actual page structure
            assessment_links = soup.find_all('a', href=re.compile(r'/products/product-catalog/'))
            
            # Extract unique assessment URLs
            seen_urls = set()
            for link in assessment_links:
                url = link.get('href', '')
                if url and url not in seen_urls and 'product-catalog' in url:
                    if not url.startswith('http'):
                        url = 'https://www.shl.com' + url
                    seen_urls.add(url)
            
            print(f"Found {len(seen_urls)} unique assessment URLs")
            
            # Scrape details from each assessment page
            for idx, url in enumerate(list(seen_urls)[:50], 1):  # Limit for demo
                try:
                    print(f"Scraping {idx}/{min(50, len(seen_urls))}: {url}")
                    assessment = self.scrape_assessment_page(url)
                    if assessment:
                        assessments.append(assessment)
                    time.sleep(0.5)  # Be polite
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue
            
            if not assessments:
                print("No assessments found via scraping. Creating sample catalog...")
                return self.create_sample_catalog()
            
            df = pd.DataFrame(assessments)
            return df
            
        except Exception as e:
            print(f"Error scraping catalog: {e}")
            print("Creating sample catalog instead...")
            return self.create_sample_catalog()
    
    def scrape_assessment_page(self, url: str) -> Dict:
        """Scrape individual assessment page for details"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title = title.get_text(strip=True) if title else "Unknown Assessment"
            
            # Extract description
            description = ""
            desc_elem = soup.find('meta', {'name': 'description'})
            if desc_elem:
                description = desc_elem.get('content', '')
            
            # Try to infer test type from title/description
            test_type = self.infer_test_type(title, description)
            
            # Try to infer domain
            domain = self.infer_domain(title, description)
            
            return {
                'assessment_name': title,
                'url': url,
                'description': description,
                'test_type': test_type,
                'domain': domain,
                'job_level': 'all'  # Default
            }
        except Exception as e:
            return None
    
    def infer_test_type(self, title: str, description: str) -> str:
        """Infer test type from content"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['personality', 'behavior', 'behaviour', 'opq', 'motivation']):
            return 'P'  # Personality & Behavior
        elif any(word in text for word in ['cognitive', 'reasoning', 'verbal', 'numerical', 'verify']):
            return 'C'  # Cognitive
        elif any(word in text for word in ['skill', 'technical', 'programming', 'coding', 'java', 'python']):
            return 'K'  # Knowledge & Skills
        else:
            return 'G'  # General
    
    def infer_domain(self, title: str, description: str) -> str:
        """Infer domain from content"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['sales', 'customer', 'account']):
            return 'Sales'
        elif any(word in text for word in ['leader', 'manager', 'executive', 'coo', 'ceo']):
            return 'Leadership'
        elif any(word in text for word in ['technical', 'developer', 'engineer', 'programming']):
            return 'Technical'
        elif any(word in text for word in ['admin', 'support', 'assistant']):
            return 'Administrative'
        elif any(word in text for word in ['analyst', 'data', 'research']):
            return 'Analytics'
        else:
            return 'General'
    
    def create_sample_catalog(self) -> pd.DataFrame:
        """Create a sample catalog based on common SHL assessments"""
        assessments = [
            {
                'assessment_name': 'Verify Interactive - Numerical Reasoning',
                'url': 'https://www.shl.com/solutions/products/product-catalog/verify-interactive-numerical/',
                'description': 'Measures numerical reasoning and data interpretation skills',
                'test_type': 'C',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Verify Interactive - Verbal Reasoning',
                'url': 'https://www.shl.com/solutions/products/product-catalog/verify-interactive-verbal/',
                'description': 'Assesses verbal reasoning and comprehension abilities',
                'test_type': 'C',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'OPQ (Occupational Personality Questionnaire)',
                'url': 'https://www.shl.com/solutions/products/product-catalog/opq/',
                'description': 'Comprehensive personality assessment for workplace behavior',
                'test_type': 'P',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Java Programming Skills Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/java-test/',
                'description': 'Technical assessment for Java programming competency',
                'test_type': 'K',
                'domain': 'Technical',
                'job_level': 'mid,senior'
            },
            {
                'assessment_name': 'Python Programming Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/python-test/',
                'description': 'Evaluates Python coding skills and problem-solving',
                'test_type': 'K',
                'domain': 'Technical',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Situational Judgement Test - Customer Service',
                'url': 'https://www.shl.com/solutions/products/product-catalog/sjt-customer-service/',
                'description': 'Measures decision-making in customer service scenarios',
                'test_type': 'P',
                'domain': 'Sales',
                'job_level': 'entry,mid'
            },
            {
                'assessment_name': 'Leadership Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/leadership-assessment/',
                'description': 'Evaluates leadership competencies and management potential',
                'test_type': 'P',
                'domain': 'Leadership',
                'job_level': 'senior'
            },
            {
                'assessment_name': 'SQL Skills Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/sql-test/',
                'description': 'Tests SQL query writing and database knowledge',
                'test_type': 'K',
                'domain': 'Technical',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Data Analysis Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/data-analysis/',
                'description': 'Assesses data interpretation and analytical thinking',
                'test_type': 'C',
                'domain': 'Analytics',
                'job_level': 'mid,senior'
            },
            {
                'assessment_name': 'Teamwork and Collaboration Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/teamwork/',
                'description': 'Measures collaboration skills and team dynamics',
                'test_type': 'P',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'JavaScript Coding Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/javascript-test/',
                'description': 'Evaluates JavaScript programming proficiency',
                'test_type': 'K',
                'domain': 'Technical',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Sales Aptitude Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/sales-aptitude/',
                'description': 'Identifies sales potential and customer-facing skills',
                'test_type': 'P',
                'domain': 'Sales',
                'job_level': 'entry,mid'
            },
            {
                'assessment_name': 'Administrative Skills Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/admin-skills/',
                'description': 'Tests organizational and administrative competencies',
                'test_type': 'K',
                'domain': 'Administrative',
                'job_level': 'entry,mid'
            },
            {
                'assessment_name': 'Critical Thinking Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/critical-thinking/',
                'description': 'Measures analytical and critical reasoning abilities',
                'test_type': 'C',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Motivation Questionnaire (MQ)',
                'url': 'https://www.shl.com/solutions/products/product-catalog/mq/',
                'description': 'Assesses workplace motivations and drivers',
                'test_type': 'P',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Communication Skills Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/communication/',
                'description': 'Evaluates written and verbal communication abilities',
                'test_type': 'K',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Verify Interactive - Inductive Reasoning',
                'url': 'https://www.shl.com/solutions/products/product-catalog/verify-inductive/',
                'description': 'Tests pattern recognition and logical thinking',
                'test_type': 'C',
                'domain': 'General',
                'job_level': 'all'
            },
            {
                'assessment_name': 'Graduate Aptitude Battery',
                'url': 'https://www.shl.com/solutions/products/product-catalog/graduate-aptitude/',
                'description': 'Comprehensive assessment for entry-level candidates',
                'test_type': 'C',
                'domain': 'General',
                'job_level': 'entry'
            },
            {
                'assessment_name': 'Manager Readiness Assessment',
                'url': 'https://www.shl.com/solutions/products/product-catalog/manager-readiness/',
                'description': 'Identifies management potential and readiness',
                'test_type': 'P',
                'domain': 'Leadership',
                'job_level': 'mid,senior'
            },
            {
                'assessment_name': 'Problem Solving Skills Test',
                'url': 'https://www.shl.com/solutions/products/product-catalog/problem-solving/',
                'description': 'Measures complex problem-solving abilities',
                'test_type': 'C',
                'domain': 'General',
                'job_level': 'all'
            }
        ]
        
        return pd.DataFrame(assessments)


def main():
    scraper = SHLScraper()
    df = scraper.scrape_catalog()
    
    # Save to CSV
    output_path = 'data/shl_catalogue.csv'
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} assessments to {output_path}")
    print(f"\nSample assessments:")
    print(df.head())
    print(f"\nTest type distribution:")
    print(df['test_type'].value_counts())


if __name__ == "__main__":
    main()
