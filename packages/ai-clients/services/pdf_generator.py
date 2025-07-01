"""
PDF generation service using WeasyPrint.
"""

from io import BytesIO
from typing import List
import pypandoc
from weasyprint import HTML
from bs4 import BeautifulSoup
from models.section_model import Section

# Ensure Pandoc is installed for markdown → HTML conversion
try:
    pypandoc.get_pandoc_version()
except OSError:
    pypandoc.download_pandoc()


class PDFGenerator:
    """Service for generating PDFs from markdown content."""
    
    @staticmethod
    def markdown_to_html(md: str) -> str:
        """Convert markdown to HTML."""
        return pypandoc.convert_text(md, 'html', format='md')
    
    @staticmethod
    def generate_pdf_from_html(html: str) -> bytes:
        """Generate PDF bytes from HTML string."""
        buf = BytesIO()
        HTML(string=html).write_pdf(buf)
        return buf.getvalue()
    
    @classmethod
    def generate_book_pdf(cls, title: str, author: str, toc: List[Section], markdown: str) -> bytes:
        """
        Convert Markdown + TOC + metadata → formatted PDF bytes.
        
        Args:
            title: Book title
            author: Book author
            toc: Table of contents sections
            markdown: Book content in markdown format
            
        Returns:
            PDF bytes
        """
        # 1) Markdown → HTML
        html_body = cls.markdown_to_html(markdown)
        
        # 2) Inject IDs for TOC
        soup = BeautifulSoup(html_body, "html.parser")
        for i, h2 in enumerate(soup.find_all("h2"), start=1):
            h2["id"] = f"sec{i}"
        body = str(soup)

        # 3) Build TOC HTML/CSS
        toc_items = []
        for i, sec in enumerate(toc, start=1):
            toc_items.append(
                f"<li><span class='toc-label'>{sec.section_name}</span>"
                f"<span class='pagenum'></span></li>"
            )
        toc_html = "<div class='toc'><h1>Table of Contents</h1><ol>" + "".join(toc_items) + "</ol></div>"
        toc_css = "\n".join(
            f".toc ol li:nth-child({i}) .pagenum:after {{content: leader(\".\") target-counter(\"#sec{i}\", page);}}"
            for i in range(1, len(toc) + 1)
        )

        # 4) Full HTML template 
        full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <meta charset="utf-8">
                  <style>
                    /*--- Define named pages ---*/
                    @page titlepage {{
                      size: 6in 9in;
                      margin: 0;
                      @top-center {{ content: none; }}
                      @bottom-center {{ content: none; }}
                    }}
                    @page blank {{
                      size: 6in 9in;
                      margin: 0;
                      @top-center {{ content: none; }}
                      @bottom-center {{ content: none; }}
                    }}
                    @page toc {{
                      size: 6in 9in;
                      margin: 1in;
                      @top-center {{ content: none; }}
                      @bottom-center {{ content: "Page " counter(page); }}
                    }}
                    /* default content pages */
                    @page {{
                      size: 6in 9in;
                      margin: 1in;
                      @top-center {{
                        content: "{title}";
                        font-size: 8pt;
                        font-family: Georgia, serif;
                      }}
                      @bottom-center {{
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 8pt;
                        font-family: Georgia, serif;
                      }}
                    }}

                    html, body {{ margin:0; padding:0; }}
                    /*--- Title Page ---*/
                    .titlepage {{
                      page: titlepage;
                      display: flex;
                      justify-content: center;
                      align-items: center;
                      flex-direction: column;
                      height: 9in;
                      page-break-after: always;
                    }}

                    .titlepage h1 {{
                        display: inline-block;
                        text-align: center;
                        overflow-wrap: break-word;
                        max-width: 90%;
                        font-family: Georgia, serif; font-size:24pt; margin:0;
                        margin: 0;
                    }}
                    .titlepage h2 {{
                        display: inline-block;
                        text-align: center;
                        overflow-wrap: break-word;
                        max-width: 90%;
                        font-family: Georgia, serif; font-size:14pt; margin-top: 1em;
                        margin: 0;
                    }}

                    /*--- Blank pages (2 & 4) ---*/
                    .blank {{
                      page: blank;
                      page-break-after: always;
                    }}

                    /*--- TOC page (3) ---*/
                    .toc {{
                      page: toc;
                      page-break-after: always;
                      font-family:Georgia, serif;
                      font-size:10pt;
                    }}
                    .toc h1 {{ text-align:center; margin-bottom:1em; }}
                    .toc ol {{
                      list-style:none;
                      counter-reset: item;
                      padding:0;
                    }}
                    .toc li {{
                    counter-increment: item;
                    margin-bottom: 0.5em;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    flex-wrap: wrap;
                    }}
                    .toc-label {{
                    flex: 1 1 auto;
                    padding-right: 1em;
                    word-wrap: break-word;
                    max-width: 80%;
                    }}
                    .toc-label::before {{
                      content: counter(item) ". ";
                    }}
                    .pagenum {{ /* filled via CSS below */ }}
                    {toc_css}

                    /*--- Actual book content starts on page 5 ---*/
                    .content {{
                      font-family:Georgia, serif;
                      font-size:10pt;
                      line-height:1.3;
                      text-align:justify;
                    }}
                    .content h2 {{
                      page-break-before: always;
                      text-align: center;
                    }}
                  </style>
                </head>
                <body>
                  <!-- Page 1: Title -->
                  <div class="titlepage">
                    <h1>{title}</h1>
                    <h2>{author}</h2>
                  </div>

                  <!-- Page 2: blank -->
                  <div class="blank"></div>

                  <!-- Page 3: TOC -->
                  {toc_html}

                  <!-- Page 4: blank -->
                  <div class="blank"></div>

                  <!-- Page 5+: content -->
                  <div class="content">
                    {body}
                  </div>
                </body>
                </html>
                """

        return cls.generate_pdf_from_html(full_html)