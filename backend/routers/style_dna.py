from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import User, StyleDNA, SkinToneEnum, BodyTypeEnum
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class StyleDNACreate(BaseModel):
    skin_tone: SkinToneEnum
    body_type: BodyTypeEnum
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bust_size: Optional[str] = None
    waist_size: Optional[str] = None
    hip_size: Optional[str] = None
    preferred_colors: Optional[List[str]] = []
    avoided_colors: Optional[List[str]] = []
    preferred_styles: Optional[List[str]] = []
    preferred_occasions: Optional[List[str]] = []
    budget_range: Optional[Dict[str, float]] = {"min": 1000, "max": 5000}
    lifestyle: Optional[str] = None
    age_group: Optional[str] = None

class StyleDNAUpdate(BaseModel):
    skin_tone: Optional[SkinToneEnum] = None
    body_type: Optional[BodyTypeEnum] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bust_size: Optional[str] = None
    waist_size: Optional[str] = None
    hip_size: Optional[str] = None
    preferred_colors: Optional[List[str]] = None
    avoided_colors: Optional[List[str]] = None
    preferred_styles: Optional[List[str]] = None
    preferred_occasions: Optional[List[str]] = None
    budget_range: Optional[Dict[str, float]] = None
    lifestyle: Optional[str] = None
    age_group: Optional[str] = None

class StyleDNAResponse(BaseModel):
    id: int
    user_id: int
    skin_tone: SkinToneEnum
    body_type: BodyTypeEnum
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bust_size: Optional[str]
    waist_size: Optional[str]
    hip_size: Optional[str]
    preferred_colors: Optional[List[str]]
    avoided_colors: Optional[List[str]]
    preferred_styles: Optional[List[str]]
    preferred_occasions: Optional[List[str]]
    budget_range: Optional[Dict[str, float]]
    lifestyle: Optional[str]
    age_group: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/onboard_style_dna", response_model=StyleDNAResponse)
async def create_style_dna(
    style_dna: StyleDNACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update user's Style DNA profile"""
    
    # Check if user already has a Style DNA profile
    existing_style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == current_user.id).first()
    
    if existing_style_dna:
        # Update existing profile
        for field, value in style_dna.dict(exclude_unset=True).items():
            setattr(existing_style_dna, field, value)
        db.commit()
        db.refresh(existing_style_dna)
        return StyleDNAResponse.from_orm(existing_style_dna)
    
    else:
        # Create new profile
        db_style_dna = StyleDNA(
            user_id=current_user.id,
            **style_dna.dict()
        )
        db.add(db_style_dna)
        db.commit()
        db.refresh(db_style_dna)
        return StyleDNAResponse.from_orm(db_style_dna)

@router.get("/style_dna", response_model=StyleDNAResponse)
async def get_style_dna(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's Style DNA profile"""
    
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == current_user.id).first()
    
    if not style_dna:
        raise HTTPException(status_code=404, detail="Style DNA profile not found")
    
    return StyleDNAResponse.from_orm(style_dna)

@router.put("/style_dna", response_model=StyleDNAResponse)
async def update_style_dna(
    style_dna_update: StyleDNAUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's Style DNA profile"""
    
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == current_user.id).first()
    
    if not style_dna:
        raise HTTPException(status_code=404, detail="Style DNA profile not found")
    
    # Update only provided fields
    update_data = style_dna_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(style_dna, field, value)
    
    db.commit()
    db.refresh(style_dna)
    
    return StyleDNAResponse.from_orm(style_dna)

@router.get("/style_dna/recommendations/preview")
async def get_style_recommendations_preview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a preview of how Style DNA affects recommendations"""
    
    style_dna = db.query(StyleDNA).filter(StyleDNA.user_id == current_user.id).first()
    
    if not style_dna:
        raise HTTPException(status_code=404, detail="Style DNA profile not found")
    
    # Generate recommendation insights based on Style DNA
    insights = {
        "skin_tone_recommendations": _get_skin_tone_recommendations(style_dna.skin_tone),
        "body_type_recommendations": _get_body_type_recommendations(style_dna.body_type),
        "color_palette": style_dna.preferred_colors or [],
        "style_tags": style_dna.preferred_styles or [],
        "occasion_focus": style_dna.preferred_occasions or [],
        "budget_range": style_dna.budget_range or {"min": 1000, "max": 5000}
    }
    
    return {
        "user_style_dna": StyleDNAResponse.from_orm(style_dna),
        "recommendation_insights": insights,
        "personalization_score": _calculate_personalization_score(style_dna)
    }

# Helper functions
def _get_skin_tone_recommendations(skin_tone: SkinToneEnum) -> Dict[str, Any]:
    """Get color and style recommendations based on skin tone"""
    recommendations = {
        SkinToneEnum.FAIR: {
            "best_colors": ["pastel_pink", "lavender", "mint_green", "baby_blue", "cream"],
            "avoid_colors": ["very_bright_colors", "neon"],
            "styling_tips": "Soft, muted colors complement fair skin beautifully"
        },
        SkinToneEnum.LIGHT: {
            "best_colors": ["coral", "peach", "light_yellow", "soft_green", "dusty_rose"],
            "avoid_colors": ["very_dark_colors"],
            "styling_tips": "Light, warm tones enhance your natural glow"
        },
        SkinToneEnum.MEDIUM: {
            "best_colors": ["jewel_tones", "emerald", "royal_blue", "rich_purple", "golden_yellow"],
            "avoid_colors": ["washed_out_pastels"],
            "styling_tips": "Rich, vibrant colors make you shine"
        },
        SkinToneEnum.OLIVE: {
            "best_colors": ["earth_tones", "olive_green", "warm_brown", "terracotta", "burgundy"],
            "avoid_colors": ["cool_pinks", "icy_blues"],
            "styling_tips": "Earthy, warm colors complement olive undertones"
        },
        SkinToneEnum.BROWN: {
            "best_colors": ["bright_colors", "orange", "red", "bright_blue", "fuchsia"],
            "avoid_colors": ["muddy_colors"],
            "styling_tips": "Bold, bright colors create stunning contrast"
        },
        SkinToneEnum.DARK: {
            "best_colors": ["vibrant_colors", "electric_blue", "hot_pink", "bright_yellow", "white"],
            "avoid_colors": ["very_dark_colors"],
            "styling_tips": "Vibrant colors and high contrast look amazing"
        }
    }
    return recommendations.get(skin_tone, {})

def _get_body_type_recommendations(body_type: BodyTypeEnum) -> Dict[str, Any]:
    """Get styling recommendations based on body type"""
    recommendations = {
        BodyTypeEnum.PEAR: {
            "flattering_styles": ["A_line_dresses", "boat_neck", "statement_sleeves", "wide_leg_pants"],
            "avoid_styles": ["tight_bottoms", "skinny_jeans"],
            "styling_tips": "Highlight your upper body with interesting necklines and sleeves"
        },
        BodyTypeEnum.APPLE: {
            "flattering_styles": ["empire_waist", "V_neck", "flowing_tops", "straight_leg_pants"],
            "avoid_styles": ["tight_around_waist", "horizontal_stripes"],
            "styling_tips": "Create a defined waistline and elongate your torso"
        },
        BodyTypeEnum.HOURGLASS: {
            "flattering_styles": ["wrap_dresses", "fitted_tops", "high_waisted_bottoms", "belted_outfits"],
            "avoid_styles": ["boxy_fits", "shapeless_clothing"],
            "styling_tips": "Show off your natural waistline with fitted styles"
        },
        BodyTypeEnum.RECTANGLE: {
            "flattering_styles": ["peplum_tops", "ruffles", "belts", "layered_looks"],
            "avoid_styles": ["straight_cuts"],
            "styling_tips": "Create curves with strategic details and layering"
        },
        BodyTypeEnum.INVERTED_TRIANGLE: {
            "flattering_styles": ["wide_leg_pants", "A_line_skirts", "straight_necklines", "bottom_details"],
            "avoid_styles": ["shoulder_pads", "boat_necks"],
            "styling_tips": "Balance your silhouette by adding volume to your lower body"
        }
    }
    return recommendations.get(body_type, {})

def _calculate_personalization_score(style_dna: StyleDNA) -> float:
    """Calculate how complete the Style DNA profile is (0-100)"""
    total_fields = 13  # Total number of Style DNA fields
    filled_fields = 0
    
    if style_dna.skin_tone: filled_fields += 1
    if style_dna.body_type: filled_fields += 1
    if style_dna.height_cm: filled_fields += 1
    if style_dna.weight_kg: filled_fields += 1
    if style_dna.bust_size: filled_fields += 1
    if style_dna.waist_size: filled_fields += 1
    if style_dna.hip_size: filled_fields += 1
    if style_dna.preferred_colors: filled_fields += 1
    if style_dna.avoided_colors: filled_fields += 1
    if style_dna.preferred_styles: filled_fields += 1
    if style_dna.preferred_occasions: filled_fields += 1
    if style_dna.lifestyle: filled_fields += 1
    if style_dna.age_group: filled_fields += 1
    
    return round((filled_fields / total_fields) * 100, 1)