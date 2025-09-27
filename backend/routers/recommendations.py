from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import User, StyleDNA, Outfit, Recommendation, CategoryEnum, SubcategoryEnum, OccasionEnum
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class RecommendationRequest(BaseModel):
    context: Optional[str] = None  # occasion, mood, event
    limit: Optional[int] = 10
    include_tried: Optional[bool] = False  # Include previously tried items

class OutfitRecommendation(BaseModel):
    id: int
    name: str
    description: Optional[str]
    brand: Optional[str]
    category: CategoryEnum
    subcategory: SubcategoryEnum
    occasion: OccasionEnum
    price: float
    discounted_price: Optional[float]
    primary_image_url: str
    colors: Optional[List[str]]
    sizes: Optional[List[str]]
    tags: Optional[List[str]]
    
    # Recommendation specific fields
    confidence_score: float
    recommendation_reason: str
    match_factors: List[str]
    
    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    recommendations: List[OutfitRecommendation]
    user_style_dna: Optional[Dict[str, Any]]
    context: Optional[str]
    algorithm_used: str
    generated_at: datetime
    total_available: int

class RecommendationFeedback(BaseModel):
    recommendation_id: int
    was_liked: Optional[bool] = None
    was_viewed: Optional[bool] = None
    user_rating: Optional[int] = None  # 1-5
    user_feedback: Optional[str] = None

@router.get("/recommend/{user_id}", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    user_id: int,
    context: Optional[str] = Query(None, description="Occasion or context for recommendations"),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    include_tried: bool = Query(False, description="Include previously tried items"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized outfit recommendations for a user"""
    
    # Verify user access (users can only get their own recommendations or admin access)
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get user's Style DNA
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == user_id).first()
    
    if not style_dna:
        # Fall back to general trending recommendations if no Style DNA
        return await _get_general_recommendations(user_id, context, limit, db)
    
    # Get personalized recommendations based on Style DNA
    recommendations = await _get_style_dna_recommendations(
        user_id, style_dna, context, limit, include_tried, db
    )
    
    return RecommendationResponse(
        recommendations=recommendations,
        user_style_dna=_serialize_style_dna(style_dna),
        context=context,
        algorithm_used="style_dna_based",
        generated_at=datetime.utcnow(),
        total_available=len(recommendations)
    )

@router.post("/recommend/feedback")
async def submit_recommendation_feedback(
    feedback: RecommendationFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback on a recommendation"""
    
    # Find the recommendation
    recommendation = db.query(Recommendation).filter(
        and_(
            Recommendation.id == feedback.recommendation_id,
            Recommendation.user_id == current_user.id
        )
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Update recommendation with feedback
    if feedback.was_liked is not None:
        recommendation.was_liked = feedback.was_liked
    if feedback.was_viewed is not None:
        recommendation.was_viewed = feedback.was_viewed
    if feedback.user_rating is not None:
        recommendation.user_rating = feedback.user_rating
    if feedback.user_feedback is not None:
        recommendation.user_feedback = feedback.user_feedback
    
    db.commit()
    
    return {"message": "Feedback submitted successfully"}

@router.get("/recommend/history")
async def get_recommendation_history(
    limit: int = Query(50, ge=1, le=200, description="Number of historical recommendations"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's recommendation history"""
    
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).order_by(
        desc(Recommendation.created_at)
    ).limit(limit).all()
    
    # Group recommendations by context/occasion
    grouped_recommendations = {}
    for rec in recommendations:
        context = rec.context or "general"
        if context not in grouped_recommendations:
            grouped_recommendations[context] = []
        
        grouped_recommendations[context].append({
            "id": rec.id,
            "outfit_id": rec.outfit_id,
            "confidence_score": rec.confidence_score,
            "recommendation_type": rec.recommendation_type,
            "was_viewed": rec.was_viewed,
            "was_liked": rec.was_liked,
            "was_purchased": rec.was_purchased,
            "was_tried_on": rec.was_tried_on,
            "user_rating": rec.user_rating,
            "created_at": rec.created_at
        })
    
    return {
        "recommendation_history": grouped_recommendations,
        "total_recommendations": len(recommendations),
        "contexts": list(grouped_recommendations.keys())
    }

@router.get("/recommend/insights")
async def get_recommendation_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insights about user's recommendation patterns and preferences"""
    
    # Get user's recommendation statistics
    total_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).count()
    
    liked_recommendations = db.query(Recommendation).filter(
        and_(
            Recommendation.user_id == current_user.id,
            Recommendation.was_liked == True
        )
    ).count()
    
    purchased_recommendations = db.query(Recommendation).filter(
        and_(
            Recommendation.user_id == current_user.id,
            Recommendation.was_purchased == True
        )
    ).count()
    
    # Get most recommended categories
    category_stats = db.query(
        Outfit.category,
        func.count(Recommendation.id).label('count')
    ).join(
        Recommendation, Outfit.id == Recommendation.outfit_id
    ).filter(
        Recommendation.user_id == current_user.id
    ).group_by(
        Outfit.category
    ).order_by(
        desc('count')
    ).all()
    
    # Get most liked occasions
    occasion_stats = db.query(
        Outfit.occasion,
        func.count(Recommendation.id).label('count')
    ).join(
        Recommendation, Outfit.id == Recommendation.outfit_id
    ).filter(
        and_(
            Recommendation.user_id == current_user.id,
            Recommendation.was_liked == True
        )
    ).group_by(
        Outfit.occasion
    ).order_by(
        desc('count')
    ).all()
    
    like_rate = (liked_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
    purchase_rate = (purchased_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
    
    return {
        "statistics": {
            "total_recommendations": total_recommendations,
            "liked_recommendations": liked_recommendations,
            "purchased_recommendations": purchased_recommendations,
            "like_rate": round(like_rate, 1),
            "purchase_rate": round(purchase_rate, 1)
        },
        "preferences": {
            "favorite_categories": [{"category": cat[0].value, "count": cat[1]} for cat in category_stats[:5]],
            "favorite_occasions": [{"occasion": occ[0].value, "count": occ[1]} for occ in occasion_stats[:5]]
        },
        "recommendation_quality": {
            "accuracy_score": like_rate,
            "conversion_rate": purchase_rate,
            "engagement_level": "high" if like_rate > 70 else "medium" if like_rate > 40 else "low"
        }
    }

# Helper functions
async def _get_general_recommendations(user_id: int, context: str, limit: int, db: Session) -> RecommendationResponse:
    """Get general trending recommendations for users without Style DNA"""
    
    # Get popular/trending outfits
    outfits = db.query(Outfit).filter(
        Outfit.is_available == True
    ).order_by(
        desc(Outfit.created_at)
    ).limit(limit).all()
    
    recommendations = []
    for outfit in outfits:
        recommendations.append(OutfitRecommendation(
            id=outfit.id,
            name=outfit.name,
            description=outfit.description,
            brand=outfit.brand,
            category=outfit.category,
            subcategory=outfit.subcategory,
            occasion=outfit.occasion,
            price=outfit.price,
            discounted_price=outfit.discounted_price,
            primary_image_url=outfit.primary_image_url,
            colors=outfit.colors,
            sizes=outfit.sizes,
            tags=outfit.tags,
            confidence_score=0.5,  # Default confidence for general recommendations
            recommendation_reason="Trending outfit",
            match_factors=["popular", "recently_added"]
        ))
    
    return RecommendationResponse(
        recommendations=recommendations,
        user_style_dna=None,
        context=context,
        algorithm_used="general_trending",
        generated_at=datetime.utcnow(),
        total_available=len(recommendations)
    )

async def _get_style_dna_recommendations(
    user_id: int, 
    style_dna: StyleDNA, 
    context: str, 
    limit: int, 
    include_tried: bool,
    db: Session
) -> List[OutfitRecommendation]:
    """Get recommendations based on user's Style DNA"""
    
    # Base query
    query = db.query(Outfit).filter(Outfit.is_available == True)
    
    # Apply Style DNA filters
    recommendations_data = []
    
    # Filter by preferred occasions if context is provided
    if context:
        try:
            context_occasion = OccasionEnum(context.lower())
            query = query.filter(Outfit.occasion == context_occasion)
        except ValueError:
            pass  # Invalid context, ignore
    elif style_dna.preferred_occasions:
        # Use user's preferred occasions
        preferred_occasions = [OccasionEnum(occ) for occ in style_dna.preferred_occasions if occ in [e.value for e in OccasionEnum]]
        if preferred_occasions:
            query = query.filter(Outfit.occasion.in_(preferred_occasions))
    
    # Filter by budget range
    if style_dna.budget_range:
        min_budget = style_dna.budget_range.get("min", 0)
        max_budget = style_dna.budget_range.get("max", 100000)
        query = query.filter(
            and_(Outfit.price >= min_budget, Outfit.price <= max_budget)
        )
    
    # Get outfits and score them
    outfits = query.order_by(desc(Outfit.created_at)).limit(limit * 2).all()  # Get more for filtering
    
    for outfit in outfits:
        confidence_score, match_factors, reason = _calculate_style_match(outfit, style_dna)
        
        if confidence_score > 0.3:  # Only include reasonably good matches
            recommendations_data.append({
                "outfit": outfit,
                "confidence_score": confidence_score,
                "match_factors": match_factors,
                "reason": reason
            })
    
    # Sort by confidence score and take top results
    recommendations_data.sort(key=lambda x: x["confidence_score"], reverse=True)
    top_recommendations = recommendations_data[:limit]
    
    # Convert to OutfitRecommendation objects
    recommendations = []
    for rec_data in top_recommendations:
        outfit = rec_data["outfit"]
        recommendations.append(OutfitRecommendation(
            id=outfit.id,
            name=outfit.name,
            description=outfit.description,
            brand=outfit.brand,
            category=outfit.category,
            subcategory=outfit.subcategory,
            occasion=outfit.occasion,
            price=outfit.price,
            discounted_price=outfit.discounted_price,
            primary_image_url=outfit.primary_image_url,
            colors=outfit.colors,
            sizes=outfit.sizes,
            tags=outfit.tags,
            confidence_score=rec_data["confidence_score"],
            recommendation_reason=rec_data["reason"],
            match_factors=rec_data["match_factors"]
        ))
    
    # Save recommendations to database for tracking
    for rec in recommendations:
        db_recommendation = Recommendation(
            user_id=user_id,
            outfit_id=rec.id,
            confidence_score=rec.confidence_score,
            recommendation_type="style_dna",
            context=context
        )
        db.add(db_recommendation)
    
    db.commit()
    
    return recommendations

def _calculate_style_match(outfit: Outfit, style_dna: StyleDNA) -> tuple[float, List[str], str]:
    """Calculate how well an outfit matches the user's Style DNA"""
    
    score = 0.0
    match_factors = []
    reasons = []
    
    # Color matching
    if style_dna.preferred_colors and outfit.colors:
        color_match = len(set(style_dna.preferred_colors) & set(outfit.colors))
        if color_match > 0:
            score += 0.3
            match_factors.append("color_preference")
            reasons.append(f"matches your preferred colors")
    
    # Avoid colors
    if style_dna.avoided_colors and outfit.colors:
        avoided_match = len(set(style_dna.avoided_colors) & set(outfit.colors))
        if avoided_match > 0:
            score -= 0.2  # Penalty for avoided colors
    
    # Style tags matching
    if style_dna.preferred_styles and outfit.tags:
        style_match = len(set(style_dna.preferred_styles) & set(outfit.tags))
        if style_match > 0:
            score += 0.25
            match_factors.append("style_preference")
            reasons.append("fits your style preferences")
    
    # Occasion matching
    if style_dna.preferred_occasions and outfit.occasion:
        if outfit.occasion.value in style_dna.preferred_occasions:
            score += 0.2
            match_factors.append("occasion")
            reasons.append(f"perfect for {outfit.occasion.value}")
    
    # Budget matching
    if style_dna.budget_range:
        min_budget = style_dna.budget_range.get("min", 0)
        max_budget = style_dna.budget_range.get("max", 100000)
        if min_budget <= outfit.price <= max_budget:
            score += 0.15
            match_factors.append("budget")
            reasons.append("within your budget")
    
    # Body type recommendations (simplified)
    if outfit.fit_type:
        body_type_fit = _get_body_type_fit_score(style_dna.body_type, outfit.fit_type)
        score += body_type_fit * 0.1
        if body_type_fit > 0.5:
            match_factors.append("body_type")
            reasons.append("flattering for your body type")
    
    # Ensure minimum score
    score = max(0.0, score)
    
    # Create reason string
    if reasons:
        reason = "This outfit " + ", ".join(reasons[:2])  # Limit to top 2 reasons
    else:
        reason = "Recommended based on current trends"
    
    return min(score, 1.0), match_factors, reason

def _get_body_type_fit_score(body_type, fit_type: str) -> float:
    """Get a score for how well a fit type matches a body type"""
    
    fit_recommendations = {
        "pear": {"a_line": 0.9, "flowing": 0.8, "loose": 0.6, "regular": 0.5},
        "apple": {"empire": 0.9, "flowing": 0.8, "loose": 0.7, "regular": 0.6},
        "hourglass": {"fitted": 0.9, "slim": 0.8, "regular": 0.7},
        "rectangle": {"fitted": 0.8, "regular": 0.7, "loose": 0.6},
        "inverted_triangle": {"a_line": 0.9, "loose": 0.8, "regular": 0.6}
    }
    
    if not body_type:
        return 0.5
    
    body_type_key = body_type.value.lower()
    fit_type_key = fit_type.lower()
    
    return fit_recommendations.get(body_type_key, {}).get(fit_type_key, 0.5)

def _serialize_style_dna(style_dna: StyleDNA) -> Dict[str, Any]:
    """Convert StyleDNA object to dictionary for API response"""
    
    return {
        "skin_tone": style_dna.skin_tone.value if style_dna.skin_tone else None,
        "body_type": style_dna.body_type.value if style_dna.body_type else None,
        "preferred_colors": style_dna.preferred_colors,
        "preferred_styles": style_dna.preferred_styles,
        "preferred_occasions": style_dna.preferred_occasions,
        "budget_range": style_dna.budget_range
    }