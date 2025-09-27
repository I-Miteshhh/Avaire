from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import Outfit, CategoryEnum, SubcategoryEnum, OccasionEnum
from routers.auth import get_current_user

router = APIRouter()

# Pydantic models
class OutfitResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    brand: Optional[str]
    category: CategoryEnum
    subcategory: SubcategoryEnum
    occasion: OccasionEnum
    price: float
    discounted_price: Optional[float]
    currency: str
    primary_image_url: str
    additional_images: Optional[List[str]]
    colors: Optional[List[str]]
    sizes: Optional[List[str]]
    material: Optional[str]
    fit_type: Optional[str]
    sleeve_length: Optional[str]
    neckline: Optional[str]
    tags: Optional[List[str]]
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CatalogFilter(BaseModel):
    category: Optional[CategoryEnum] = None
    subcategory: Optional[List[SubcategoryEnum]] = None
    occasion: Optional[List[OccasionEnum]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    colors: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    fit_types: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class CatalogResponse(BaseModel):
    outfits: List[OutfitResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
    filters_applied: Dict[str, Any]

@router.get("/catalog", response_model=CatalogResponse)
async def get_catalog(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[CategoryEnum] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategories (comma-separated)"),
    occasion: Optional[str] = Query(None, description="Filter by occasions (comma-separated)"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
    colors: Optional[str] = Query(None, description="Filter by colors (comma-separated)"),
    sizes: Optional[str] = Query(None, description="Filter by sizes (comma-separated)"),
    brands: Optional[str] = Query(None, description="Filter by brands (comma-separated)"),
    search: Optional[str] = Query(None, description="Search query"),
    sort_by: Optional[str] = Query("created_at", description="Sort by: price_asc, price_desc, created_at, name"),
    db: Session = Depends(get_db)
):
    """Get paginated catalog with filters and search"""
    
    # Build the query
    query = db.query(Outfit).filter(Outfit.is_available == True)
    
    # Apply filters
    filters_applied = {}
    
    if category:
        query = query.filter(Outfit.category == category)
        filters_applied["category"] = category
    
    if subcategory:
        subcategory_list = [SubcategoryEnum(sc.strip()) for sc in subcategory.split(",")]
        query = query.filter(Outfit.subcategory.in_(subcategory_list))
        filters_applied["subcategory"] = subcategory_list
    
    if occasion:
        occasion_list = [OccasionEnum(occ.strip()) for occ in occasion.split(",")]
        query = query.filter(Outfit.occasion.in_(occasion_list))
        filters_applied["occasion"] = occasion_list
    
    if price_min is not None:
        query = query.filter(Outfit.price >= price_min)
        filters_applied["price_min"] = price_min
    
    if price_max is not None:
        query = query.filter(Outfit.price <= price_max)
        filters_applied["price_max"] = price_max
    
    if colors:
        color_list = [color.strip() for color in colors.split(",")]
        # Filter outfits that have at least one of the specified colors
        color_conditions = [Outfit.colors.contains([color]) for color in color_list]
        query = query.filter(or_(*color_conditions))
        filters_applied["colors"] = color_list
    
    if sizes:
        size_list = [size.strip() for size in sizes.split(",")]
        size_conditions = [Outfit.sizes.contains([size]) for size in size_list]
        query = query.filter(or_(*size_conditions))
        filters_applied["sizes"] = size_list
    
    if brands:
        brand_list = [brand.strip() for brand in brands.split(",")]
        query = query.filter(Outfit.brand.in_(brand_list))
        filters_applied["brands"] = brand_list
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Outfit.name.ilike(search_term),
                Outfit.description.ilike(search_term),
                Outfit.brand.ilike(search_term),
                Outfit.tags.astext.ilike(search_term)
            )
        )
        filters_applied["search"] = search
    
    # Apply sorting
    if sort_by == "price_asc":
        query = query.order_by(Outfit.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Outfit.price.desc())
    elif sort_by == "name":
        query = query.order_by(Outfit.name.asc())
    else:  # default: created_at
        query = query.order_by(Outfit.created_at.desc())
    
    filters_applied["sort_by"] = sort_by
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    outfits = query.offset(offset).limit(page_size).all()
    
    # Calculate pagination info
    has_next = offset + page_size < total_count
    has_previous = page > 1
    
    return CatalogResponse(
        outfits=[OutfitResponse.from_orm(outfit) for outfit in outfits],
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=has_next,
        has_previous=has_previous,
        filters_applied=filters_applied
    )

@router.get("/catalog/{outfit_id}", response_model=OutfitResponse)
async def get_outfit_details(
    outfit_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific outfit"""
    
    outfit = db.query(Outfit).filter(
        and_(Outfit.id == outfit_id, Outfit.is_available == True)
    ).first()
    
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    return OutfitResponse.from_orm(outfit)

@router.get("/catalog/filters/options")
async def get_filter_options(db: Session = Depends(get_db)):
    """Get all available filter options for the catalog"""
    
    # Get distinct values for various filters
    distinct_brands = db.query(Outfit.brand).distinct().filter(
        and_(Outfit.brand.isnot(None), Outfit.is_available == True)
    ).all()
    
    distinct_materials = db.query(Outfit.material).distinct().filter(
        and_(Outfit.material.isnot(None), Outfit.is_available == True)
    ).all()
    
    distinct_fit_types = db.query(Outfit.fit_type).distinct().filter(
        and_(Outfit.fit_type.isnot(None), Outfit.is_available == True)
    ).all()
    
    # Get price range
    price_range = db.query(
        db.func.min(Outfit.price).label('min_price'),
        db.func.max(Outfit.price).label('max_price')
    ).filter(Outfit.is_available == True).first()
    
    # Get unique colors and sizes from JSON fields
    all_outfits = db.query(Outfit.colors, Outfit.sizes).filter(Outfit.is_available == True).all()
    
    all_colors = set()
    all_sizes = set()
    
    for outfit in all_outfits:
        if outfit.colors:
            all_colors.update(outfit.colors)
        if outfit.sizes:
            all_sizes.update(outfit.sizes)
    
    return {
        "categories": [category.value for category in CategoryEnum],
        "subcategories": [subcategory.value for subcategory in SubcategoryEnum],
        "occasions": [occasion.value for occasion in OccasionEnum],
        "brands": sorted([brand[0] for brand in distinct_brands if brand[0]]),
        "materials": sorted([material[0] for material in distinct_materials if material[0]]),
        "fit_types": sorted([fit_type[0] for fit_type in distinct_fit_types if fit_type[0]]),
        "colors": sorted(list(all_colors)),
        "sizes": sorted(list(all_sizes)),
        "price_range": {
            "min": float(price_range.min_price) if price_range.min_price else 0,
            "max": float(price_range.max_price) if price_range.max_price else 10000
        }
    }

@router.get("/catalog/trending")
async def get_trending_outfits(
    limit: int = Query(10, ge=1, le=50, description="Number of trending outfits to return"),
    db: Session = Depends(get_db)
):
    """Get trending outfits based on user interactions"""
    
    # For now, return recently added popular items
    # In production, this would use recommendation/interaction data
    trending_outfits = db.query(Outfit).filter(
        Outfit.is_available == True
    ).order_by(
        Outfit.created_at.desc()
    ).limit(limit).all()
    
    return {
        "trending_outfits": [OutfitResponse.from_orm(outfit) for outfit in trending_outfits],
        "generated_at": datetime.utcnow(),
        "algorithm": "recent_popular"  # Placeholder for actual trending algorithm
    }

@router.get("/catalog/categories/{category}")
async def get_category_showcase(
    category: CategoryEnum,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get showcase outfits for a specific category"""
    
    outfits = db.query(Outfit).filter(
        and_(Outfit.category == category, Outfit.is_available == True)
    ).order_by(
        Outfit.created_at.desc()
    ).limit(limit).all()
    
    if not outfits:
        raise HTTPException(status_code=404, detail=f"No outfits found for category: {category}")
    
    # Group by subcategory
    subcategory_groups = {}
    for outfit in outfits:
        if outfit.subcategory.value not in subcategory_groups:
            subcategory_groups[outfit.subcategory.value] = []
        subcategory_groups[outfit.subcategory.value].append(OutfitResponse.from_orm(outfit))
    
    return {
        "category": category,
        "total_outfits": len(outfits),
        "subcategory_groups": subcategory_groups,
        "featured_outfits": [OutfitResponse.from_orm(outfit) for outfit in outfits[:6]]
    }