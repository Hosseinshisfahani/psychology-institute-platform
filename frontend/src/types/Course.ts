export interface Course {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  thumbnail: string | null;
  price: number;
  discount_price: number | null;
  current_price: number;
  discount_percentage: number;
  is_free: boolean;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_hours: number;
  language: string;
  level: string;
  instructor_name: string;
  category_name: string;
  category_slug: string;
  enrollment_count: number;
  rating: number;
  review_count: number;
  created_at: string;
  created_at_persian: string;
}

export interface CourseCategory {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  color: string;
}

export interface CourseFilters {
  search?: string;
  category?: number;
  difficulty?: string;
  is_free?: boolean;
  language?: string;
  min_price?: number;
  max_price?: number;
  ordering?: string;
}
