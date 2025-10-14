import type { CatalogItem, Recommendation, TryOnSession, StyleDNAProfile } from "@/lib/types";

export const sampleHeroLooks = [
  {
    id: "fusion-glam",
    title: "Fusion Glam for Festive Nights",
    description: "A shimmer sari with a streetwear crop top for the girl who loves remixing traditions.",
    image: "/images/hero-fusion.jpg"
  },
  {
    id: "campus-cool",
    title: "Campus Cool for Everyday Confidence",
    description: "Relaxed cargo coord with layered jewelry to match your hustle.",
    image: "/images/hero-campus.jpg"
  },
  {
    id: "power-hour",
    title: "Power Hour Boardroom Energy",
    description: "Structured blazer dress with statement belt for career highs and after-hours vibes.",
    image: "/images/hero-power.jpg"
  }
] as const;

export const sampleCatalog: CatalogItem[] = [
  {
    id: 101,
    name: "Ikat Draped Saree",
    description: "Handwoven ikat saree paired with a modern cut blouse.",
    brand: "Avaire Studio",
    category: "indian_wear",
    subcategory: "saree",
    occasion: "wedding",
    price: 6999,
    currency: "INR",
    primary_image_url: "/storage/catalog/outfit_001.jpg",
    additional_images: [
      "/storage/catalog/outfit_001_alt1.jpg",
      "/storage/catalog/outfit_001_alt2.jpg"
    ],
    colors: ["pearl", "gold"],
    sizes: ["S", "M", "L"],
    material: "silk",
    fit_type: "draped",
    sleeve_length: "sleeveless",
    tags: ["festive", "minimal"],
    stock_quantity: 8,
    is_available: true
  },
  {
    id: 205,
    name: "Velvet Power Blazer",
    description: "Cropped blazer with sharp shoulders and matching pleated skort.",
    brand: "Noir Alley",
    category: "western_wear",
    subcategory: "blazer",
    occasion: "formal",
    price: 5499,
    currency: "INR",
    primary_image_url: "/storage/catalog/outfit_045.jpg",
    additional_images: [
      "/storage/catalog/outfit_045_alt1.jpg"
    ],
    colors: ["black", "emerald"],
    sizes: ["XS", "S", "M"],
    material: "velvet",
    fit_type: "structured",
    sleeve_length: "full",
    tags: ["power", "classic"],
    stock_quantity: 5,
    is_available: true
  },
  {
    id: 309,
    name: "Coastal Brunch Coord",
    description: "Two-piece linen coord set with playful shell buttons.",
    brand: "Urban Nari",
    category: "fusion",
    subcategory: "coord_set",
    occasion: "brunch",
    price: 3299,
    currency: "INR",
    primary_image_url: "/storage/catalog/outfit_078.jpg",
    additional_images: [
      "/storage/catalog/outfit_078_alt1.jpg"
    ],
    colors: ["mint", "ivory"],
    sizes: ["XS", "S", "M", "L"],
    material: "linen",
    fit_type: "relaxed",
    sleeve_length: "short",
    tags: ["boho", "minimal"],
    stock_quantity: 12,
    is_available: true
  }
];

export const sampleStyleDNA: StyleDNAProfile = {
  user_id: 1,
  skin_tone: "medium",
  body_type: "hourglass",
  height_cm: 164,
  weight_kg: 58,
  bust_size: "M",
  waist_size: "S",
  hip_size: "M",
  preferred_colors: ["emerald", "blush", "black"],
  avoided_colors: ["neon", "orange"],
  preferred_styles: ["street", "festive"],
  preferred_occasions: ["party", "brunch"],
  lifestyle: "creator",
  age_group: "23-27"
};

export const sampleRecommendations: Recommendation[] = sampleCatalog.map((item, idx) => ({
  outfit_id: item.id,
  score: 0.9 - idx * 0.1,
  reason: idx === 0 ? "Color sync with preferred palette" : "Mirror fit to Style DNA silhouette",
  outfit: item
}));

export const sampleTryOnHistory: TryOnSession[] = [
  {
    session_id: "TRYON-01-01",
    outfit_id: 205,
    result_image_url: "/storage/results/TRYON-01-01.jpg",
    processing_time_seconds: 8.4,
    quality_score: 0.86,
    created_at: new Date().toISOString()
  },
  {
    session_id: "TRYON-01-02",
    outfit_id: 101,
    result_image_url: "/storage/results/TRYON-01-02.jpg",
    processing_time_seconds: 7.9,
    quality_score: 0.82,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString()
  }
];
