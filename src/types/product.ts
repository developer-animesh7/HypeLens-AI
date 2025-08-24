export interface ProductAnalysis {
  original_product: Product;
  alternatives: Product[];
  savings_summary: SavingsSummary;
  category: string;
  analysis_date: string;
}

export interface Product {
  name: string;
  price: number;
  url: string;
  image_url?: string;
  rating?: number;
  reviews_count?: number;
  specifications?: Record<string, any>;
  features?: string[];
  brand?: string;
  platform?: string;
  availability?: string;
  shipping_info?: string;
  quality_score?: number;
  value_score?: number;
  overall_score?: number;
}

export interface SavingsSummary {
  total_savings: number;
  average_savings_percentage: number;
  best_alternative: Product;
  price_comparison: {
    original_price: number;
    lowest_alternative_price: number;
    highest_alternative_price: number;
    average_alternative_price: number;
  };
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  icon?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ErrorResponse {
  detail: string;
  error?: string;
}
