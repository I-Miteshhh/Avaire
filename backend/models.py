from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class SkinToneEnum(enum.Enum):
    FAIR = "fair"
    LIGHT = "light"
    MEDIUM = "medium"
    OLIVE = "olive"
    BROWN = "brown"
    DARK = "dark"

class BodyTypeEnum(enum.Enum):
    PEAR = "pear"
    APPLE = "apple"
    HOURGLASS = "hourglass"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"

class CategoryEnum(enum.Enum):
    INDIAN_WEAR = "indian_wear"
    WESTERN_WEAR = "western_wear"
    FUSION = "fusion"

class SubcategoryEnum(enum.Enum):
    # Indian Wear
    SAREE = "saree"
    LEHENGA = "lehenga"
    KURTA = "kurta"
    SHARARA = "sharara"
    PALAZZO = "palazzo"
    
    # Western Wear
    DRESS = "dress"
    TOP = "top"
    JEANS = "jeans"
    SKIRT = "skirt"
    COORD_SET = "coord_set"
    BLAZER = "blazer"

class OccasionEnum(enum.Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    PARTY = "party"
    WEDDING = "wedding"
    FESTIVE = "festive"
    DATE_NIGHT = "date_night"
    BRUNCH = "brunch"
    COLLEGE = "college"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    style_dna = relationship("StyleDNA", back_populates="user", uselist=False)
    recommendations = relationship("Recommendation", back_populates="user")
    tryon_history = relationship("TryOnHistory", back_populates="user")

class StyleDNA(Base):
    __tablename__ = "style_dna"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Physical attributes
    skin_tone = Column(Enum(SkinToneEnum), nullable=False)
    body_type = Column(Enum(BodyTypeEnum), nullable=False)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    
    # Size preferences
    bust_size = Column(String)  # XS, S, M, L, XL, XXL
    waist_size = Column(String)
    hip_size = Column(String)
    
    # Style preferences
    preferred_colors = Column(JSON)  # List of color codes/names
    avoided_colors = Column(JSON)
    preferred_styles = Column(JSON)  # List of style tags
    preferred_occasions = Column(JSON)  # List of occasions
    budget_range = Column(JSON)  # {"min": 1000, "max": 5000}
    
    # Lifestyle
    lifestyle = Column(String)  # student, working, homemaker
    age_group = Column(String)  # 18-22, 23-27, 28-35
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="style_dna")

class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    brand = Column(String)
    
    # Categorization
    category = Column(Enum(CategoryEnum), nullable=False)
    subcategory = Column(Enum(SubcategoryEnum), nullable=False)
    occasion = Column(Enum(OccasionEnum), nullable=False)
    
    # Pricing
    price = Column(Float, nullable=False)
    discounted_price = Column(Float)
    currency = Column(String, default="INR")
    
    # Images
    primary_image_url = Column(String, nullable=False)
    additional_images = Column(JSON)  # List of image URLs
    
    # Attributes
    colors = Column(JSON)  # List of available colors
    sizes = Column(JSON)  # List of available sizes
    material = Column(String)
    care_instructions = Column(Text)
    
    # Fit and style
    fit_type = Column(String)  # slim, regular, loose, oversized
    sleeve_length = Column(String)  # sleeveless, short, three_quarter, full
    neckline = Column(String)  # round, v_neck, boat, off_shoulder
    
    # SEO and tags
    tags = Column(JSON)  # Style tags for recommendation engine
    seo_title = Column(String)
    seo_description = Column(Text)
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    recommendations = relationship("Recommendation", back_populates="outfit")
    tryon_history = relationship("TryOnHistory", back_populates="outfit")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    
    # Recommendation metadata
    confidence_score = Column(Float)  # 0-1 score
    recommendation_type = Column(String)  # style_dna, collaborative, trending
    context = Column(String)  # occasion context that triggered recommendation
    
    # User interaction
    was_viewed = Column(Boolean, default=False)
    was_liked = Column(Boolean, default=False)
    was_purchased = Column(Boolean, default=False)
    was_tried_on = Column(Boolean, default=False)
    
    # Feedback
    user_rating = Column(Integer)  # 1-5 star rating
    user_feedback = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    outfit = relationship("Outfit", back_populates="recommendations")

class TryOnHistory(Base):
    __tablename__ = "tryon_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    
    # Try-on session data
    session_id = Column(String, unique=True, nullable=False)
    user_image_url = Column(String, nullable=False)
    result_image_url = Column(String, nullable=False)
    
    # Processing metadata
    processing_time_seconds = Column(Float)
    model_version = Column(String)
    quality_score = Column(Float)  # 0-1 quality score
    
    # User feedback
    user_rating = Column(Integer)  # 1-5 star rating
    user_feedback = Column(Text)
    was_shared = Column(Boolean, default=False)
    was_purchased_after = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tryon_history")
    outfit = relationship("Outfit", back_populates="tryon_history")