/**
 * Quarto Configuration Templates
 * Generates Quarto project files for book generation
 */

export interface BookMetadata {
  title: string;
  author: string;
  topic: string;
  outline: BookOutline;
  theme?: string;
  format?: 'html' | 'pdf' | 'epub' | 'all';
  description?: string;
  publishingDate?: string;
  publisher?: string;
  isbn?: string;
  websiteUrl?: string;
}

export interface BookOutline {
  book: {
    title: string;
    description: string;
    target_length: number;
  };
  chapters: Chapter[];
}

export interface Chapter {
  id: string;
  title: string;
  description: string;
  target_words: number;
  status: 'pending' | 'generated' | 'edited';
  key_points: string[];
  prompt_context: {
    focus: string;
    tone: string;
  };
  content?: string;
  slug?: string;
}

export interface GeneratedChapter extends Chapter {
  content: string;
  word_count: number;
  generated_at: string;
}

/**
 * Generate the main _quarto.yml configuration file
 */
export function generateQuartoConfig(metadata: BookMetadata): string {
  const { title, author, outline, theme = 'cosmo', publishingDate, websiteUrl } = metadata;
  
  // Create chapter file references
  const chapterFiles = outline.chapters.map((chapter, index) => {
    const chapterNum = String(index + 1).padStart(2, '0');
    const slug = chapter.slug || slugify(chapter.title);
    return `    - chapters/${chapterNum}-${slug}.qmd`;
  }).join('\n');

  return `project:
  type: book
  title: "${title}"

book:
  title: "${title}"
  author: "${author}"
  date: "${publishingDate || new Date().toISOString().split('T')[0]}"
  search: true
  downloads: [pdf, epub]
  chapters:
    - index.qmd
    - preface.qmd
${chapterFiles}
    - conclusion.qmd
    - references.qmd

bibliography: references.bib
nocite: '@*'

format:
  html:
    theme: ${theme}
    toc: true
    toc-depth: 3
    number-sections: true
    page-footer: "© ${new Date().getFullYear()} ${author}"
    site-url: "${websiteUrl || ''}"
    css: styles.css
  pdf:
    papersize: "Letter"
    mainfont: "Georgia"
    sansfont: "Arial"
    toc: true
    toc-depth: 2
    documentclass: scrbook
    geometry: 
      - margin=1in
      - paperwidth=6in
      - paperheight=9in
    standalone: true
    keep-tex: false
    number-sections: true
    colorlinks: true
  epub:
    toc: true
    toc-depth: 2
    number-sections: true
    epub-cover-image: cover.png
`;
}

/**
 * Generate the index.qmd file (book homepage)
 */
export function generateIndexFile(metadata: BookMetadata): string {
  const { title, author, topic, outline } = metadata;
  
  return `---
title: "${title}"
author: "${author}"
---

# ${title}

by **${author}**

## About This Book

${outline.book.description}

This book consists of ${outline.chapters.length} chapters covering:

${outline.chapters.map((chapter, index) => 
  `${index + 1}. **${chapter.title}** - ${chapter.description}`
).join('\n')}

## How to Use This Book

This book is designed to be read sequentially, with each chapter building upon the previous ones. However, you can also jump to specific chapters that interest you most.

## Target Audience

This book is written for readers who want to understand ${topic} in depth, regardless of their background level.

---

*Total estimated length: ~${Math.round(outline.book.target_length / 1000)}k words*
`;
}

/**
 * Generate preface.qmd file
 */
export function generatePrefaceFile(metadata: BookMetadata): string {
  const { title, author, topic } = metadata;
  
  return `---
title: "Preface"
---

# Preface

Welcome to *${title}*. This book represents a comprehensive exploration of ${topic}, designed to provide you with both theoretical understanding and practical insights.

## Why This Book?

In today's rapidly evolving world, understanding ${topic} has become increasingly important. This book aims to bridge the gap between complex concepts and practical application, making this knowledge accessible to everyone.

## What You'll Learn

By the end of this book, you will:

- Have a solid foundation in the core concepts of ${topic}
- Understand how to apply these concepts in real-world situations
- Be equipped with the knowledge to continue learning and growing in this field
- Have practical tools and frameworks you can use immediately

## How This Book Is Organized

This book is structured to take you on a journey from foundational concepts to advanced applications. Each chapter builds upon the previous ones, creating a comprehensive learning experience.

## Acknowledgments

I would like to thank all the researchers, practitioners, and thought leaders whose work has contributed to our understanding of ${topic}. Their insights and discoveries form the foundation upon which this book is built.

## A Note to Readers

This book is designed to be practical and actionable. Don't just read it—engage with it. Take notes, try the exercises, and most importantly, apply what you learn.

---

*${author}*  
*${new Date().getFullYear()}*
`;
}

/**
 * Generate a chapter file
 */
export function generateChapterFile(chapter: Chapter, chapterNumber: number, bookTitle: string): string {
  const slug = chapter.slug || slugify(chapter.title);
  
  return `---
title: "${chapter.title}"
---

# ${chapter.title}

${chapter.content || generatePlaceholderContent(chapter, chapterNumber)}
`;
}

/**
 * Generate placeholder content for a chapter
 */
function generatePlaceholderContent(chapter: Chapter, chapterNumber: number): string {
  return `## Overview

${chapter.description}

## Key Topics

This chapter will cover:

${chapter.key_points.map(point => `- ${point}`).join('\n')}

## Chapter Content

*This chapter content will be generated by AI based on the outline and key topics above.*

### Introduction

*Introduction content will appear here...*

### Main Content

*Main chapter content will appear here...*

### Summary

*Chapter summary will appear here...*

---

*Target length: ~${chapter.target_words} words*
`;
}

/**
 * Generate conclusion.qmd file
 */
export function generateConclusionFile(metadata: BookMetadata): string {
  const { title, topic, outline } = metadata;
  
  return `---
title: "Conclusion"
---

# Conclusion

As we reach the end of *${title}*, let's reflect on the journey we've taken together through the world of ${topic}.

## What We've Covered

Throughout this book, we've explored:

${outline.chapters.map((chapter, index) => 
  `- **Chapter ${index + 1}**: ${chapter.title}`
).join('\n')}

## Key Takeaways

The most important insights from this book include:

1. **Foundation Understanding**: We've built a solid foundation in ${topic}
2. **Practical Application**: We've seen how these concepts apply in real-world scenarios
3. **Future Thinking**: We've explored where this field is heading

## Next Steps

Your learning journey doesn't end here. Consider these next steps:

- **Practice**: Apply what you've learned in your own projects
- **Stay Updated**: Keep up with the latest developments in ${topic}
- **Connect**: Join communities of practitioners and learners
- **Teach**: Share your knowledge with others

## Final Thoughts

Understanding ${topic} is not just about acquiring knowledge—it's about developing a new way of thinking and approaching problems. As you continue to grow and learn, remember that mastery comes through practice and continuous learning.

Thank you for taking this journey with me. I hope this book serves as a valuable resource that you'll return to again and again.

## Resources for Continued Learning

- [Additional resources will be listed here]
- [Relevant websites and communities]
- [Recommended further reading]

---

*The end is just the beginning of your journey.*
`;
}

/**
 * Generate references.qmd file
 */
export function generateReferencesFile(): string {
  return `---
title: "References"
---

# References

::: {#refs}
:::

## Additional Resources

### Books

- [Recommended books will be listed here]

### Articles and Papers

- [Relevant academic papers and articles]

### Websites and Online Resources

- [Useful websites and online tools]

### Tools and Software

- [Recommended tools and software packages]
`;
}

/**
 * Generate references.bib file
 */
export function generateBibliographyFile(): string {
  return `@book{sample2024,
  title={Sample Reference},
  author={Sample Author},
  year={2024},
  publisher={Sample Publisher}
}

@article{example2024,
  title={Example Article},
  author={Example Author},
  journal={Example Journal},
  year={2024},
  volume={1},
  pages={1--10}
}
`;
}

/**
 * Generate basic CSS file for styling
 */
export function generateStylesFile(): string {
  return `/* Custom styles for the book */

body {
  font-family: Georgia, serif;
  line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
  font-family: Arial, sans-serif;
  font-weight: 600;
}

.chapter-intro {
  font-style: italic;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-left: 4px solid #007bff;
}

.key-takeaway {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 0.25rem;
  padding: 1rem;
  margin: 1.5rem 0;
}

.key-takeaway::before {
  content: "💡 Key Takeaway: ";
  font-weight: bold;
  color: #856404;
}

blockquote {
  border-left: 4px solid #6c757d;
  padding-left: 1rem;
  margin-left: 0;
  font-style: italic;
  color: #6c757d;
}

code {
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.9em;
}

pre code {
  background-color: transparent;
  padding: 0;
}
`;
}

/**
 * Generate README.md file for the project
 */
export function generateReadmeFile(metadata: BookMetadata): string {
  const { title, author, topic } = metadata;
  
  return `# ${title}

by **${author}**

## About

${topic}

## Building This Book

This book is built using [Quarto](https://quarto.org/). To render the book:

\`\`\`bash
# Install Quarto (if not already installed)
# Visit: https://quarto.org/docs/get-started/

# Render to HTML
quarto render --to html

# Render to PDF
quarto render --to pdf

# Render to EPUB
quarto render --to epub

# Render all formats
quarto render
\`\`\`

## Chapter Status

${metadata.outline.chapters.map((chapter, index) => 
  `- [ ] Chapter ${index + 1}: ${chapter.title}`
).join('\n')}

## Project Structure

\`\`\`
├── _quarto.yml          # Quarto configuration
├── index.qmd            # Book homepage
├── preface.qmd          # Preface
├── chapters/            # Chapter files
│   ├── 01-*.qmd
│   ├── 02-*.qmd
│   └── ...
├── conclusion.qmd       # Conclusion
├── references.qmd       # References
├── references.bib       # Bibliography
├── styles.css          # Custom styles
└── README.md           # This file
\`\`\`

## Output

The rendered book will be available in the \`_book/\` directory after running \`quarto render\`.

---

Generated with Proofbound AI Book Generator
`;
}

/**
 * Generate .gitignore file
 */
export function generateGitignoreFile(): string {
  return `# Quarto output
_book/
_site/
.quarto/

# R
.Rproj.user
.Rhistory
.RData
.Ruserdata
*.Rproj

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/

# macOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# LaTeX
*.aux
*.log
*.synctex.gz
*.toc
*.out
*.fdb_latexmk
*.fls

# Temporary files
*.tmp
*.temp
`;
}

/**
 * Convert title to URL-friendly slug
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
    .replace(/^-+|-+$/g, ''); // Remove leading and trailing hyphens
}