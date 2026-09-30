export type Category = 'food' | 'transport' | 'home' | 'leisure' | 'health' | 'other';

export interface User {
  id: number;
  email: string;
  telegram_id: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Expense {
  id: number;
  amount: string;
  category: Category | string;
  note: string | null;
  spent_at: string;
  created_at: string;
}

export interface CategoryTotal {
  category: string;
  total: string;
}

export interface MonthSummary {
  year: number;
  month: number;
  total: string;
  by_category: CategoryTotal[];
  count: number;
}

export interface LinkCode {
  code: string;
  expires_at: string;
  bot_deep_link_hint: string;
}

export const CATEGORIES: Category[] = ['food', 'transport', 'home', 'leisure', 'health', 'other'];

export const CATEGORY_LABELS: Record<string, string> = {
  food: 'Comida',
  transport: 'Transporte',
  home: 'Casa',
  leisure: 'Ocio',
  health: 'Salud',
  other: 'Otros',
};
