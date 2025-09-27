from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import os

from database import get_db
from models import User, Outfit, TryOnHistory
from routers.auth import get_current_user
from ml.pipeline import MLPipeline
from services import get_storage_client

router = APIRouter()

# Initialize ML Pipeline and Storage client
ml_pipeline = MLPipeline()
storage_client = get_storage_client()

# Pydantic models
class TryOnRequest(BaseModel):
    outfit_id: int
    user_image_base64: Optional[str] = None

class TryOnResponse(BaseModel):
    session_id: str
    result_image_url: str
    processing_time_seconds: float
    quality_score: float
    outfit_id: int
    outfit_name: str
    created_at: datetime

class TryOnFeedback(BaseModel):
    session_id: str
    user_rating: Optional[int] = None  # 1-5
    user_feedback: Optional[str] = None
    was_shared: Optional[bool] = None
    was_purchased_after: Optional[bool] = None

@router.post("/tryon", response_model=TryOnResponse)
async def virtual_tryon(
    outfit_id: int = Form(...),
    user_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform virtual try-on with user image and selected outfit"""
    
    start_time = datetime.utcnow()
    
    # Validate outfit exists
    outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Validate image file
    if not user_image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    try:
        # Save uploaded user image through storage client
        upload_key = f"uploads/users/{current_user.id}/{session_id}_original.jpg"
        stored_upload = await storage_client.save_upload(user_image, upload_key)
        user_image_path = str(stored_upload.local_path)

        # Resolve garment image path relative to storage root
        if outfit.primary_image_url.startswith("http"):
            garment_image_path = outfit.primary_image_url
        else:
            garment_path = storage_client.resolve_local_path(outfit.primary_image_url)
            if not garment_path.exists():
                raise HTTPException(status_code=404, detail="Garment asset not found on storage")
            garment_image_path = str(garment_path)

        # Prepare result path
        result_key = f"results/{current_user.id}/{session_id}_result.jpg"
        storage_client.ensure_directory(os.path.dirname(result_key))
        result_local_path = storage_client.resolve_local_path(result_key)

        # Run virtual try-on pipeline
        ml_result = await ml_pipeline.virtual_tryon(
            user_image_path=user_image_path,
            garment_image_path=garment_image_path,
            output_path=str(result_local_path),
            session_id=session_id
        )

        if not ml_result.get("success", True):
            raise HTTPException(status_code=500, detail="Virtual try-on processing failed")
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Save to database
        # Sync result asset for public serving
        try:
            stored_result = storage_client.sync(result_key, content_type="image/jpeg")
        except FileNotFoundError as exc:
            raise HTTPException(status_code=500, detail=f"Result asset unavailable: {exc}") from exc

        tryon_record = TryOnHistory(
            user_id=current_user.id,
            outfit_id=outfit_id,
            session_id=session_id,
            user_image_url=stored_upload.url,
            result_image_url=stored_result.url,
            processing_time_seconds=processing_time,
            model_version=ml_result.get("model_version", "v1.0"),
            quality_score=ml_result.get("quality_score", 0.8)
        )
        
        db.add(tryon_record)
        db.commit()
        db.refresh(tryon_record)
        
        return TryOnResponse(
            session_id=session_id,
            result_image_url=stored_result.url,
            processing_time_seconds=processing_time,
            quality_score=ml_result.get("quality_score", 0.8),
            outfit_id=outfit_id,
            outfit_name=outfit.name,
            created_at=tryon_record.created_at
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Virtual try-on processing failed: {str(e)}")

@router.post("/tryon/feedback")
async def submit_tryon_feedback(
    feedback: TryOnFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for a virtual try-on session"""
    
    # Find the try-on record
    tryon_record = db.query(TryOnHistory).filter(
        TryOnHistory.session_id == feedback.session_id,
        TryOnHistory.user_id == current_user.id
    ).first()
    
    if not tryon_record:
        raise HTTPException(status_code=404, detail="Try-on session not found")
    
    # Update feedback
    if feedback.user_rating is not None:
        tryon_record.user_rating = feedback.user_rating
    if feedback.user_feedback is not None:
        tryon_record.user_feedback = feedback.user_feedback
    if feedback.was_shared is not None:
        tryon_record.was_shared = feedback.was_shared
    if feedback.was_purchased_after is not None:
        tryon_record.was_purchased_after = feedback.was_purchased_after
    
    db.commit()
    
    return {"message": "Feedback submitted successfully"}

@router.get("/tryon/history")
async def get_tryon_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's virtual try-on history"""
    
    tryon_history = db.query(TryOnHistory).filter(
        TryOnHistory.user_id == current_user.id
    ).order_by(
        TryOnHistory.created_at.desc()
    ).limit(limit).all()
    
    history_data = []
    for record in tryon_history:
        outfit = db.query(Outfit).filter(Outfit.id == record.outfit_id).first()
        
        history_data.append({
            "session_id": record.session_id,
            "result_image_url": record.result_image_url,
            "processing_time_seconds": record.processing_time_seconds,
            "quality_score": record.quality_score,
            "user_rating": record.user_rating,
            "was_shared": record.was_shared,
            "was_purchased_after": record.was_purchased_after,
            "created_at": record.created_at,
            "outfit": {
                "id": outfit.id,
                "name": outfit.name,
                "brand": outfit.brand,
                "price": outfit.price,
                "primary_image_url": outfit.primary_image_url
            } if outfit else None
        })
    
    return {
        "tryon_history": history_data,
        "total_sessions": len(history_data)
    }

@router.get("/tryon/session/{session_id}")
async def get_tryon_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific try-on session"""
    
    tryon_record = db.query(TryOnHistory).filter(
        TryOnHistory.session_id == session_id,
        TryOnHistory.user_id == current_user.id
    ).first()
    
    if not tryon_record:
        raise HTTPException(status_code=404, detail="Try-on session not found")
    
    outfit = db.query(Outfit).filter(Outfit.id == tryon_record.outfit_id).first()
    
    return {
        "session_id": tryon_record.session_id,
        "user_image_url": tryon_record.user_image_url,
        "result_image_url": tryon_record.result_image_url,
        "processing_time_seconds": tryon_record.processing_time_seconds,
        "quality_score": tryon_record.quality_score,
        "model_version": tryon_record.model_version,
        "user_rating": tryon_record.user_rating,
        "user_feedback": tryon_record.user_feedback,
        "was_shared": tryon_record.was_shared,
        "was_purchased_after": tryon_record.was_purchased_after,
        "created_at": tryon_record.created_at,
        "outfit": {
            "id": outfit.id,
            "name": outfit.name,
            "description": outfit.description,
            "brand": outfit.brand,
            "category": outfit.category.value,
            "subcategory": outfit.subcategory.value,
            "price": outfit.price,
            "primary_image_url": outfit.primary_image_url,
            "colors": outfit.colors,
            "sizes": outfit.sizes
        } if outfit else None
    }

@router.delete("/tryon/session/{session_id}")
async def delete_tryon_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a try-on session and its associated files"""
    
    tryon_record = db.query(TryOnHistory).filter(
        TryOnHistory.session_id == session_id,
        TryOnHistory.user_id == current_user.id
    ).first()
    
    if not tryon_record:
        raise HTTPException(status_code=404, detail="Try-on session not found")
    
    try:
        # Delete associated files
        if os.path.exists(tryon_record.user_image_url):
            os.remove(tryon_record.user_image_url)
        if os.path.exists(tryon_record.result_image_url):
            os.remove(tryon_record.result_image_url)
        
        # Delete database record
        db.delete(tryon_record)
        db.commit()
        
        return {"message": "Try-on session deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@router.get("/tryon/stats")
async def get_tryon_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's virtual try-on statistics and insights"""
    
    # Total try-on sessions
    total_sessions = db.query(TryOnHistory).filter(
        TryOnHistory.user_id == current_user.id
    ).count()
    
    if total_sessions == 0:
        return {
            "total_sessions": 0,
            "average_quality_score": 0,
            "favorite_categories": [],
            "sharing_rate": 0,
            "purchase_rate": 0
        }
    
    # Get all records for analysis
    all_records = db.query(TryOnHistory).filter(
        TryOnHistory.user_id == current_user.id
    ).all()
    
    # Calculate statistics
    quality_scores = [r.quality_score for r in all_records if r.quality_score]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    shared_count = len([r for r in all_records if r.was_shared])
    purchased_count = len([r for r in all_records if r.was_purchased_after])
    
    sharing_rate = (shared_count / total_sessions) * 100
    purchase_rate = (purchased_count / total_sessions) * 100
    
    # Get favorite categories (most tried-on)
    outfit_ids = [r.outfit_id for r in all_records]
    outfits = db.query(Outfit).filter(Outfit.id.in_(outfit_ids)).all()
    
    category_counts = {}
    for outfit in outfits:
        category = outfit.category.value
        category_counts[category] = category_counts.get(category, 0) + 1
    
    favorite_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "total_sessions": total_sessions,
        "average_quality_score": round(avg_quality, 2),
        "favorite_categories": [{"category": cat, "count": count} for cat, count in favorite_categories],
        "sharing_rate": round(sharing_rate, 1),
        "purchase_rate": round(purchase_rate, 1),
        "engagement_level": "high" if sharing_rate > 20 else "medium" if sharing_rate > 10 else "low"
    }