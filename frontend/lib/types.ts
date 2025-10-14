export interface CatalogItem {
  id: number;
  name: string;
  description: string;
  brand: string;
  category: string;
  subcategory: string;
  occasion: string;
  price: number;
  currency: string;
  primary_image_url: string;
  additional_images: string[];
  colors: string[];
  sizes: string[];
  material: string;
  fit_type: string;
  sleeve_length: string;
  tags: string[];
  stock_quantity: number;
  is_available: boolean;
}

export interface Recommendation {
  outfit_id: number;
  score: number;
  reason: string;
  outfit: CatalogItem;
}

export interface StyleDNAProfile {
  user_id: number;
  skin_tone: string;
  body_type: string;
  height_cm: number;
  weight_kg: number;
  bust_size?: string;
  waist_size?: string;
  hip_size?: string;
  preferred_colors: string[];
  avoided_colors?: string[];
  preferred_styles: string[];
  preferred_occasions: string[];
  lifestyle: string;
  age_group: string;
  budget_range?: {
    min: number;
    max: number;
  };
}

export interface TryOnSession {
  session_id: string;
  outfit_id: number;
  result_image_url: string;
  processing_time_seconds: number;
  quality_score: number;
  created_at: string;
}

export interface FilterState {
  search: string;
  category: string | null;
  occasion: string | null;
  priceRange: [number, number];
  colors: string[];
  sizes: string[];
  tags: string[];
}
