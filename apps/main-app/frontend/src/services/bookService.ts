/**
 * Book Service - Orchestrates AI book generation using HAL9 API
 */

import { supabase } from '../lib/supabase';
import JSZip from 'jszip';
import {
  BookGenerationRequest,
  ChapterGenerationRequest,
  BookOutline,
  BookMetadata,
  GeneratedChapter,
  AIGenerationResponse,
  BookProject
} from '../types/book';
import {
  generateQuartoProject,
  generateQuartoProjectWithContent,
  updateProjectWithChapter,
  createProjectFilename,
  getProjectStats
} from './projectGenerator';

export class BookService {
  private baseUrl: string;

  constructor() {
    const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
    if (!supabaseUrl) {
      throw new Error('VITE_SUPABASE_URL environment variable is not set');
    }
    this.baseUrl = `${supabaseUrl}/functions/v1`;
  }

  /**
   * Generate book outline using existing HAL9 API (generate-toc)
   */
  async generateOutline(request: BookGenerationRequest): Promise<BookOutline> {
    console.log('🚀 Calling generate-toc with:', {
      title: request.title,
      author: request.author,
      book_idea: request.bookIdea
    });

    const { data, error } = await supabase.functions.invoke('generate-toc', {
      body: {
        title: request.title,
        author: request.author,
        book_idea: request.bookIdea
      }
    });
    
    console.log('📥 generate-toc response:', { data, error });
    
    if (error) {
      console.error('Outline generation error details:', error);
      // For demo purposes, provide a fallback
      console.log('🔄 Using fallback outline for demo');
      return this.createFallbackOutline(request);
    }

    // Transform HAL9 TOC response to BookOutline format
    if (data && data.toc) {
      const outline: BookOutline = {
        book: {
          title: request.title,
          description: request.bookIdea,
          target_length: data.toc.length * 3000 // Estimate based on chapter count
        },
        chapters: data.toc.map((section: any, index: number) => ({
          id: index === 0 ? 'intro' : `chapter-${String(index + 1).padStart(2, '0')}`,
          title: section.section_name,
          description: section.section_ideas?.slice(0, 2)?.join('. ') || 'Chapter content description',
          target_words: this.parseEstimatedPages(section.estimated_pages),
          status: 'pending' as const,
          key_points: section.section_ideas || [],
          prompt_context: {
            focus: section.section_ideas?.[0] || 'Main chapter focus',
            tone: 'clear and engaging'
          },
          slug: this.slugify(section.section_name)
        }))
      };

      // Update total target length based on actual chapters
      outline.book.target_length = outline.chapters.reduce((sum, ch) => sum + ch.target_words, 0);
      
      return outline;
    }
    
    throw new Error('Invalid response from generate-toc function');
  }

  /**
   * Generate a single chapter using existing HAL9 API (generate-content)
   */
  async generateChapter(
    chapterRequest: ChapterGenerationRequest,
    outline: BookOutline
  ): Promise<GeneratedChapter> {
    // Transform outline to HAL9 format
    const toc = outline.chapters.map(chapter => ({
      section_name: chapter.title,
      section_ideas: chapter.key_points,
      estimated_pages: Math.ceil(chapter.target_words / 250).toString()
    }));

    const { data, error } = await supabase.functions.invoke('generate-content', {
      body: {
        title: chapterRequest.bookTitle,
        author: chapterRequest.author,
        book_idea: outline.book.description,
        toc,
        chapter_number: chapterRequest.chapterNumber,
        content_depth: 'polished',
        generation_mode: 'selective'
      }
    });
    
    if (error) {
      console.error('Chapter generation error details:', error);
      // For demo purposes, provide a fallback
      console.log('🔄 Using fallback chapter for demo');
      return this.createFallbackChapter(chapterRequest, outline);
    }

    // Transform HAL9 response to GeneratedChapter format
    if (data && data.content) {
      const generatedChapter: GeneratedChapter = {
        id: `chapter-${String(chapterRequest.chapterNumber).padStart(2, '0')}`,
        title: data.chapter_title || chapterRequest.chapterTitle,
        description: chapterRequest.chapterSummary,
        target_words: chapterRequest.targetWords || 3000,
        status: 'generated' as const,
        key_points: chapterRequest.keyPoints,
        prompt_context: {
          focus: chapterRequest.keyPoints[0] || 'Chapter focus',
          tone: chapterRequest.writingStyle || 'clear and engaging'
        },
        content: this.cleanChapterContent(data.content, data.chapter_title || chapterRequest.chapterTitle),
        word_count: data.word_count || this.estimateWordCount(data.content),
        generated_at: new Date().toISOString(),
        slug: this.slugify(data.chapter_title || chapterRequest.chapterTitle),
        chapterNumber: data.chapter_number || chapterRequest.chapterNumber
      };
      
      return generatedChapter;
    }
    
    throw new Error('Invalid response from generate-content function');
  }

  /**
   * Generate multiple chapters in sequence
   */
  async generateChapters(
    outline: BookOutline,
    metadata: BookMetadata,
    chapterIndices: number[] = [],
    onProgress?: (chapterIndex: number, chapter: GeneratedChapter) => void
  ): Promise<GeneratedChapter[]> {
    const chapters: GeneratedChapter[] = [];
    const indicesToGenerate = chapterIndices.length > 0 
      ? chapterIndices 
      : outline.chapters.map((_, index) => index);

    for (const chapterIndex of indicesToGenerate) {
      const chapter = outline.chapters[chapterIndex];
      if (!chapter) continue;

      try {
        const chapterRequest: ChapterGenerationRequest = {
          chapterNumber: chapterIndex + 1,
          chapterTitle: chapter.title,
          chapterSummary: chapter.description,
          keyPoints: chapter.key_points,
          bookTitle: metadata.title,
          author: metadata.author,
          previousChapters: chapters.map(ch => ch.title),
          bookTheme: metadata.topic,
          targetAudience: metadata.outline.book.description,
          writingStyle: chapter.prompt_context.tone,
          targetWords: chapter.target_words
        };

        const generatedChapter = await this.generateChapter(chapterRequest, outline);
        chapters.push(generatedChapter);

        if (onProgress) {
          onProgress(chapterIndex, generatedChapter);
        }

        // Small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Failed to generate chapter ${chapterIndex + 1}:`, error);
        // Continue with other chapters
      }
    }

    return chapters;
  }

  /**
   * Create downloadable Quarto project
   */
  async createQuartoProject(
    outline: BookOutline, 
    metadata: BookMetadata,
    generatedChapters: GeneratedChapter[] = []
  ): Promise<Blob> {
    const projectFiles = generatedChapters.length > 0
      ? generateQuartoProjectWithContent(outline, metadata, generatedChapters)
      : generateQuartoProject(outline, metadata);
    
    // Create ZIP file
    const zip = new JSZip();
    
    Object.entries(projectFiles).forEach(([filename, content]) => {
      // Create directory structure
      if (filename.includes('/')) {
        const dir = filename.substring(0, filename.lastIndexOf('/'));
        zip.folder(dir);
      }
      zip.file(filename, content);
    });
    
    return await zip.generateAsync({ 
      type: 'blob',
      compression: 'DEFLATE',
      compressionOptions: {
        level: 6
      }
    });
  }

  /**
   * Save book project to database
   */
  async saveProject(
    outline: BookOutline,
    metadata: BookMetadata,
    status: BookProject['status'] = 'outline_complete'
  ): Promise<string> {
    const userId = await this.getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const { data, error } = await supabase
      .from('book_projects')
      .insert({
        user_id: userId,
        title: metadata.title,
        author: metadata.author,
        book_idea: metadata.topic,
        topic: metadata.topic,
        outline,
        writing_style: metadata.outline.chapters[0]?.prompt_context.tone,
        target_audience: 'general readers',
        estimated_length: metadata.outline.book.target_length,
        status
      })
      .select('id')
      .single();

    if (error) {
      console.error('Database save error:', error);
      throw new Error('Failed to save project');
    }

    return data.id;
  }

  /**
   * Load book project from database
   */
  async loadProject(projectId: string): Promise<BookProject> {
    const { data, error } = await supabase
      .from('book_projects')
      .select('*')
      .eq('id', projectId)
      .single();

    if (error) {
      console.error('Database load error:', error);
      throw new Error('Failed to load project');
    }

    return data;
  }

  /**
   * List user's book projects
   */
  async listProjects(): Promise<BookProject[]> {
    const userId = await this.getCurrentUserId();
    if (!userId) {
      return [];
    }

    const { data, error } = await supabase
      .from('book_projects')
      .select('*')
      .eq('user_id', userId)
      .order('updated_at', { ascending: false });

    if (error) {
      console.error('Database list error:', error);
      return [];
    }

    return data || [];
  }

  /**
   * Update project status
   */
  async updateProjectStatus(projectId: string, status: BookProject['status']): Promise<void> {
    const { error } = await supabase
      .from('book_projects')
      .update({ 
        status, 
        updated_at: new Date().toISOString() 
      })
      .eq('id', projectId);

    if (error) {
      console.error('Status update error:', error);
      throw new Error('Failed to update project status');
    }
  }

  /**
   * Delete project
   */
  async deleteProject(projectId: string): Promise<void> {
    const { error } = await supabase
      .from('book_projects')
      .delete()
      .eq('id', projectId);

    if (error) {
      console.error('Delete project error:', error);
      throw new Error('Failed to delete project');
    }
  }

  /**
   * Get current authenticated user ID
   */
  private async getCurrentUserId(): Promise<string | null> {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      return user?.id || null;
    } catch {
      return null;
    }
  }

  /**
   * Parse estimated pages to word count (assuming ~250 words per page)
   */
  private parseEstimatedPages(estimatedPages: string): number {
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
   * Estimate word count from content
   */
  private estimateWordCount(content: string): number {
    if (!content) return 0;
    return content.split(/\s+/).filter(word => word.length > 0).length;
  }

  /**
   * Convert title to URL-friendly slug
   */
  private slugify(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }

  /**
   * Clean chapter content by removing redundant H1 title
   * 
   * TODO: Remove this fix when we move to direct API calls where we can control
   * the prompt to exclude H1 titles from generated content. This is a temporary
   * workaround for HAL9 API responses that include redundant H1 headings.
   */
  private cleanChapterContent(content: string, chapterTitle: string): string {
    if (!content) return content;
    
    // Split content into lines
    const lines = content.split('\n');
    
    // Check if the first non-empty line is an H1 that matches the chapter title
    let startIndex = 0;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line === '') continue; // Skip empty lines
      
      // Check if this line is an H1 heading that matches the chapter title
      if (line.startsWith('# ')) {
        const h1Title = line.substring(2).trim();
        if (h1Title === chapterTitle || h1Title.toLowerCase() === chapterTitle.toLowerCase()) {
          // Skip this H1 line and any immediately following empty lines
          startIndex = i + 1;
          while (startIndex < lines.length && lines[startIndex].trim() === '') {
            startIndex++;
          }
          break;
        }
      }
      
      // If we found a non-H1 line, stop looking
      break;
    }
    
    // Return the content without the redundant H1 title
    return lines.slice(startIndex).join('\n');
  }

  /**
   * Create a fallback outline for demo purposes when HAL9 API fails
   */
  private createFallbackOutline(request: BookGenerationRequest): BookOutline {
    console.log('🎭 Creating fallback outline for:', request.title);
    
    return {
      book: {
        title: request.title,
        description: request.bookIdea,
        target_length: 30000
      },
      chapters: [
        {
          id: 'intro',
          title: `Introduction to ${request.title}`,
          description: `Overview of ${request.bookIdea} and what readers will learn`,
          target_words: 3000,
          status: 'pending',
          key_points: [
            `Overview of ${request.bookIdea}`,
            'Setting the foundation',
            'What readers will learn',
            'Why this topic matters'
          ],
          prompt_context: {
            focus: 'Introduction and overview',
            tone: 'clear and engaging'
          },
          slug: 'introduction'
        },
        {
          id: 'chapter-02',
          title: 'Core Concepts and Fundamentals',
          description: 'Essential principles and foundational knowledge',
          target_words: 4000,
          status: 'pending',
          key_points: [
            'Essential principles and theories',
            'Key terminology and definitions',
            'Historical context and evolution',
            'Current state of the field'
          ],
          prompt_context: {
            focus: 'Foundational concepts',
            tone: 'clear and engaging'
          },
          slug: 'core-concepts'
        },
        {
          id: 'chapter-03',
          title: 'Practical Applications',
          description: 'Real-world implementation and case studies',
          target_words: 5000,
          status: 'pending',
          key_points: [
            'Real-world implementation strategies',
            'Case studies and examples',
            'Step-by-step methodologies',
            'Tools and resources'
          ],
          prompt_context: {
            focus: 'Practical implementation',
            tone: 'clear and engaging'
          },
          slug: 'practical-applications'
        },
        {
          id: 'chapter-04',
          title: 'Advanced Techniques',
          description: 'Expert-level strategies and optimization',
          target_words: 4500,
          status: 'pending',
          key_points: [
            'Expert-level strategies',
            'Optimization and best practices',
            'Troubleshooting common issues',
            'Scaling and growth considerations'
          ],
          prompt_context: {
            focus: 'Advanced techniques',
            tone: 'clear and engaging'
          },
          slug: 'advanced-techniques'
        },
        {
          id: 'chapter-05',
          title: 'Future Trends and Opportunities',
          description: 'Emerging developments and future outlook',
          target_words: 3500,
          status: 'pending',
          key_points: [
            'Emerging developments in the field',
            'Predicted future changes',
            'Opportunities for innovation',
            'Preparing for what\'s next'
          ],
          prompt_context: {
            focus: 'Future trends',
            tone: 'clear and engaging'
          },
          slug: 'future-trends'
        },
        {
          id: 'chapter-06',
          title: 'Conclusion and Next Steps',
          description: 'Key takeaways and actionable next steps',
          target_words: 2500,
          status: 'pending',
          key_points: [
            'Key takeaways and summary',
            'Action items for readers',
            'Additional resources',
            'Final thoughts and encouragement'
          ],
          prompt_context: {
            focus: 'Conclusion and next steps',
            tone: 'clear and engaging'
          },
          slug: 'conclusion'
        }
      ]
    };
  }

  /**
   * Create a fallback chapter for demo purposes when HAL9 API fails
   */
  private createFallbackChapter(chapterRequest: ChapterGenerationRequest, outline: BookOutline): GeneratedChapter {
    console.log('🎭 Creating fallback chapter:', chapterRequest.chapterNumber, chapterRequest.chapterTitle);
    
    const content = `## Introduction

${chapterRequest.chapterSummary}

This chapter explores the key concepts and practical applications related to ${chapterRequest.chapterTitle.toLowerCase()}. 

## Key Topics Covered

${chapterRequest.keyPoints.map(point => `### ${point}

This section would cover ${point.toLowerCase()} in comprehensive detail. In the full version, this content would be generated by HAL9 AI based on your specific requirements and the overall book context.

`).join('')}

## Summary

This chapter has provided an overview of ${chapterRequest.chapterTitle.toLowerCase()}. The key takeaways include understanding the fundamental concepts, practical applications, and how they fit into the broader context of ${outline.book.title}.

## Next Steps

In the next chapter, we'll explore [next topic] and how it builds upon the concepts covered here.

---

*Note: This is demonstration content generated when the HAL9 API is unavailable. The full version generates comprehensive, personalized content using advanced AI.*`;

    return {
      id: `chapter-${String(chapterRequest.chapterNumber).padStart(2, '0')}`,
      title: chapterRequest.chapterTitle,
      description: chapterRequest.chapterSummary,
      target_words: chapterRequest.targetWords || 3000,
      status: 'generated',
      key_points: chapterRequest.keyPoints,
      prompt_context: {
        focus: chapterRequest.keyPoints[0] || 'Chapter focus',
        tone: chapterRequest.writingStyle || 'clear and engaging'
      },
      content,
      word_count: this.estimateWordCount(content),
      generated_at: new Date().toISOString(),
      slug: this.slugify(chapterRequest.chapterTitle),
      chapterNumber: chapterRequest.chapterNumber
    };
  }

  /**
   * Check if HAL9 is properly configured
   */
  async checkConfiguration(): Promise<{ configured: boolean; error?: string }> {
    const hal9Token = import.meta.env.VITE_HAL9_TOKEN;
    
    if (!hal9Token) {
      return {
        configured: false,
        error: 'HAL9 token not configured. Please set VITE_HAL9_TOKEN environment variable.'
      };
    }

    try {
      // Test connection with a simple request
      const testResponse = await supabase.functions.invoke('generate-outline', {
        body: {
          title: 'Test Book',
          author: 'Test Author',
          bookIdea: 'Test book idea',
          topic: 'Testing'
        }
      });

      return { configured: true };
    } catch (error) {
      return {
        configured: false,
        error: `HAL9 connection test failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Generate project filename for download
   */
  createDownloadFilename(metadata: BookMetadata): string {
    return createProjectFilename(metadata);
  }

  /**
   * Get project statistics
   */
  getProjectStatistics(outline: BookOutline, generatedChapters: GeneratedChapter[] = []) {
    const totalChapters = outline.chapters.length;
    const completedChapters = generatedChapters.length;
    const estimatedWords = outline.book.target_length;
    const actualWords = generatedChapters.reduce((sum, ch) => sum + ch.word_count, 0);

    return {
      totalChapters,
      completedChapters,
      completionPercentage: Math.round((completedChapters / totalChapters) * 100),
      estimatedWords,
      actualWords,
      averageWordsPerChapter: completedChapters > 0 ? Math.round(actualWords / completedChapters) : 0
    };
  }
}

// Create singleton instance
export const bookService = new BookService();