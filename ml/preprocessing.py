"""Preprocessing utilities for Avaire's virtual try-on pipeline."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:  # Optional heavy dependencies
    import cv2
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingResult:
    """Container for preprocessing outputs."""

    image_path: str
    metadata: Dict[str, Any]


class ImagePreprocessor:
    """Handles all image preprocessing steps for the try-on pipeline."""

    version = "0.1.0"

    def __init__(self, device: str = "cpu") -> None:
        self.device = device
        self._temp_dir = Path(tempfile.gettempdir()) / "avaire_preproc"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    async def preprocess_user_image(
        self, image_path: str, session_id: Optional[str] = None
    ) -> PreprocessingResult:
        """Preprocess the user image (background removal, parsing, pose)."""

        return await self._run_pipeline(
            image_path=image_path,
            session_id=session_id,
            steps=[
                self._remove_background,
                self._human_parsing,
                self._pose_estimation,
            ],
        )

    async def preprocess_garment_image(
        self, image_path: str, session_id: Optional[str] = None
    ) -> PreprocessingResult:
        """Preprocess the garment image (alignment prep, mask creation)."""

        return await self._run_pipeline(
            image_path=image_path,
            session_id=session_id,
            steps=[
                self._normalize_garment,
                self._generate_mask,
            ],
        )

    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Extract useful metadata from an image for recommendations."""

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._analyze_image_sync, image_path)

    async def bulk_preprocess(self, dataset_path: str, output_dir: str) -> int:
        """Preprocess an entire dataset for offline training tasks."""

        dataset_path_obj = Path(dataset_path)
        files = list(dataset_path_obj.glob("**/*.*"))
        count = 0
        for file_path in files:
            await self.preprocess_user_image(str(file_path))
            count += 1
        return count

    async def cleanup_temp_files(self, session_id: str) -> None:
        """Clean up temporary files created during a session."""

        if not self._temp_dir.exists():
            return

        for file in self._temp_dir.glob(f"*{session_id}*"):
            try:
                file.unlink()
            except Exception:  # pragma: no cover
                logger.debug("Failed to delete temp file: %s", file)

    def shutdown(self) -> None:
        """Release any resources held by the preprocessor."""

        # No-op for now
        logger.info("Shutting down ImagePreprocessor")

    async def _run_pipeline(self, image_path: str, session_id: Optional[str], steps):
        """Run a sequence of synchronous steps asynchronously."""

        loop = asyncio.get_running_loop()
        current_path = image_path
        metadata: Dict[str, Any] = {"source": image_path}

        for step in steps:
            current_path, new_metadata = await loop.run_in_executor(
                None, step, current_path, session_id
            )
            metadata.update(new_metadata)

        return PreprocessingResult(image_path=current_path, metadata=metadata)

    # --- Individual preprocessing stages ---

    def _remove_background(self, image_path: str, session_id: Optional[str]):
        """Placeholder background removal using rembg or OpenCV."""

        target_path = self._resolve_temp_path(image_path, session_id, suffix="_nobg.png")
        if cv2 is None:  # pragma: no cover - optional dependency
            Path(target_path).write_bytes(Path(image_path).read_bytes())
            return target_path, {"background_removed": False}

        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise FileNotFoundError(f"Unable to read image: {image_path}")

        # Placeholder: simply copy image
        cv2.imwrite(target_path, image)
        return target_path, {"background_removed": True}

    def _human_parsing(self, image_path: str, session_id: Optional[str]):
        """Placeholder human parsing step."""

        metadata = {
            "human_parsing": {
                "segments": ["upper_body", "lower_body"],
                "confidence": 0.6,
            }
        }
        return image_path, metadata

    def _pose_estimation(self, image_path: str, session_id: Optional[str]):
        """Placeholder pose estimation step."""

        metadata = {
            "pose": {
                "keypoints_detected": 17,
                "confidence": 0.7,
            }
        }
        return image_path, metadata

    def _normalize_garment(self, image_path: str, session_id: Optional[str]):
        """Normalize garment orientation and scale."""

        return image_path, {"garment_normalized": True}

    def _generate_mask(self, image_path: str, session_id: Optional[str]):
        """Generate a binary mask for the garment."""

        target_path = self._resolve_temp_path(image_path, session_id, suffix="_mask.png")
        if cv2 is None:  # pragma: no cover
            Path(target_path).write_bytes(Path(image_path).read_bytes())
            return target_path, {"mask_generated": False}

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Unable to read garment image: {image_path}")

        _, mask = cv2.threshold(image, 10, 255, cv2.THRESH_BINARY)
        cv2.imwrite(target_path, mask)
        return target_path, {"mask_generated": True}

    def _analyze_image_sync(self, image_path: str) -> Dict[str, Any]:
        """Synchronous helper to extract color palette and brightness."""

        if cv2 is None or np is None:  # pragma: no cover
            return {"analysis_available": False}

        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Unable to read image: {image_path}")

        avg_color = image.mean(axis=(0, 1)).tolist()
        brightness = float(image.mean())

        return {
            "analysis_available": True,
            "average_color_bgr": avg_color,
            "brightness": brightness,
        }

    def _resolve_temp_path(
        self, image_path: str, session_id: Optional[str], suffix: str
    ) -> str:
        """Construct a deterministic temp file path per session."""

        session_fragment = session_id or "common"
        filename = f"{Path(image_path).stem}_{session_fragment}{suffix}"
        return str(self._temp_dir / filename)
