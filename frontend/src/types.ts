export interface HCP {
  id: number;
  name: string;
  specialty?: string | null;
  organization?: string | null;
  notes?: string | null;
}

export interface ExtractedEntities {
  summary?: string;
  hcp_name?: string | null;
  specialty?: string | null;
  products?: string[];
  key_topics?: string[];
  sentiment?: string;
  samples_given?: string | null;
  follow_up_date?: string | null;
  follow_up_action?: string | null;
}

export interface Interaction {
  id: number;
  hcp_id: number;
  rep_name?: string | null;
  date?: string | null;
  channel?: string | null;
  product_discussed?: string | null;
  raw_notes?: string | null;
  llm_summary?: string | null;
  extracted_entities?: ExtractedEntities | null;
  sentiment?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  hcp?: HCP | null;
}

export interface InteractionCreate {
  hcp_name: string;
  specialty?: string;
  organization?: string;
  rep_name?: string;
  date?: string;
  channel?: string;
  product_discussed?: string;
  raw_notes: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: string[];
}

export interface FollowUp {
  id: number;
  hcp_id: number;
  interaction_id?: number | null;
  due_date?: string | null;
  action?: string | null;
  status?: string | null;
  hcp?: HCP | null;
}
