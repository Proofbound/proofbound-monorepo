import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const hal9Token = Deno.env.get('VITE_HAL9_TOKEN');

interface ChapterRequest {
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
  // HAL9 specific fields
  toc: Array<{
    section_name: string;
    section_ideas: string[];
    estimated_pages: string;
  }>;
  book_idea: string;
}

interface HAL9ChapterRequest {
  title: string;
  author: string;
  book_idea: string;
  toc: Array<{
    section_name: string;
    section_ideas: string[];
    estimated_pages: string;
  }>;
  chapter_number: number;
  content_depth?: 'outline' | 'draft' | 'polished';
  generation_mode?: 'sequential' | 'parallel' | 'selective';
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      },
    });
  }

  try {
    if (!hal9Token) {
      throw new Error('HAL9 token not configured');
    }

    const chapterData = await req.json() as ChapterRequest;
    
    const { 
      chapterNumber, 
      chapterTitle, 
      bookTitle,
      author,
      book_idea,
      toc
    } = chapterData;

    if (!chapterNumber || !chapterTitle || !bookTitle || !author || !book_idea || !toc) {
      throw new Error('Missing required fields for chapter generation');
    }

    console.log('Generating chapter:', { chapterNumber, chapterTitle, bookTitle });

    // Use HAL9 generate-book-chapters endpoint
    const hal9Response = await fetch('https://api.hal9.com/books/bookgeneratorapi/proxy/generate-book-chapters', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${hal9Token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: bookTitle,
        author,
        book_idea,
        toc,
        chapter_number: chapterNumber,
        content_depth: 'polished',
        generation_mode: 'selective'
      } as HAL9ChapterRequest),
    });

    if (!hal9Response.ok) {
      const errorText = await hal9Response.text();
      console.error('HAL9 API error:', errorText);
      throw new Error(`HAL9 API error: ${hal9Response.status} ${errorText}`);
    }

    const hal9Data = await hal9Response.json();
    console.log('HAL9 chapter response received');

    // Transform HAL9 response to our format
    const generatedChapter = transformHAL9ChapterResponse(hal9Data, chapterData);
    
    return new Response(JSON.stringify({ 
      success: true,
      ...generatedChapter
    }), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
    
  } catch (error) {
    console.error('Chapter generation error:', error);
    return new Response(JSON.stringify({ 
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
  }
});

/**
 * Transform HAL9 chapter response to our GeneratedChapter format
 */
function transformHAL9ChapterResponse(hal9Data: any, originalRequest: ChapterRequest) {
  // HAL9 returns: { chapter_number, chapter_title, content, word_count, estimated_pages }
  const wordCount = hal9Data.word_count || estimateWordCount(hal9Data.content || '');
  
  return {
    chapterNumber: hal9Data.chapter_number || originalRequest.chapterNumber,
    chapterTitle: hal9Data.chapter_title || originalRequest.chapterTitle,
    content: hal9Data.content || '# Chapter content not generated\n\nPlease try again.',
    word_count: wordCount,
    estimated_pages: hal9Data.estimated_pages || Math.ceil(wordCount / 250),
    generated_at: new Date().toISOString(),
    status: 'generated' as const,
    // Include original metadata
    id: `chapter-${String(originalRequest.chapterNumber).padStart(2, '0')}`,
    title: hal9Data.chapter_title || originalRequest.chapterTitle,
    description: originalRequest.chapterSummary,
    target_words: originalRequest.targetWords || 3000,
    key_points: originalRequest.keyPoints,
    prompt_context: {
      focus: originalRequest.keyPoints[0] || 'Chapter focus',
      tone: originalRequest.writingStyle || 'clear and engaging'
    },
    slug: slugify(hal9Data.chapter_title || originalRequest.chapterTitle)
  };
}

/**
 * Estimate word count from content
 */
function estimateWordCount(content: string): number {
  if (!content) return 0;
  return content.split(/\s+/).filter(word => word.length > 0).length;
}

/**
 * Convert title to URL-friendly slug
 */
function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}