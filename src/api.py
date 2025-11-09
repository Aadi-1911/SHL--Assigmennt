"""
FastAPI backend for SHL Assessment Recommendation System
Follows API specification from assignment Appendix 2
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from recommendation_engine import RecommendationEngine

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="API for recommending SHL assessments based on job descriptions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommendation engine (singleton)
engine = None

@app.on_event("startup")
async def startup_event():
    """Load recommendation engine on startup"""
    global engine
    print("Initializing recommendation engine...")
    # Use absolute path relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    catalog_path = os.path.join(base_dir, 'data', 'shl_catalogue.csv')
    engine = RecommendationEngine(catalog_path=catalog_path)
    print("API ready!")


# Request/Response Models
class RecommendRequest(BaseModel):
    query: str = Field(..., description="Job description or natural language query")
    top_k: Optional[int] = Field(10, description="Number of recommendations (1-10)", ge=1, le=10)


class AssessmentRecommendation(BaseModel):
    assessment_name: str
    url: str
    relevance_score: Optional[float] = None
    test_type: Optional[str] = None
    explanation: Optional[str] = None


class RecommendResponse(BaseModel):
    query: str
    recommendations: List[AssessmentRecommendation]
    total_results: int
    explanation: Optional[str] = None
    best_recommendation: Optional[str] = None


# Endpoints
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns API status
    """
    return {
        "status": "healthy",
        "message": "SHL Assessment Recommendation API is running",
        "version": "1.0.0"
    }


@app.post("/recommend", response_model=RecommendResponse)
async def recommend_assessments(request: RecommendRequest):
    """
    Recommend assessments based on job query
    
    Parameters:
    - query: Job description or natural language query
    - top_k: Number of recommendations to return (1-10)
    
    Returns:
    - List of recommended assessments with URLs and relevance scores
    """
    if not engine:
        raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
    
    if not request.query or len(request.query.strip()) < 10:
        raise HTTPException(status_code=400, detail="Query must be at least 10 characters")
    
    try:
        # Get recommendations
        result = engine.recommend(request.query, top_k=request.top_k)
        
        # Format response
        recommendations = [
            AssessmentRecommendation(
                assessment_name=rec['assessment_name'],
                url=rec['url'],
                relevance_score=rec['similarity_score'],
                test_type=rec['test_type_label'],
                explanation=None  # Can add per-item explanation if needed
            )
            for rec in result['recommendations']
        ]
        
        return RecommendResponse(
            query=result['query'],
            recommendations=recommendations,
            total_results=result['total_results'],
            explanation=result['explanation'],
            best_recommendation=result['best_recommendation']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SHL Assessment Recommendation API",
        "endpoints": {
            "health": "/health - Check API status",
            "recommend": "/recommend - Get assessment recommendations (POST)",
            "docs": "/docs - Interactive API documentation"
        },
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
