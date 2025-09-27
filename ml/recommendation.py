"""Rule-based recommendation engine for Avaire MVP."""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate contextual outfit recommendations from catalog metadata."""

    version = "rb-0.1.0"

    def __init__(self) -> None:
        self._loop = asyncio.get_event_loop()

    async def generate_recommendations(
        self,
        style_dna: Dict[str, Any],
        context: Optional[str],
        limit: int,
        catalog_items: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Public async wrapper around synchronous scoring."""

        if catalog_items is None:
            logger.warning("Catalog items missing; returning empty recommendations")
            return []

        return await asyncio.get_running_loop().run_in_executor(
            None,
            self._score_catalog,
            style_dna,
            context,
            limit,
            catalog_items,
        )

    def warmup(self) -> None:
        """Placeholder for loading ML models later."""

        logger.info("RecommendationEngine warmup - nothing to load yet")

    def shutdown(self) -> None:
        """Clean up resources if needed."""

        logger.info("RecommendationEngine shutdown")

    # --- Internal helpers ---

    def _score_catalog(
        self,
        style_dna: Dict[str, Any],
        context: Optional[str],
        limit: int,
        catalog_items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Score catalog items against style DNA heuristics."""

    scored: List[Tuple[float, Dict[str, Any]]] = []
        preferred_colors = set(style_dna.get("preferred_colors", []))
        avoided_colors = set(style_dna.get("avoided_colors", []))
        preferred_styles = set(style_dna.get("preferred_styles", []))
        preferred_occasions = set(style_dna.get("preferred_occasions", []))
        budget = style_dna.get("budget_range") or {}
        min_budget = budget.get("min", 0)
        max_budget = budget.get("max", 999999)

        for item in catalog_items:
            score = 0.0
            reasons = []

            # Budget matching
            price = item.get("price", 0)
            if min_budget <= price <= max_budget:
                score += 0.2
                reasons.append("within_budget")

            # Color preferences
            item_colors = set(item.get("colors") or [])
            if item_colors & preferred_colors:
                score += 0.25
                reasons.append("color_match")
            if item_colors & avoided_colors:
                score -= 0.2
                reasons.append("avoided_color")

            # Style tags
            item_tags = set(item.get("tags") or [])
            if item_tags & preferred_styles:
                score += 0.2
                reasons.append("style_match")

            # Occasion/context
            item_occasion = item.get("occasion")
            if context and item_occasion == context:
                score += 0.25
                reasons.append("context_match")
            elif preferred_occasions and item_occasion in preferred_occasions:
                score += 0.15
                reasons.append("preferred_occasion")

            # Popularity heuristic
            interactions = item.get("interaction_score", 0)
            score += min(interactions / 100.0, 0.1)

            scored.append((score, {**item, "match_reasons": reasons, "confidence": round(max(score, 0.0), 2)}))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _score, item in scored[:limit]]

    def summarize_preferences(self, catalog_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate catalog metadata to help UX surface filter suggestions."""

        tags = Counter()
        occasions = Counter()
        colors = Counter()
        for item in catalog_items:
            tags.update(item.get("tags") or [])
            occasions.update([item.get("occasion")])
            colors.update(item.get("colors") or [])

        return {
            "top_tags": tags.most_common(5),
            "top_occasions": occasions.most_common(5),
            "top_colors": colors.most_common(5),
        }
