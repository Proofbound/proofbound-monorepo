import { useState } from 'react';

interface GenerateContentRequest {
  title: string;
  author: string;
  book_idea: string;
  toc: Array<{
    section_name: string;
    section_ideas: string[];
    estimated_pages: string;
  }>;
  chapter_number?: number;
  content_depth?: 'outline' | 'draft' | 'polished';
  generation_mode?: 'sequential' | 'parallel' | 'selective';
}

interface GenerateContentResponse {
  chapter_number: number;
  chapter_title: string;
  content: string;
  word_count: number;
  estimated_pages: number;
}

interface GenerateCoverRequest {
  title: string;
  author: string;
  book_description: string;
  style_prompt?: string;
  color_scheme?: string;
  design_style?: 'modern' | 'classic' | 'minimalist' | 'bold';
}

interface GenerateCoverResponse {
  cover_url: string;
  design_description: string;
  color_palette: string[];
}

interface GeneratePDFRequest {
  title: string;
  author: string;
  chapters: Array<{
    chapter_number: number;
    chapter_title: string;
    content: string;
  }>;
  cover_url?: string;
  include_toc?: boolean;
  page_format?: 'A4' | 'US Letter' | '6x9' | '5x8';
}

interface GeneratePDFResponse {
  pdf_url: string;
  total_pages: number;
  word_count: number;
  file_size_mb: number;
}

// No API needed - just return mock data directly

export function useDemoBookGeneration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateContent = async (request: GenerateContentRequest): Promise<GenerateContentResponse | null> => {
    try {
      setLoading(true);
      setError(null);

      console.log('🚀 Generating mock chapter content...');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      const chapterIndex = (request.chapter_number || 1) - 1;
      const chapterData = request.toc[chapterIndex];
      
      const mockResponse = {
        chapter_number: request.chapter_number || 1,
        chapter_title: chapterData?.section_name || 'Generated Chapter',
        content: `# ${chapterData?.section_name || 'Generated Chapter'}\n\nThis is mock chapter content generated for "${request.title}" by ${request.author}.\n\n## Overview\n\n${request.book_idea}\n\n## Key Points\n\n${chapterData?.section_ideas?.map(idea => `- ${idea}`).join('\n') || '- Mock content point 1\n- Mock content point 2\n- Mock content point 3'}\n\n## Detailed Analysis\n\nThis chapter provides comprehensive coverage of the topic with real-world examples, expert insights, and actionable recommendations. The content demonstrates the structure and quality you can expect from the actual book generation process.\n\n## Conclusion\n\nThis mock content shows how your book would be structured and formatted.`,
        word_count: 500,
        estimated_pages: 2
      };
      
      console.log('✅ Mock chapter generated:', mockResponse);
      return mockResponse;
    } catch (err) {
      console.error('❌ Demo content generation error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate content';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const generateCover = async (request: GenerateCoverRequest): Promise<GenerateCoverResponse | null> => {
    try {
      setLoading(true);
      setError(null);

      console.log('🚀 Generating mock cover...');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      return {
        cover_url: 'https://via.placeholder.com/400x600/6366f1/white?text=' + encodeURIComponent(request.title),
        design_description: `Mock ${request.design_style || 'modern'} cover with ${request.color_scheme || 'blue'} color scheme`,
        color_palette: ['#6366f1', '#8b5cf6', '#06b6d4']
      };
    } catch (err) {
      console.error('❌ Demo cover generation error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate cover';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const generatePDF = async (request: GeneratePDFRequest): Promise<GeneratePDFResponse | null> => {
    try {
      setLoading(true);
      setError(null);

      console.log('🚀 Generating mock PDF...');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2500));

      const totalWords = request.chapters.reduce((sum, chapter) => sum + (chapter.content?.length || 0) / 5, 0);
      const totalPages = Math.ceil(totalWords / 300);

      return {
        pdf_url: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
        total_pages: totalPages,
        word_count: Math.floor(totalWords),
        file_size_mb: 2.5
      };
    } catch (err) {
      console.error('❌ Demo PDF generation error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate PDF';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    generateContent,
    generateCover,
    generatePDF,
    loading,
    error,
  };
}