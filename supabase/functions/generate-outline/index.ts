import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { processPrompt, OUTLINE_PROMPT, DEFAULT_PROMPT_VARIABLES } from '../_shared/prompts.ts';

const hal9Token = Deno.env.get('VITE_HAL9_TOKEN');
const supabaseUrl = Deno.env.get('SUPABASE_URL');
const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY');

interface OutlineRequest {
  title: string;
  author: string;
  bookIdea: string;
  topic: string;
  writingStyle?: string;
  targetAudience?: string;
  userId?: string;
}

interface HAL9TOCRequest {
  title: string;
  author: string;
  book_idea: string;
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

    const { title, author, bookIdea, topic, writingStyle, targetAudience, userId } = await req.json() as OutlineRequest;
    
    if (!title || !author || !bookIdea) {
      throw new Error('Missing required fields: title, author, bookIdea');
    }

    console.log('Generating outline for:', { title, author, topic: bookIdea });

    // Use HAL9 TOC endpoint first
    const hal9Response = await fetch('https://api.hal9.com/books/bookgeneratorapi/proxy/toc', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${hal9Token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title,
        author,
        book_idea: bookIdea
      } as HAL9TOCRequest),
    });

    if (!hal9Response.ok) {
      const errorText = await hal9Response.text();
      console.error('HAL9 API error:', errorText);
      throw new Error(`HAL9 API error: ${hal9Response.status} ${errorText}`);
    }

    const hal9Data = await hal9Response.json();
    console.log('HAL9 response:', hal9Data);

    // Transform HAL9 response to our BookOutline format
    const outline = transformHAL9Response(hal9Data, title, bookIdea);

    // Save to database if user provided
    if (userId && supabaseUrl && supabaseKey) {
      try {
        const supabase = createClient(supabaseUrl, supabaseKey);
        const { error: dbError } = await supabase.from('book_projects').insert({
          user_id: userId,
          title,
          author,
          book_idea: bookIdea,
          topic: topic || bookIdea,
          outline,
          writing_style: writingStyle,
          target_audience: targetAudience,
          status: 'outline_complete'
        });

        if (dbError) {
          console.error('Database save error:', dbError);
          // Don't fail the request if DB save fails
        } else {
          console.log('Outline saved to database');
        }
      } catch (dbError) {
        console.error('Database error:', dbError);
        // Continue without failing
      }
    }
    
    return new Response(JSON.stringify({ 
      success: true,
      outline 
    }), {
      status: 200,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
    
  } catch (error) {
    console.error('Outline generation error:', error);
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
 * Transform HAL9 TOC response to our BookOutline format
 */
function transformHAL9Response(hal9Data: any, title: string, description: string) {
  // HAL9 returns { toc: Array<{ section_name, section_ideas, estimated_pages }> }
  const chapters = hal9Data.toc?.map((section: any, index: number) => {
    const estimatedWords = parseEstimatedPages(section.estimated_pages);
    
    return {
      id: index === 0 ? 'intro' : `chapter-${String(index + 1).padStart(2, '0')}`,
      title: section.section_name,
      description: section.section_ideas?.slice(0, 2)?.join('. ') || 'Chapter content description',
      target_words: estimatedWords,
      status: 'pending' as const,
      key_points: section.section_ideas || [],
      prompt_context: {
        focus: section.section_ideas?.[0] || 'Main chapter focus',
        tone: 'clear and engaging'
      },
      slug: slugify(section.section_name)
    };
  }) || [];

  const totalWords = chapters.reduce((sum, ch) => sum + ch.target_words, 0);

  return {
    book: {
      title,
      description,
      target_length: totalWords
    },
    chapters
  };
}

/**
 * Parse estimated pages to word count (assuming ~250 words per page)
 */
function parseEstimatedPages(estimatedPages: string): number {
  if (!estimatedPages) return 3000;
  
  // Handle ranges like "8-12" or "10-15"
  const match = estimatedPages.match(/(\d+)[-–]?(\d+)?/);
  if (match) {
    const min = parseInt(match[1]);
    const max = match[2] ? parseInt(match[2]) : min;
    const avgPages = (min + max) / 2;
    return Math.round(avgPages * 250); // ~250 words per page
  }
  
  return 3000; // Default fallback
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