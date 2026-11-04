export interface Account {
  handle: string;
  name: string;
  avatar: string;
  bio: string;
  location?: string;
  posts: number;
  followers: number;
  following: number;
  verified?: boolean;
  photos: string[];
  category?: "football" | "travel" | "photography" | "technology" | "lifestyle";
  profileLabel?: string;
  highlights?: string[];
}
export interface Post {
  id: string;
  account: string;
  image: string;
  location: string;
  caption: string;
  likes: number;
  comments: number;
  age: string;
  images?: string[];
}
export type ClaimStatus = "under_review" | "confirmed" | "rejected";
export interface ProfileRisk {
  risk_score: number;
  risk_band: string;
  factors: { label: string; value: number; direction: string }[];
  limitations: string[];
  out_of_range_features: string[];
}
export interface Analysis {
  provider?: string;
  model?: string;
  similarity_score?: number;
  summary?: string;
  evidence?: string[];
  differences?: string[];
  limitations?: string[];
  recommendation?: string;
  profile_ml?: ProfileRisk;
  pair_ml?: {
    risk_score: number | null;
    assessment: string;
    training_data: "synthetic";
    factors: { label: string; value: number; direction: string }[];
    limitations: string[];
  };
  screenshot_tools?: ScreenshotTools;
  privacy_redaction?: RedactionAudit;
}
export interface Claim {
  id: string;
  suspect_handle: string;
  owner_handle: string;
  status: ClaimStatus;
  score: number;
  reasons: string[];
  analysis: Analysis;
  created_at?: string;
  evidence?: { original: string; suspect: string };
  version?: number;
  history?: ModerationEvent[];
  appeals?: AppealRecord[];
}
export interface ModerationEvent {
  kind: string;
  reason: string;
  actor: string;
  at: string;
  version: number;
  from_status?: string;
  to_status?: string;
}
export interface AppealRecord {
  id: string;
  reason: string;
  status: "pending" | "uphold" | "overturn";
  created_at: string;
  resolved_at?: string;
  resolution_reason?: string;
}
export interface ServiceStatus {
  public_demo?: boolean;
  privacy_redaction_required?: boolean;
  provider: string;
  model: string | null;
  ready: boolean;
  meta_key_configured: boolean;
  profile_ml: { ready: boolean; enabled: boolean; model?: string };
  pair_ml?: { ready: boolean; model?: string; training_data?: string };
  evidence_tools?: { ready: boolean; code?: string };
}

export interface PrivacyReport {
  provider?: string;
  count: number;
  findings: { entity_type: string; confidence?: number; box?: number[] }[];
}
export interface ScreenshotTools {
  providers: { ocr: string; photos: string; privacy: string };
  original: { privacy: PrivacyReport };
  suspect: { privacy: PrivacyReport };
  photos: {
    count: number;
    matches: {
      original_index: number;
      suspect_index: number;
      phash_distance?: number;
      verification?: "perceptual_hash" | "orb_geometry" | "sift_geometry";
      geometric_inliers?: number;
    }[];
    original_boxes: number[][];
    suspect_boxes: number[][];
    limitations: string[];
  };
  elapsed_seconds: number;
}
export interface ScreenshotInspection extends ScreenshotTools {
  inspection_id: string;
  original: InspectedProfile;
  suspect: InspectedProfile;
  redaction: RedactionAudit & {
    previews: { original: string; suspect: string };
  };
}
export interface RedactionAudit {
  applied: boolean;
  policy_version: string;
  regions_masked: number;
  images?: Record<string, { sha256: string; regions_masked: number }>;
}
export interface InspectedProfile {
  fields: Record<string, { value: string | number; confidence: number }>;
  warnings: string[];
  privacy: PrivacyReport;
}
