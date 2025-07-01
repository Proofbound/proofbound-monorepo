"""
Cover generation service using AI-generated images and PDF assembly.
"""

import base64
import requests
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from weasyprint import HTML
from .ai_client import get_openai_client, get_replicate_client, ask_llm


class CoverGenerator:
    """Service for generating book covers with AI-generated artwork."""
    
    @staticmethod
    def _ensure_image(src) -> Image.Image:
        """Convert various image sources to PIL Image."""
        if isinstance(src, Image.Image):
            return src
        if isinstance(src, (bytes, bytearray)):
            return Image.open(BytesIO(src))
        if hasattr(src, "read"):
            return Image.open(src)
        return Image.open(src)

    @staticmethod
    def inches_to_px(inches: float, dpi: int = 300) -> int:
        """Convert inches to pixels at given DPI."""
        return int(inches * dpi)

    @classmethod
    def create_cover_image(cls, front_img, back_img, spine_color, num_pages, 
                          paper_thickness, dpi, back_brightness=0.2, back_blur=2.0):
        """
        Create a combined cover image with front, back, and spine.
        
        Returns:
            Tuple of (canvas_image, dimensions_tuple)
        """
        # Dimensions in inches
        front_w_in, h_in = 6.125, 9.25
        back_w_in = front_w_in
        spine_w_in = num_pages * paper_thickness
        full_w_in = back_w_in + spine_w_in + front_w_in

        # Pixels
        full_w_px = cls.inches_to_px(full_w_in, dpi)
        h_px = cls.inches_to_px(h_in, dpi)
        back_w_px = cls.inches_to_px(back_w_in, dpi)
        spine_w_px = cls.inches_to_px(spine_w_in, dpi)
        front_w_px = cls.inches_to_px(front_w_in, dpi)

        canvas = Image.new("RGB", (full_w_px, h_px), "white")
        
        # Spine
        spine_rect = Image.new("RGB", (spine_w_px, h_px), spine_color)
        canvas.paste(spine_rect, (back_w_px, 0))

        # Back
        if back_img:
            back = cls._ensure_image(back_img).convert("RGB").resize((back_w_px, h_px))
            back = ImageEnhance.Brightness(back).enhance(back_brightness)
            if back_blur > 0:
                back = back.filter(ImageFilter.GaussianBlur(back_blur))
            canvas.paste(back, (0, 0))

        # Front
        if front_img:
            front = cls._ensure_image(front_img).convert("RGB").resize((front_w_px, h_px))
            canvas.paste(front, (back_w_px + spine_w_px, 0))

        return canvas, (full_w_in, h_in, back_w_in, spine_w_in, front_w_in)

    @classmethod
    def generate_cover_pdf(cls, title: str, author: str, book_idea: str, 
                          num_pages: int, include_spine_title: bool = False) -> bytes:
        """
        Generate a full 6x9 cover PDF (front/back/spine) via AI + assemble.
        
        Args:
            title: Book title
            author: Book author  
            book_idea: Book concept for AI generation
            num_pages: Number of pages for spine width calculation
            include_spine_title: Whether to include title on spine
            
        Returns:
            PDF bytes
        """
        openai_client = get_openai_client()
        replicate_client = get_replicate_client()
        
        # 1) Generate a front image via OpenAI Images
        front_prompt = (
            f"Generate a book cover (6×9 in) for a book titles '{title}' by the author {author} "
            f"about '{book_idea}'. Do not put any margins as this cover might be cropped. Be very creative. "
            f"The only texts in the cover should be the book title and the book author name."
        )
        img_resp = openai_client.images.generate(model="gpt-image-1", prompt=front_prompt)
        front_b64 = img_resp.data[0].b64_json
        if front_b64:
            front_bytes = base64.b64decode(front_b64)
        else:
            raise ValueError("Failed to generate front cover image")

        # 2) Generate a back illustration prompt via LLM + Replicate
        back_desc = ask_llm(f"Write a vivid, text‐free illustration description around the idea of '{book_idea}'.")
        replicate_out = replicate_client.run(
            "black-forest-labs/flux-dev",
            input={"prompt": back_desc, "aspect_ratio": "2:3"}
        )
        back_url = list(replicate_out)[0] if replicate_out else None
        if not back_url:
            raise ValueError("Failed to generate back cover image")
        back_img = requests.get(back_url).content

        canvas_img, (full_w_in, h_in, back_w_in, spine_w_in, front_w_in) = cls.create_cover_image(
            front_bytes,
            back_img,
            spine_color="#000000",
            back_brightness=0.2,
            back_blur=2.0,
            num_pages=num_pages,
            paper_thickness=0.00225,
            dpi=300,
        )

        # 4) Back‐cover text
        back_blurb = ask_llm(
            f"Write the text for the back cover of the book '{title}' "
            f"by the author '{author}' that is about '{book_idea}'. REPLY ONLY WITH THE BACK COVER TEXT."
        ) or ""
        back_desc_paragraphs = "".join(f"<p>{line}</p>" for line in back_blurb.split("\n"))

        # 5) Encode assembled canvas to base64
        buf = BytesIO()
        canvas_img.save(buf, format="PNG")
        bg_b64 = base64.b64encode(buf.getvalue()).decode()

        # 6) Conditionally include spine text
        spine_html = (
            f"<div class='spine-text'>{title}</div>"
            if include_spine_title else ""
        )

        # 7) Full HTML/CSS
        html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset='utf-8'>
            <style>
              @font-face {{
                font-family: "MyCustomFont";
                src: url("fonts/Kanit-Bold.ttf") format("truetype");
              }}
              @page {{ size:{full_w_in:.3f}in {h_in:.2f}in; margin:0 }}
              body {{ margin:0; padding:0 }}
              .cover {{ position:relative; width:{full_w_in:.3f}in; height:{h_in:.2f}in; }}
              .cover img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
              .front-text {{
                position:absolute;
                left:{(back_w_in+spine_w_in):.3f}in;
                top:0.5in;
                width:{front_w_in:.3f}in;
                text-align:center;
                font-size:48pt;
                font-family:MyCustomFont;
                color:white; stroke:black; stroke-width:2;
              }}
              .author-text {{
                position:absolute;
                left:{(back_w_in+spine_w_in):.3f}in;
                top:1.5in;
                width:{front_w_in:.3f}in;
                text-align:center;
                font-size:24pt;
                font-family:MyCustomFont;
                color:white; stroke:black; stroke-width:2;
              }}
              .spine-text {{
                position:absolute;
                top:50%; left:{(back_w_in + spine_w_in/2):.3f}in;
                transform:translate(-50%,-50%) rotate(90deg);
                transform-origin:center;
                font-size:10pt;
                font-family:MyCustomFont;
                color:white;
                white-space:nowrap;
              }}
              .back-text {{
                position:absolute;
                left:0; top:0.5in;
                width:{(back_w_in - 1 - spine_w_in/2):.3f}in;
                padding:0.6in;
                font-size:12pt;
                font-family:MyCustomFont;
                color:white;
              }}
              .back-text p {{
                text-indent:2em;
                margin:0 0 1em 0;
              }}
            </style>
          </head>
          <body>
            <div class='cover'>
              <img src='data:image/png;base64,{bg_b64}' />
              {spine_html}
              <div class="back-text" style="text-align: justify;">
                {back_desc_paragraphs}
              </div>
            </div>
          </body>
        </html>
        """

        # 8) Render PDF
        pdf_buf = BytesIO()
        HTML(string=html).write_pdf(pdf_buf)
        return pdf_buf.getvalue()