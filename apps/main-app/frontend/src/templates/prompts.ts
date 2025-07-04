/**
 * AI Prompt Templates for Book Generation
 * Extracted from cc-template and adapted for direct AI integration
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

export const CHAPTER_PROMPT = `Write Chapter {chapterNumber}: "{chapterTitle}" for the book "{title}" by {author}.

Chapter Summary: {chapterSummary}
Key Points to Cover: {keyPoints}

Context:
- Previous chapters: {previousChapters}
- Book theme: {bookTheme}
- Target audience: {targetAudience}
- Writing style: {writingStyle}

Write a complete, engaging chapter of approximately {estimatedPages} pages (roughly {targetWords} words). The chapter should:

1. **Start with a compelling hook** that draws readers in
2. **Build on previous chapters** while introducing new concepts
3. **Cover all key points** in a logical, flowing manner
4. **Include practical examples** and real-world applications where relevant
5. **End with a smooth transition** to the next chapter or conclusion

Format the chapter in Markdown with:
- Clear section headings (##, ###)
- Well-structured paragraphs
- Bullet points or numbered lists where appropriate
- Emphasis (*italic* or **bold**) for important concepts
- Code blocks or quotes where relevant

The chapter should be engaging, informative, and maintain the {writingStyle} style throughout. Write for {targetAudience}, ensuring concepts are accessible yet thorough.

Generate only the chapter content in Markdown format, no additional commentary.`;

export const INTRODUCTION_PROMPT = `Write an engaging introduction chapter for the book "{title}" by {author}.

Book Description: {topic}
Writing Style: {writingStyle}
Target Audience: {targetAudience}

This introduction should:

1. **Hook the reader** with a compelling opening that demonstrates why this topic matters
2. **Establish credibility** and explain why you're qualified to write about this topic
3. **Preview the journey** - what readers will learn and accomplish by the end
4. **Set expectations** for the book's approach and style
5. **Create excitement** for the chapters ahead

The introduction should be approximately 2000-3000 words and include:
- A powerful opening story, statistic, or question
- Clear explanation of what the book covers
- Who this book is for (and who it's not for)
- How to get the most out of the book
- What readers will be able to do after reading

Format in Markdown with clear sections and engaging, accessible language that matches the {writingStyle} style.

Generate only the introduction content in Markdown format, no additional commentary.`;

export const CONCLUSION_PROMPT = `Write a compelling conclusion chapter for the book "{title}" by {author}.

Book Description: {topic}
Key Chapters Covered: {previousChapters}
Writing Style: {writingStyle}
Target Audience: {targetAudience}

This conclusion should:

1. **Summarize key insights** from throughout the book
2. **Reinforce the main message** and why it matters
3. **Provide actionable next steps** for readers
4. **Inspire action** and continued learning
5. **End on a high note** that leaves readers motivated

The conclusion should be approximately 2000-3000 words and include:
- Brief recap of the journey through the book
- The most important takeaways
- Practical next steps readers can take immediately
- Resources for continued learning
- A memorable final thought or call to action

Format in Markdown with clear sections and inspiring, motivational language that matches the {writingStyle} style.

Generate only the conclusion content in Markdown format, no additional commentary.`;

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
  targetWords: 4000,
};