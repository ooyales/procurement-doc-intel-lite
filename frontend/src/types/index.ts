// ── Auth ──────────────────────────────────────────────

export interface User {
  id: number;
  username: string;
  display_name: string;
  email: string;
  role: string;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  setAuth: (token: string, user: User) => void;
}

// ── Document Types ───────────────────────────────────

export type DocumentType =
  | 'vendor_quote'
  | 'purchase_order'
  | 'invoice'
  | 'bom'
  | 'contract'
  | 'delivery_order'
  | 'price_list'
  | 'other';

export type ProcessingStatus =
  | 'uploaded'
  | 'extracting'
  | 'mapping'
  | 'review'
  | 'complete'
  | 'failed';

export type FileFormat = 'pdf' | 'xlsx' | 'docx' | 'csv';

export type LineItemCategory =
  | 'hardware'
  | 'software'
  | 'service'
  | 'license'
  | 'maintenance'
  | 'labor'
  | 'other';

// ── Document ─────────────────────────────────────────

export interface Document {
  id: string;
  original_filename: string;
  file_format: FileFormat;
  file_size_bytes: number | null;
  file_hash: string | null;
  stored_path: string | null;
  document_type: DocumentType | null;
  vendor_name: string | null;
  document_number: string | null;
  document_date: string | null;
  contract_number: string | null;
  task_order_number: string | null;
  period_of_performance_start: string | null;
  period_of_performance_end: string | null;
  total_amount: number | null;
  currency: string;
  processing_status: ProcessingStatus;
  extraction_method: string | null;
  extraction_confidence: number | null;
  ai_model_used: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  review_notes: string | null;
  chunk_count: number;
  embedded: number;
  uploaded_by: string | null;
  created_at: string | null;
  updated_at: string | null;
  tags: string;
  notes: string | null;
  line_item_count: number;
  line_items?: LineItem[];
}

// ── Line Item ────────────────────────────────────────

export interface LineItem {
  id: string;
  document_id: string;
  line_number: number | null;
  clin: string | null;
  slin: string | null;
  part_number: string | null;
  manufacturer: string | null;
  manufacturer_part_number: string | null;
  product_name: string | null;
  product_description: string | null;
  category: LineItemCategory | null;
  sub_category: string | null;
  quantity: number | null;
  unit_of_issue: string | null;
  unit_price: number | null;
  extended_price: number | null;
  discount_percent: number | null;
  discount_amount: number | null;
  labor_category: string | null;
  labor_hours: number | null;
  labor_rate: number | null;
  period_start: string | null;
  period_end: string | null;
  mapping_confidence: number | null;
  human_verified: number;
  original_row_text: string | null;
  created_at: string | null;
  // Joined from document
  vendor_name: string | null;
  document_number: string | null;
  document_type: string | null;
  document_date: string | null;
  original_filename: string | null;
}

// ── Document Chunk ───────────────────────────────────

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  chunk_type: string | null;
  page_number: number | null;
  created_at: string | null;
}

// ── Field Mapping ────────────────────────────────────

export interface FieldMapping {
  id: string;
  vendor_name: string;
  source_column_name: string;
  target_field: string;
  confidence: number;
  times_confirmed: number;
  created_at: string | null;
}

// ── Canonical Product ────────────────────────────────

export interface CanonicalProduct {
  id: string;
  canonical_name: string;
  category: string | null;
  manufacturer: string | null;
  known_part_numbers: string[];
  known_aliases: string[];
  last_known_price: number | null;
  last_price_date: string | null;
  avg_price: number | null;
  min_price: number | null;
  max_price: number | null;
  price_history: Array<{ price: number; date: string; vendor: string }>;
  asset_tracker_category: string | null;
  created_at: string | null;
}

// ── Chat ─────────────────────────────────────────────

export interface ChatSource {
  document_id: string;
  document_number: string;
  vendor_name: string;
  original_filename: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: ChatSource[];
}

// ── Dashboard ────────────────────────────────────────

export interface DashboardData {
  total_documents: number;
  documents_by_status: Record<string, number>;
  documents_by_type: Record<string, number>;
  total_line_items: number;
  total_products: number;
  total_spend: number;
  top_vendors: Array<{ vendor: string; spend: number; document_count: number }>;
  spend_by_category: Record<string, number>;
  recent_documents: Document[];
  processing_queue: Document[];
}
