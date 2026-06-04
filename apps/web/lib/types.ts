export interface Profile {
  id: string;
  full_name: string;
  headline: string;
  location: string;
  email: string;
  phone: string;
  links: string;
  default_summary: string;
  created_at: string;
  updated_at: string;
}

export interface Position {
  id: string; company: string; title: string; employment_type: string;
  location: string; start_date: string | null; end_date: string | null;
  is_current: boolean; description: string; tech_stack: string;
  created_at: string; updated_at: string;
}

export interface Project {
  id: string; title: string; organization: string; role: string;
  summary: string; skills: string; tools: string; domain: string;
  impact: string; created_at: string; updated_at: string;
}

export interface Evidence {
  id: string; type: string; title: string; description: string;
  url: string; confidence: number; created_at: string; updated_at: string;
}

export interface Resume {
  id: string; title: string; target_role: string; status: string;
  job_description_id: string | null; created_at: string; updated_at: string;
}

export interface ResumeVersion {
  id: string; resume_id: string; version_number: number;
  content_json: string; markdown: string; html: string;
  ats_score: number | null; review_notes: string; created_at: string;
}

export interface JD {
  id: string; title: string; company: string; raw_text: string;
  source_url: string; source_type: string; analysis: string;
  created_at: string; updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface HealthResponse {
  status: string;
  database: { status: string; message?: string };
  environment: string;
}

export interface LLMHealthResponse {
  llm: { provider: string; configured: boolean };
  search: { configured: boolean };
}
