"""
PDF assembly module for creating children's storybook PDFs.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PDFBuilder:
    """Handles PDF creation from story data and images"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "storybook_pdfs"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Check for available PDF libraries
        self.reportlab_available = False
        self.fpdf_available = False
        self.img2pdf_available = False
        
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            self.reportlab_available = True
        except ImportError:
            logger.warning("ReportLab not available")
        
        try:
            from fpdf import FPDF
            self.fpdf_available = True
        except ImportError:
            logger.warning("FPDF not available")
        
        try:
            import img2pdf
            self.img2pdf_available = True
        except ImportError:
            logger.warning("img2pdf not available")
        
        # PIL is required for final fallback
        try:
            from PIL import Image  # noqa: F401
            self.pil_available = True
        except Exception:
            self.pil_available = False
    
    def create_pdf(self, story_data: Dict, images: Dict[str, str], output_filename: str = "storybook.pdf") -> Optional[str]:
        """
        Create a PDF from story data and images
        
        Args:
            story_data: Story data dictionary
            images: Dictionary mapping page numbers to image paths
            output_filename: Name of the output PDF file
            
        Returns:
            Path to created PDF or None if creation fails
        """
        try:
            output_path = self.temp_dir / output_filename
            
            # Try different PDF creation methods with fallback chain
            result_path: Optional[str] = None
            errors: list[str] = []
            
            if self.reportlab_available:
                try:
                    result_path = self._create_pdf_reportlab(story_data, images, output_path)
                except Exception as e:
                    errors.append(f"ReportLab error: {e}")
                    logger.error(f"ReportLab error: {e}")
            
            if (not result_path or not Path(result_path).exists()) and self.fpdf_available:
                try:
                    result_path = self._create_pdf_fpdf(story_data, images, output_path)
                except Exception as e:
                    errors.append(f"FPDF error: {e}")
                    logger.error(f"FPDF error: {e}")
            
            if (not result_path or not Path(result_path).exists()) and self.img2pdf_available:
                try:
                    result_path = self._create_pdf_img2pdf(story_data, images, output_path)
                except Exception as e:
                    errors.append(f"img2pdf error: {e}")
                    logger.error(f"img2pdf error: {e}")
            
            # Final fallback: PIL-only PDF assembly
            if (not result_path or not Path(result_path).exists()) and getattr(self, 'pil_available', False):
                try:
                    result_path = self._create_pdf_pil(story_data, images, output_path)
                except Exception as e:
                    errors.append(f"PIL fallback error: {e}")
                    logger.error(f"PIL fallback error: {e}")

            if result_path and Path(result_path).exists():
                return result_path
            
            logger.error("PDF creation failed. " + ("; ".join(errors) if errors else "No engines available"))
            return None

    def _create_pdf_pil(self, story_data: Dict, images: Dict[str, str], output_path: Path) -> Optional[str]:
        """Create a PDF using only Pillow (broadest compatibility in constrained envs)."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # A4 at ~150 DPI
            page_w, page_h = 1240, 1754
            margin = 80
            image_area_h = 900  # top area for image
            
            def get_img_for_page(page_number: int) -> Optional[Image.Image]:
                path = images.get(page_number) or images.get(str(page_number))
                if path and Path(path).exists():
                    try:
                        im = Image.open(path).convert('RGB')
                        # Fit into image area keeping aspect ratio
                        max_w, max_h = page_w - 2*margin, image_area_h - margin
                        im.thumbnail((max_w, max_h))
                        return im
                    except Exception as e:
                        logger.warning(f"PIL could not load image for page {page_number}: {e}")
                return None
            
            def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
                words = text.split()
                lines, line = [], []
                for w in words:
                    test = (' '.join(line+[w])).strip()
                    if draw.textlength(test, font=font) <= max_width:
                        line.append(w)
                    else:
                        if line:
                            lines.append(' '.join(line))
                        line = [w]
                if line:
                    lines.append(' '.join(line))
                return lines
            
            # Fonts
            try:
                title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
                body_font = ImageFont.truetype("DejaVuSans.ttf", 28)
                small_font = ImageFont.truetype("DejaVuSans.ttf", 22)
            except Exception:
                title_font = ImageFont.load_default()
                body_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Build pages: title + 5 story pages
            pil_pages: list[Image.Image] = []
            
            # Title page
            title_img = Image.new('RGB', (page_w, page_h), 'white')
            d = ImageDraw.Draw(title_img)
            title = story_data.get('title', 'Storybook')
            tw = d.textlength(title, font=title_font)
            d.text(((page_w - tw)//2, page_h//3), title, fill='darkblue', font=title_font)
            d.text((margin, page_h//3 + 120), "A Children's Story", fill='gray', font=body_font)
            pil_pages.append(title_img)
            
            # Story pages
            for page in story_data.get('pages', []):
                canvas = Image.new('RGB', (page_w, page_h), 'white')
                draw = ImageDraw.Draw(canvas)
                pnum = page.get('page', 1)
                # image
                im = get_img_for_page(pnum)
                if im:
                    x = (page_w - im.width)//2
                    y = margin
                    canvas.paste(im, (x, y))
                # text
                text_top = (margin + image_area_h) if im else margin
                text_area_w = page_w - 2*margin
                draw.text((margin, text_top), f"Page {pnum}", fill='black', font=small_font)
                y_cursor = text_top + 50
                lines = wrap_text(draw, page.get('text', ''), body_font, text_area_w)
                for line in lines:
                    draw.text((margin, y_cursor), line, fill='black', font=body_font)
                    y_cursor += 44
                pil_pages.append(canvas)
            
            # Save multi-page PDF
            if pil_pages:
                pil_pages[0].save(str(output_path), save_all=True, append_images=pil_pages[1:], format='PDF')
            
            return str(output_path) if output_path.exists() else None
        except Exception as e:
            logger.error(f"PIL PDF creation failed: {e}")
            return None
    
    def _create_pdf_reportlab(self, story_data: Dict, images: Dict[str, str], output_path: Path) -> Optional[str]:
        """Create PDF using ReportLab"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            def _get_image_path_for_page(images_map: Dict, page_number: int) -> Optional[str]:
                """Return existing image path for the page regardless of key type (int/str)."""
                # Try int key first
                path = images_map.get(page_number)
                if isinstance(path, str) and Path(path).exists():
                    return path
                # Then try string key
                path = images_map.get(str(page_number))
                if isinstance(path, str) and Path(path).exists():
                    return path
                return None
            
            # Create document
            doc = SimpleDocTemplate(str(output_path), pagesize=A4, 
                                  rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            page_style = ParagraphStyle(
                'CustomPage',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=12,
                alignment=TA_LEFT,
                leading=20
            )
            
            # Build content
            story = []
            
            # Title page
            story.append(Paragraph(story_data['title'], title_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Characters section
            if story_data.get('characters'):
                story.append(Paragraph("Characters", styles['Heading2']))
                for character in story_data['characters']:
                    char_text = f"<b>{character['name']}</b>: {character['description']}"
                    story.append(Paragraph(char_text, page_style))
                story.append(Spacer(1, 0.3*inch))
            
            story.append(PageBreak())
            
            # Story pages
            for page_data in story_data['pages']:
                page_num = page_data['page']
                
                # Add image if available
                img_path = _get_image_path_for_page(images, page_num)
                if img_path:
                    try:
                        img = RLImage(img_path, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                    except Exception as e:
                        logger.warning(f"Could not add image for page {page_num}: {e}")
                else:
                    # Add placeholder text if no image
                    story.append(Paragraph(f"[Image for Page {page_num}]", styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
                
                # Add page text
                page_text = f"<b>Page {page_num}</b><br/><br/>{page_data['text']}"
                story.append(Paragraph(page_text, page_style))
                story.append(Spacer(1, 0.3*inch))
                
                # Add page break (except for last page)
                if page_num < len(story_data['pages']):
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            if output_path.exists():
                return str(output_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"ReportLab PDF creation failed: {e}")
            return None
    
    def _create_pdf_fpdf(self, story_data: Dict, images: Dict[str, str], output_path: Path) -> Optional[str]:
        """Create PDF using FPDF"""
        try:
            from fpdf import FPDF
            from pathlib import Path as _Path
            
            def _get_image_path_for_page(images_map: Dict, page_number: int) -> Optional[str]:
                path = images_map.get(page_number)
                if isinstance(path, str) and _Path(path).exists():
                    return path
                path = images_map.get(str(page_number))
                if isinstance(path, str) and _Path(path).exists():
                    return path
                return None
            
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Add title page
            pdf.add_page()
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 10, story_data['title'], 0, 1, 'C')
            pdf.ln(10)
            
            # Add characters
            if story_data.get('characters'):
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, 'Characters', 0, 1, 'L')
                pdf.ln(5)
                
                pdf.set_font('Arial', '', 12)
                for character in story_data['characters']:
                    pdf.cell(0, 8, f"{character['name']}: {character['description']}", 0, 1, 'L')
                pdf.ln(10)
            
            # Add story pages
            for page_data in story_data['pages']:
                page_num = page_data['page']
                pdf.add_page()
                
                # Add image if available
                img_path = _get_image_path_for_page(images, page_num)
                if img_path:
                    try:
                        # Fit image within page width keeping aspect ratio
                        page_w = pdf.w - 2 * pdf.l_margin
                        # Approximate height for a 3:2 area
                        img_h = page_w * 2 / 3
                        pdf.image(img_path, x=pdf.l_margin, y=None, w=page_w, h=img_h)
                        pdf.ln(5)
                    except Exception as e:
                        logger.warning(f"Could not add image for page {page_num}: {e}")
                
                # Add page text
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f"Page {page_num}", 0, 1, 'L')
                pdf.ln(5)
                
                pdf.set_font('Arial', '', 12)
                # Split text into lines that fit the page
                text = page_data['text']
                lines = self._wrap_text_fpdf(text, 80)  # 80 characters per line
                for line in lines:
                    pdf.cell(0, 8, line, 0, 1, 'L')
                pdf.ln(5)
            
            # Save PDF
            pdf.output(str(output_path))
            
            if output_path.exists():
                return str(output_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"FPDF creation failed: {e}")
            return None
    
    def _create_pdf_img2pdf(self, story_data: Dict, images: Dict[str, str], output_path: Path) -> Optional[str]:
        """Create PDF using img2pdf (simpler but less flexible)"""
        try:
            import img2pdf
            
            # Create a list of images in order
            image_paths = []
            
            # Add title page (we'll create a simple one)
            title_page_path = self._create_title_page(story_data)
            if title_page_path:
                image_paths.append(title_page_path)
            
            # Add story pages with images
            for page_data in story_data['pages']:
                page_num = page_data['page']
                
                if str(page_num) in images and Path(images[str(page_num)]).exists():
                    image_paths.append(images[str(page_num)])
                else:
                    # Create a placeholder page
                    placeholder_path = self._create_placeholder_page(page_data, page_num)
                    if placeholder_path:
                        image_paths.append(placeholder_path)
            
            # Convert images to PDF
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(image_paths))
            
            if output_path.exists():
                return str(output_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"img2pdf creation failed: {e}")
            return None
    
    def _create_title_page(self, story_data: Dict) -> Optional[str]:
        """Create a simple title page image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image
            img = Image.new('RGB', (1200, 1600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to load a font
            try:
                title_font = ImageFont.truetype("arial.ttf", 72)
                subtitle_font = ImageFont.truetype("arial.ttf", 36)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Draw title
            title = story_data['title']
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1200 - title_width) // 2
            draw.text((title_x, 600), title, fill='darkblue', font=title_font)
            
            # Draw subtitle
            subtitle = "A Children's Story"
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (1200 - subtitle_width) // 2
            draw.text((subtitle_x, 700), subtitle, fill='gray', font=subtitle_font)
            
            # Draw decorative elements
            for i in range(5):
                x = 200 + i * 200
                y = 800 + i * 50
                draw.ellipse([x, y, x + 50, y + 50], fill='lightblue', outline='blue')
            
            # Save image
            title_path = self.temp_dir / "title_page.png"
            img.save(title_path, 'PNG')
            return str(title_path)
            
        except Exception as e:
            logger.error(f"Title page creation failed: {e}")
            return None
    
    def _create_placeholder_page(self, page_data: Dict, page_num: int) -> Optional[str]:
        """Create a placeholder page with text"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image
            img = Image.new('RGB', (1200, 1600), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # Try to load a font
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                text_font = ImageFont.truetype("arial.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Draw page number
            page_title = f"Page {page_num}"
            title_bbox = draw.textbbox((0, 0), page_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1200 - title_width) // 2
            draw.text((title_x, 100), page_title, fill='darkblue', font=title_font)
            
            # Draw page text
            text = page_data['text']
            lines = self._wrap_text_pil(text, text_font, 1000)
            
            y_start = 300
            for line in lines:
                line_bbox = draw.textbbox((0, 0), line, font=text_font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (1200 - line_width) // 2
                draw.text((line_x, y_start), line, fill='black', font=text_font)
                y_start += 40
            
            # Save image
            placeholder_path = self.temp_dir / f"placeholder_page_{page_num}.png"
            img.save(placeholder_path, 'PNG')
            return str(placeholder_path)
            
        except Exception as e:
            logger.error(f"Placeholder page creation failed: {e}")
            return None
    
    def _wrap_text_fpdf(self, text: str, max_chars: int) -> List[str]:
        """Wrap text for FPDF"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _wrap_text_pil(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text for PIL"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Rough estimate of text width
            if len(test_line) * 12 <= max_width:  # Rough estimate
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines[:15]  # Limit to 15 lines
