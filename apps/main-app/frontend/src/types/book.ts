/**
 * Type definitions for book generation
 */

// Re-export types from other modules for convenience
export type {
  BookMetadata,
  BookOutline,
  Chapter,
  GeneratedChapter
} from '../templates/quartoConfig';

export type {
  PromptVariables
} from '../templates/prompts';

export type {
  QuartoProject,
  ProjectGenerationOptions,
  ProjectStats,
  ProjectValidation
} from '../services/projectGenerator';

/**
 * Book generation request from user form
 */
export interface BookGenerationRequest {
  title: string;
  author: string;
  bookIdea: string;
  topic: string;
  writingStyle?: string;
  targetAudience?: string;
  estimatedLength?: number;
  genre?: string;
  format?: 'html' | 'pdf' | 'epub' | 'all';
}

/**
 * Chapter generation request
 */
export interface ChapterGenerationRequest {
  projectId?: string;
  chapterNumber: number;
  chapterTitle: string;
  chapterSummary: string;
  keyPoints: string[];
  bookTitle: string;
  author: string;
  previousChapters?: string[];
  bookTheme?: string;
  targetAudience?: string;
  writingStyle?: string;
  estimatedPages?: number;
  targetWords?: number;
}

/**
 * AI generation response
 */
export interface AIGenerationResponse {
  success: boolean;
  content?: string;
  outline?: BookOutline;
  chapter?: GeneratedChapter;
  error?: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * Book project in database
 */
export interface BookProject {
  id: string;
  user_id: string;
  title: string;
  author: string;
  book_idea: string;
  topic: string;
  outline?: BookOutline;
  status: 'draft' | 'outline_complete' | 'generating' | 'complete';
  created_at: string;
  updated_at: string;
  writing_style?: string;
  target_audience?: string;
  estimated_length?: number;
  format?: string;
}

/**
 * Chapter generation status
 */
export interface ChapterStatus {
  chapterIndex: number;
  status: 'pending' | 'generating' | 'generated' | 'error';
  generatedAt?: string;
  wordCount?: number;
  error?: string;
}

/**
 * Book generation progress
 */
export interface GenerationProgress {
  projectId: string;
  totalChapters: number;
  completedChapters: number;
  currentChapter?: number;
  status: 'outline' | 'generating_chapters' | 'complete' | 'error';
  estimatedCompletion?: string;
  chaptersStatus: ChapterStatus[];
}

/**
 * File download options
 */
export interface DownloadOptions {
  format: 'zip' | 'individual';
  includeSource: boolean;
  includePreview?: boolean;
}

/**
 * Project export data
 */
export interface ProjectExport {
  project: QuartoProject;
  metadata: BookMetadata;
  stats: ProjectStats;
  exportedAt: string;
  version: string;
}

/**
 * AI provider configuration
 */
export interface AIProviderConfig {
  provider: 'hal9' | 'openai' | 'anthropic';
  model?: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
}

/**
 * Generation settings
 */
export interface GenerationSettings {
  aiProvider: AIProviderConfig;
  chapterLength: 'short' | 'medium' | 'long';
  writingStyle: 'academic' | 'conversational' | 'technical' | 'creative';
  includeReferences: boolean;
  includeImages: boolean;
  autoGenerate: boolean;
}

/**
 * User preferences for book generation
 */
export interface UserGenerationPreferences {
  defaultWritingStyle: string;
  defaultTargetAudience: string;
  defaultFormat: string;
  aiProvider: string;
  autoSave: boolean;
  showAdvancedOptions: boolean;
}

/**
 * Book template for quick start
 */
export interface BookTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  outline: Partial<BookOutline>;
  defaultSettings: Partial<GenerationSettings>;
  estimatedChapters: number;
  estimatedLength: number;
  tags: string[];
}

/**
 * Error types for better error handling
 */
export type BookGenerationError = 
  | 'INVALID_INPUT'
  | 'AI_API_ERROR'
  | 'QUOTA_EXCEEDED'
  | 'NETWORK_ERROR'
  | 'UNKNOWN_ERROR';

/**
 * API response wrapper
 */
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    type: BookGenerationError;
    message: string;
    details?: any;
  };
}

/**
 * Form validation errors
 */
export interface FormErrors {
  title?: string;
  author?: string;
  bookIdea?: string;
  topic?: string;
  writingStyle?: string;
  targetAudience?: string;
}

/**
 * Component props for book generation components
 */
export interface BookFormProps {
  initialData?: Partial<BookGenerationRequest>;
  onSubmit: (data: BookGenerationRequest) => void;
  isLoading?: boolean;
  errors?: FormErrors;
}

export interface OutlineDisplayProps {
  outline: BookOutline;
  editable?: boolean;
  onChapterClick?: (chapterIndex: number) => void;
  onOutlineChange?: (outline: BookOutline) => void;
}

export interface ChapterCardProps {
  chapter: Chapter;
  chapterIndex: number;
  isGenerating?: boolean;
  generatedContent?: GeneratedChapter;
  onGenerate?: (chapterIndex: number) => void;
  onEdit?: (chapterIndex: number, content: string) => void;
  onDelete?: (chapterIndex: number) => void;
}

export interface ProgressIndicatorProps {
  progress: GenerationProgress;
  showDetails?: boolean;
}

/**
 * Utility types
 */
export type BookStatus = BookProject['status'];
export type ChapterStatusType = ChapterStatus['status'];
export type GenerationPhase = GenerationProgress['status'];

/**
 * Constants
 */
export const WRITING_STYLES = [
  'clear and engaging',
  'academic and formal',
  'conversational and friendly',
  'technical and detailed',
  'creative and narrative',
  'professional and authoritative'
] as const;

export const TARGET_AUDIENCES = [
  'general readers',
  'beginners',
  'intermediate learners',
  'advanced practitioners',
  'professionals',
  'students',
  'researchers'
] as const;

export const BOOK_FORMATS = [
  'html',
  'pdf',
  'epub',
  'all'
] as const;

export const AI_PROVIDERS = [
  'hal9',
  'openai',
  'anthropic'
] as const;

export type WritingStyle = typeof WRITING_STYLES[number];
export type TargetAudience = typeof TARGET_AUDIENCES[number];
export type BookFormat = typeof BOOK_FORMATS[number];
export type AIProvider = typeof AI_PROVIDERS[number];