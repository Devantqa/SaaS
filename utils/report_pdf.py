import os
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

class PdfReport:
    """
    Simple PDF report with a consistent API: add_title(), add_step(), add_info(), save()
    Output: artifacts/TestSummary.pdf
    """
    def __init__(self, out_path="artifacts/TestSummary.pdf"):
        self.out_path = out_path
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        self.buffer = io.BytesIO()
        self.c = canvas.Canvas(self.buffer, pagesize=A4)
        self.width, self.height = A4
        self.cursor_y = self.height - 2*cm
        self._add_header_meta()

    def _add_header_meta(self):
        self.c.setTitle("Automation Test Summary")
        self.c.setAuthor("Automation")
        self.c.setSubject("Selenium Pytest Report")

    def _flush_page(self):
        self.c.showPage()
        self.cursor_y = self.height - 2*cm

    def _write_wrapped(self, text, font="Helvetica", size=11, leading=14, max_width=None):
        self.c.setFont(font, size)
        if max_width is None:
            max_width = self.width - 4*cm
        words = text.split()
        line = ""
        for w in words:
            candidate = (line + " " + w).strip()
            if self.c.stringWidth(candidate, font, size) <= max_width:
                line = candidate
            else:
                self.c.drawString(2*cm, self.cursor_y, line)
                self.cursor_y -= leading
                if self.cursor_y < 3*cm:
                    self._flush_page()
                line = w
        if line:
            self.c.drawString(2*cm, self.cursor_y, line)
            self.cursor_y -= leading
            if self.cursor_y < 3*cm:
                self._flush_page()

    def add_title(self, text):
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(2*cm, self.cursor_y, text)
        self.cursor_y -= 18
        self._write_wrapped(f"Generated: {datetime.datetime.now().isoformat(timespec='seconds')}", size=9, leading=12)
        self.cursor_y -= 6

    def add_step(self, title, description=None, screenshot_path=None):
        # Heading
        self.c.setFont("Helvetica-Bold", 13)
        if self.cursor_y < 4*cm:
            self._flush_page()
        self.c.drawString(2*cm, self.cursor_y, f"• {title}")
        self.cursor_y -= 16
        # Body
        if description:
            self._write_wrapped(description, size=10, leading=13)
            self.cursor_y -= 4
        # Screenshot
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                img = ImageReader(screenshot_path)
                # Fit width to page with margins, keep aspect
                img_w, img_h = img.getSize()
                max_w = self.width - 4*cm
                scale = min(max_w / img_w, 12*cm / img_h)
                draw_w, draw_h = img_w*scale, img_h*scale
                if self.cursor_y - draw_h < 2*cm:
                    self._flush_page()
                self.c.drawImage(img, 2*cm, self.cursor_y - draw_h, width=draw_w, height=draw_h, preserveAspectRatio=True)
                self.cursor_y -= (draw_h + 12)
            except Exception:
                # If picture fails, just continue
                pass

    def add_info(self, text):
        self._write_wrapped(text, size=10, leading=13)
        self.cursor_y -= 6

    def save(self):
        self.c.save()
        with open(self.out_path, "wb") as f:
            f.write(self.buffer.getvalue())

