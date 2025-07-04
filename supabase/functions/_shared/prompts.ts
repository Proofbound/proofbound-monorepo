/**
 * Shared prompt templates for Supabase Edge Functions
 * Re-export from the main frontend prompts for consistency
 */

export interface PromptVariables {
  title?: string;
  author?: string;
  topic?: string;
  bookIdea?: string;
  writingStyle?: string;
  targetAudience?: string;
  chapterNumber?: number;
  chapterTitle?: string;
  chapterSummary?: string;
  keyPoints?: string[];
  previousChapters?: string[];
  bookTheme?: string;
  estimatedPages?: number;
}

export const OUTLINE_PROMPT = `You are an expert book outline generator. Generate a detailed chapter outline for a book on the following topic:

**Topic:** {topic}
**Writing Style:** {writingStyle}
**Target Audience:** {targetAudience}

Please create an outline with 8-12 chapters that:
1. Starts with an engaging introduction
2. Builds knowledge progressively
3. Includes practical applications where relevant
4. Ends with a compelling conclusion

For each chapter, provide:
- A clear, engaging chapter title
- A 2-3 sentence description of what the chapter covers
- Estimated word count (aim for 3000-5000 words per chapter)
- Key points or subtopics to cover

Format your response as a JSON structure that matches this template:

{
  "book": {
    "title": "{title}",
    "description": "{topic}",
    "target_length": 50000
  },
  "chapters": [
    {
      "id": "intro",
      "title": "Your Chapter Title Here",
      "description": "Brief description of what this chapter covers and why it's important.",
      "target_words": 3500,
      "status": "pending",
      "key_points": [
        "First key point to cover",
        "Second key point to cover",
        "Third key point to cover"
      ],
      "prompt_context": {
        "focus": "Key themes or focus areas for this chapter",
        "tone": "{writingStyle}"
      }
    }
  ]
}

Continue this pattern for all chapters. Make sure:
- Chapter IDs are unique and follow the pattern: intro, chapter-02, chapter-03, etc.
- Total word count across all chapters is around 40,000-60,000 words
- Each chapter builds on previous ones logically
- The outline is comprehensive yet focused on the core topic

Generate only the JSON content, no additional commentary.`;

/**
 * Process prompt template by replacing variables
 */
export function processPrompt(template: string, variables: PromptVariables): string {
  let processed = template;
  
  // Replace all variables in the template
  Object.entries(variables).forEach(([key, value]) => {
    const placeholder = `{${key}}`;
    const replacement = Array.isArray(value) ? value.join(', ') : String(value || '');
    processed = processed.replace(new RegExp(placeholder, 'g'), replacement);
  });
  
  return processed;
}

/**
 * Default values for prompt variables
 */
export const DEFAULT_PROMPT_VARIABLES: Partial<PromptVariables> = {
  writingStyle: 'clear and engaging',
  targetAudience: 'general readers',
  estimatedPages: 15,
};