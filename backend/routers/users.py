from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import User, StyleDNA, Recommendation, TryOnHistory
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class UserProfile(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: Optional[str]
    phone_number: Optional[str]
    is_verified: bool
    created_at: datetime
    
    # Style DNA info
    has_style_dna: bool
    style_completeness_score: Optional[float] = None
    
    # Activity stats
    total_recommendations: int
    total_tryons: int
    favorite_category: Optional[str] = None

    class Config:
        from_attributes = True

class ProfileStats(BaseModel):
    recommendations: Dict[str, Any]
    tryons: Dict[str, Any]
    engagement: Dict[str, Any]
    personalization: Dict[str, Any]

@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user profile with activity statistics"""
    
    # Users can only access their own profile
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get Style DNA information
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == user_id).first()
    has_style_dna = style_dna is not None
    style_completeness = _calculate_style_completeness(style_dna) if style_dna else 0
    
    # Get activity statistics
    total_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == user_id
    ).count()
    
    total_tryons = db.query(TryOnHistory).filter(
        TryOnHistory.user_id == user_id
    ).count()
    
    # Get favorite category based on most tried-on items
    favorite_category = _get_favorite_category(user_id, db)
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone_number=current_user.phone_number,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        has_style_dna=has_style_dna,
        style_completeness_score=style_completeness,
        total_recommendations=total_recommendations,
        total_tryons=total_tryons,
        favorite_category=favorite_category
    )

@router.get("/{user_id}/stats", response_model=ProfileStats)
async def get_user_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed user statistics and insights"""
    
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Recommendation statistics
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == user_id
    ).all()
    
    total_recommendations = len(recommendations)
    liked_recommendations = len([r for r in recommendations if r.was_liked])
    purchased_recommendations = len([r for r in recommendations if r.was_purchased])
    
    recommendation_stats = {
        "total": total_recommendations,
        "liked": liked_recommendations,
        "purchased": purchased_recommendations,
        "like_rate": (liked_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0,
        "purchase_rate": (purchased_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0
    }
    
    # Try-on statistics
    tryons = db.query(TryOnHistory).filter(
        TryOnHistory.user_id == user_id
    ).all()
    
    total_tryons = len(tryons)
    shared_tryons = len([t for t in tryons if t.was_shared])
    purchased_after_tryon = len([t for t in tryons if t.was_purchased_after])
    avg_rating = sum([t.user_rating for t in tryons if t.user_rating]) / len([t for t in tryons if t.user_rating]) if tryons else 0
    
    tryon_stats = {
        "total": total_tryons,
        "shared": shared_tryons,
        "purchased_after": purchased_after_tryon,
        "sharing_rate": (shared_tryons / total_tryons * 100) if total_tryons > 0 else 0,
        "conversion_rate": (purchased_after_tryon / total_tryons * 100) if total_tryons > 0 else 0,
        "average_rating": round(avg_rating, 1)
    }
    
    # Engagement statistics
    total_interactions = total_recommendations + total_tryons
    positive_interactions = liked_recommendations + shared_tryons
    
    engagement_stats = {
        "total_interactions": total_interactions,
        "positive_interactions": positive_interactions,
        "engagement_score": (positive_interactions / total_interactions * 100) if total_interactions > 0 else 0,
        "days_active": _calculate_days_active(user_id, db),
        "last_activity": _get_last_activity_date(user_id, db)
    }
    
    # Personalization statistics
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == user_id).first()
    personalization_stats = {
        "style_dna_completeness": _calculate_style_completeness(style_dna) if style_dna else 0,
        "recommendation_accuracy": recommendation_stats["like_rate"],
        "personalization_level": _get_personalization_level(style_dna, recommendation_stats["like_rate"]),
        "data_points_collected": _count_data_points(user_id, db)
    }
    
    return ProfileStats(
        recommendations=recommendation_stats,
        tryons=tryon_stats,
        engagement=engagement_stats,
        personalization=personalization_stats
    )

@router.get("/{user_id}/activity")
async def get_user_activity_timeline(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's activity timeline"""
    
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get recent recommendations
    recent_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == user_id
    ).order_by(Recommendation.created_at.desc()).limit(limit // 2).all()
    
    # Get recent try-ons
    recent_tryons = db.query(TryOnHistory).filter(
        TryOnHistory.user_id == user_id
    ).order_by(TryOnHistory.created_at.desc()).limit(limit // 2).all()
    
    # Combine and sort activities
    activities = []
    
    for rec in recent_recommendations:
        activities.append({
            "type": "recommendation",
            "id": rec.id,
            "outfit_id": rec.outfit_id,
            "confidence_score": rec.confidence_score,
            "was_liked": rec.was_liked,
            "was_viewed": rec.was_viewed,
            "created_at": rec.created_at,
            "context": rec.context
        })
    
    for tryon in recent_tryons:
        activities.append({
            "type": "tryon",
            "id": tryon.id,
            "session_id": tryon.session_id,
            "outfit_id": tryon.outfit_id,
            "quality_score": tryon.quality_score,
            "user_rating": tryon.user_rating,
            "was_shared": tryon.was_shared,
            "created_at": tryon.created_at
        })
    
    # Sort by creation date
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "activities": activities[:limit],
        "total_count": len(activities)
    }

@router.put("/{user_id}/profile")
async def update_user_profile(
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone_number: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile information"""
    
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if phone_number is not None:
        user.phone_number = phone_number
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Profile updated successfully"}

@router.get("/{user_id}/insights")
async def get_user_insights(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized insights and recommendations for improving user experience"""
    
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == user_id).first()
    
    # Get user statistics
    total_recommendations = db.query(Recommendation).filter(Recommendation.user_id == user_id).count()
    liked_recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == user_id, Recommendation.was_liked == True
    ).count()
    
    total_tryons = db.query(TryOnHistory).filter(TryOnHistory.user_id == user_id).count()
    
    insights = []
    
    # Style DNA completeness insight
    if not style_dna:
        insights.append({
            "type": "style_dna_missing",
            "priority": "high",
            "title": "Complete your Style DNA",
            "description": "Complete your style profile to get better personalized recommendations",
            "action": "Complete Style DNA onboarding",
            "potential_improvement": "Up to 70% better recommendations"
        })
    elif _calculate_style_completeness(style_dna) < 80:
        insights.append({
            "type": "style_dna_incomplete",
            "priority": "medium",
            "title": "Improve your Style DNA",
            "description": "Adding more details to your style profile will improve recommendations",
            "action": "Update Style DNA with missing information",
            "potential_improvement": f"{100 - _calculate_style_completeness(style_dna):.0f}% more personalization"
        })
    
    # Recommendation engagement insight
    if total_recommendations > 10:
        like_rate = (liked_recommendations / total_recommendations) * 100
        if like_rate < 50:
            insights.append({
                "type": "low_engagement",
                "priority": "medium",
                "title": "Let us know your preferences",
                "description": "Your feedback helps us learn your style better",
                "action": "Rate more recommendations to improve accuracy",
                "potential_improvement": "Better recommendation accuracy"
            })
    
    # Try-on encouragement
    if total_tryons < 3:
        insights.append({
            "type": "try_virtual_tryon",
            "priority": "low",
            "title": "Try our Virtual Try-On",
            "description": "See how outfits look on you before deciding",
            "action": "Upload a photo and try on some outfits",
            "potential_improvement": "Better purchase confidence"
        })
    
    # Personalization score
    personalization_score = _calculate_overall_personalization_score(user_id, db)
    
    return {
        "personalization_score": personalization_score,
        "insights": insights,
        "next_steps": _get_next_steps(user_id, style_dna, db),
        "achievements": _get_user_achievements(user_id, db)
    }

# Helper functions
def _calculate_style_completeness(style_dna: Optional[StyleDNA]) -> float:
    """Calculate how complete the Style DNA profile is"""
    if not style_dna:
        return 0.0
    
    total_fields = 13
    filled_fields = sum([
        1 if style_dna.skin_tone else 0,
        1 if style_dna.body_type else 0,
        1 if style_dna.height_cm else 0,
        1 if style_dna.weight_kg else 0,
        1 if style_dna.bust_size else 0,
        1 if style_dna.waist_size else 0,
        1 if style_dna.hip_size else 0,
        1 if style_dna.preferred_colors else 0,
        1 if style_dna.avoided_colors else 0,
        1 if style_dna.preferred_styles else 0,
        1 if style_dna.preferred_occasions else 0,
        1 if style_dna.lifestyle else 0,
        1 if style_dna.age_group else 0
    ])
    
    return (filled_fields / total_fields) * 100

def _get_favorite_category(user_id: int, db: Session) -> Optional[str]:
    """Get user's favorite category based on try-on history"""
    from sqlalchemy import func
    from models import Outfit
    
    result = db.query(
        Outfit.category,
        func.count(TryOnHistory.id).label('count')
    ).join(
        TryOnHistory, Outfit.id == TryOnHistory.outfit_id
    ).filter(
        TryOnHistory.user_id == user_id
    ).group_by(
        Outfit.category
    ).order_by(
        func.count(TryOnHistory.id).desc()
    ).first()
    
    return result[0].value if result else None

def _calculate_days_active(user_id: int, db: Session) -> int:
    """Calculate number of days user has been active"""
    from sqlalchemy import func
    
    # Get distinct dates of activity
    recommendation_dates = db.query(
        func.date(Recommendation.created_at)
    ).filter(Recommendation.user_id == user_id).distinct().all()
    
    tryon_dates = db.query(
        func.date(TryOnHistory.created_at)
    ).filter(TryOnHistory.user_id == user_id).distinct().all()
    
    all_dates = set([date[0] for date in recommendation_dates + tryon_dates])
    return len(all_dates)

def _get_last_activity_date(user_id: int, db: Session) -> Optional[datetime]:
    """Get user's last activity date"""
    last_rec = db.query(Recommendation.created_at).filter(
        Recommendation.user_id == user_id
    ).order_by(Recommendation.created_at.desc()).first()
    
    last_tryon = db.query(TryOnHistory.created_at).filter(
        TryOnHistory.user_id == user_id
    ).order_by(TryOnHistory.created_at.desc()).first()
    
    dates = [date[0] for date in [last_rec, last_tryon] if date]
    return max(dates) if dates else None

def _get_personalization_level(style_dna: Optional[StyleDNA], recommendation_accuracy: float) -> str:
    """Determine user's personalization level"""
    if not style_dna:
        return "basic"
    
    completeness = _calculate_style_completeness(style_dna)
    
    if completeness > 80 and recommendation_accuracy > 70:
        return "advanced"
    elif completeness > 50 and recommendation_accuracy > 50:
        return "intermediate"
    else:
        return "basic"

def _count_data_points(user_id: int, db: Session) -> int:
    """Count total data points collected for user"""
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == user_id).first()
    recommendations = db.query(Recommendation).filter(Recommendation.user_id == user_id).count()
    tryons = db.query(TryOnHistory).filter(TryOnHistory.user_id == user_id).count()
    
    style_points = _calculate_style_completeness(style_dna) / 100 * 13 if style_dna else 0
    interaction_points = recommendations + tryons
    
    return int(style_points + interaction_points)

def _calculate_overall_personalization_score(user_id: int, db: Session) -> float:
    """Calculate overall personalization score"""
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == user_id).first()
    
    # Style DNA completeness (40% weight)
    style_score = _calculate_style_completeness(style_dna) if style_dna else 0
    
    # Recommendation feedback (40% weight)
    recommendations = db.query(Recommendation).filter(Recommendation.user_id == user_id).all()
    if recommendations:
        liked = len([r for r in recommendations if r.was_liked])
        feedback_score = (liked / len(recommendations)) * 100
    else:
        feedback_score = 0
    
    # Activity level (20% weight)
    total_interactions = len(recommendations) + db.query(TryOnHistory).filter(TryOnHistory.user_id == user_id).count()
    activity_score = min(total_interactions * 2, 100)  # Cap at 100
    
    overall_score = (style_score * 0.4) + (feedback_score * 0.4) + (activity_score * 0.2)
    return round(overall_score, 1)

def _get_next_steps(user_id: int, style_dna: Optional[StyleDNA], db: Session) -> List[str]:
    """Get recommended next steps for user"""
    steps = []
    
    if not style_dna:
        steps.append("Complete your Style DNA profile")
    elif _calculate_style_completeness(style_dna) < 80:
        steps.append("Fill in missing Style DNA details")
    
    tryon_count = db.query(TryOnHistory).filter(TryOnHistory.user_id == user_id).count()
    if tryon_count < 5:
        steps.append("Try on more outfits virtually")
    
    recommendation_feedback = db.query(Recommendation).filter(
        Recommendation.user_id == user_id,
        Recommendation.was_liked.isnot(None)
    ).count()
    
    if recommendation_feedback < 10:
        steps.append("Provide feedback on more recommendations")
    
    return steps

def _get_user_achievements(user_id: int, db: Session) -> List[Dict[str, Any]]:
    """Get user achievements/badges"""
    achievements = []
    
    # Style DNA completion
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == user_id).first()
    if style_dna and _calculate_style_completeness(style_dna) >= 100:
        achievements.append({
            "name": "Style Expert",
            "description": "Completed full Style DNA profile",
            "icon": "🎯",
            "earned_at": style_dna.created_at
        })
    
    # Try-on achievements
    tryon_count = db.query(TryOnHistory).filter(TryOnHistory.user_id == user_id).count()
    if tryon_count >= 10:
        achievements.append({
            "name": "Virtual Fashion Explorer",
            "description": "Tried on 10+ outfits virtually",
            "icon": "👗",
            "earned_at": None  # Would need to track when milestone was reached
        })
    
    # Recommendation feedback
    feedback_count = db.query(Recommendation).filter(
        Recommendation.user_id == user_id,
        Recommendation.was_liked.isnot(None)
    ).count()
    
    if feedback_count >= 50:
        achievements.append({
            "name": "Style Curator",
            "description": "Provided feedback on 50+ recommendations",
            "icon": "⭐",
            "earned_at": None
        })
    
    return achievements