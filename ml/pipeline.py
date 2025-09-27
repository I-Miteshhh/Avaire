import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .preprocessing import ImagePreprocessor
from .tryon import VirtualTryOnEngine
from .recommendation import RecommendationEngine

logger = logging.getLogger(__name__)


class MLPipeline:
    """Main ML Pipeline orchestrator for Avaire Fashion AI Platform."""

    def __init__(self, device: Optional[str] = None) -> None:
        """Initialize ML Pipeline with all required components."""

        self.device = device or self._detect_device()
        logger.info("Initializing Avaire ML Pipeline on device: %s", self.device)

        try:
            self.preprocessor = ImagePreprocessor(device=self.device)
            self.tryon_engine = VirtualTryOnEngine(device=self.device)
            self.recommendation_engine = RecommendationEngine()

            self.is_initialized = True
            logger.info("ML Pipeline initialized successfully")

            if os.getenv("ML_PIPELINE_AUTOWARM", "false").lower() == "true":
                self.warmup()

        except Exception as exc:
            logger.exception("Failed to initialize ML Pipeline")
            self.is_initialized = False
            raise

    @staticmethod
    def _detect_device() -> str:
        """Detect the best available compute device."""

        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
            if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
                return "mps"
        except Exception:  # pragma: no cover - optional dependency
            pass
        return "cpu"
    
    async def virtual_tryon(
        self,
        user_image_path: str,
        garment_image_path: str,
        output_path: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform virtual try-on processing
        
        Args:
            user_image_path: Path to user's photo
            garment_image_path: Path to garment image
            output_path: Path to save result
            session_id: Unique session identifier
            
        Returns:
            Dict containing result metadata
        """
        if not self.is_initialized:
            raise RuntimeError("ML Pipeline not properly initialized")
        
        metadata = metadata or {}

        try:
            start_time = datetime.utcnow()
            logger.info(f"Starting virtual try-on for session {session_id}")
            
            # Step 1: Preprocess user image
            logger.info("Preprocessing user image...")
            preprocessed_user, preprocessed_garment = await asyncio.gather(
                self.preprocessor.preprocess_user_image(user_image_path, session_id=session_id),
                self.preprocessor.preprocess_garment_image(garment_image_path, session_id=session_id),
            )

            # Step 2: Perform virtual try-on
            logger.info("Performing virtual try-on...")
            warp_result = await self.tryon_engine.perform_warp(
                user_data=preprocessed_user,
                garment_data=preprocessed_garment,
                metadata=metadata,
            )

            compose_result = await self.tryon_engine.compose_result(
                warp_result,
                output_path=output_path,
            )
            
            # Step 4: Calculate processing metrics
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            result_metadata = {
                "session_id": session_id,
                "processing_time_seconds": processing_time,
                "model_version": self.tryon_engine.model_version,
                "quality_score": compose_result.get("quality_score", 0.8),
                "preprocessing_stats": {
                    "user_image_processed": preprocessed_user is not None,
                    "garment_image_processed": preprocessed_garment is not None,
                },
                "output_path": output_path,
                "success": True
            }
            
            logger.info(f"Virtual try-on completed for session {session_id} in {processing_time:.2f}s")
            return result_metadata
            
        except Exception as e:
            logger.error(f"Virtual try-on failed for session {session_id}: {str(e)}")
            return {
                "session_id": session_id,
                "success": False,
                "error": str(e),
                "model_version": getattr(self.tryon_engine, 'model_version', 'unknown'),
                "quality_score": 0.0
            }
    
    async def generate_recommendations(
        self,
        user_style_dna: Dict[str, Any],
        context: Optional[str] = None,
        limit: int = 10,
        catalog_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate personalized recommendations
        
        Args:
            user_style_dna: User's style DNA profile
            context: Context for recommendations (occasion, mood, etc.)
            limit: Number of recommendations to generate
            catalog_items: Available catalog items to recommend from
            
        Returns:
            Dict containing recommendations and metadata
        """
        try:
            logger.info(f"Generating {limit} recommendations for user with context: {context}")
            
            recommendations = await self.recommendation_engine.generate_recommendations(
                style_dna=user_style_dna,
                context=context,
                limit=limit,
                catalog_items=catalog_items,
            )
            
            return {
                "recommendations": recommendations,
                "algorithm_version": self.recommendation_engine.version,
                "context_used": context,
                "personalization_score": self._calculate_personalization_score(user_style_dna),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return {
                "recommendations": [],
                "error": str(e),
                "algorithm_version": getattr(self.recommendation_engine, 'version', 'unknown')
            }
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image for various attributes (colors, style, etc.)
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict containing image analysis results
        """
        try:
            logger.info(f"Analyzing image: {image_path}")
            
            analysis = await self.preprocessor.analyze_image(image_path)
            
            return {
                "success": True,
                "analysis": analysis,
                "model_version": self.preprocessor.version
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current status of ML Pipeline components"""
        return {
            "pipeline_initialized": self.is_initialized,
            "device": self.device,
            "components": {
                "preprocessor": {
                    "initialized": hasattr(self, "preprocessor"),
                    "version": getattr(self.preprocessor, "version", "unknown") if hasattr(self, "preprocessor") else None,
                },
                "tryon_engine": {
                    "initialized": hasattr(self, "tryon_engine"),
                    "model_version": getattr(self.tryon_engine, "model_version", "unknown") if hasattr(self, "tryon_engine") else None,
                },
                "recommendation_engine": {
                    "initialized": hasattr(self, "recommendation_engine"),
                    "version": getattr(self.recommendation_engine, "version", "unknown") if hasattr(self, "recommendation_engine") else None,
                },
            },
        }
    
    def _calculate_personalization_score(self, style_dna: Dict[str, Any]) -> float:
        """Calculate personalization score based on Style DNA completeness"""
        if not style_dna:
            return 0.0
        
        # Count filled fields
        total_fields = 10  # Expected number of Style DNA fields
        filled_fields = 0
        
        key_fields = [
            'skin_tone', 'body_type', 'preferred_colors', 'preferred_styles',
            'preferred_occasions', 'budget_range', 'lifestyle', 'age_group',
            'height_cm', 'weight_kg'
        ]
        
        for field in key_fields:
            if style_dna.get(field) is not None:
                filled_fields += 1
        
        return (filled_fields / total_fields) * 100
    
    async def cleanup_temp_files(self, session_id: str) -> None:
        """Clean up temporary files for a session."""

        try:
            if hasattr(self, "preprocessor"):
                await self.preprocessor.cleanup_temp_files(session_id)
            logger.info(f"Cleaned up temp files for session {session_id}")
        except Exception as exc:
            logger.warning("Failed to cleanup temp files for session %s: %s", session_id, exc)

    def warmup(self) -> None:
        """Warm up heavy models so first request is fast."""

        logger.info("Warming up ML pipeline components")
        if hasattr(self, "tryon_engine"):
            self.tryon_engine.warmup()
        if hasattr(self, "recommendation_engine"):
            self.recommendation_engine.warmup()

    def shutdown(self) -> None:
        """Release compute resources gracefully."""

        logger.info("Shutting down ML pipeline")
        if hasattr(self, "tryon_engine"):
            self.tryon_engine.shutdown()
        if hasattr(self, "recommendation_engine"):
            self.recommendation_engine.shutdown()
        if hasattr(self, "preprocessor"):
            self.preprocessor.shutdown()


def init_pipeline() -> MLPipeline:
    """Factory helper to instantiate the pipeline with env overrides."""

    device_override = os.getenv("ML_DEVICE")
    return MLPipeline(device=device_override)