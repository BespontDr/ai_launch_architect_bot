import asyncio
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class PDFGenerator:
    def __init__(self) -> None:
        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    async def create_strategy_pdf(self, telegram_id: int, content: str) -> Path:
        filename = f"strategy_{telegram_id}.pdf"
        file_path = self.output_dir / filename
        await asyncio.to_thread(self._build_pdf, file_path, content)
        return file_path

    def _build_pdf(self, file_path: Path, content: str) -> None:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if Path(font_path).exists():
            pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
            font_name = "DejaVuSans"
        else:
            font_name = "Helvetica"

        c = canvas.Canvas(str(file_path), pagesize=A4)
        width, height = A4

        x = 15 * mm
        y = height - 20 * mm
        c.setFont(font_name, 14)
        c.drawString(x, y, "Полная стратегия запуска")
        y -= 10 * mm

        c.setFont(font_name, 10)
        line_height = 5 * mm
        max_width = width - 30 * mm

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line:
                y -= line_height
                if y < 20 * mm:
                    c.showPage()
                    c.setFont(font_name, 10)
                    y = height - 20 * mm
                continue

            words = line.split()
            current_line = ""
            for word in words:
                candidate = f"{current_line} {word}".strip()
                if pdfmetrics.stringWidth(candidate, font_name, 10) <= max_width:
                    current_line = candidate
                else:
                    c.drawString(x, y, current_line)
                    y -= line_height
                    if y < 20 * mm:
                        c.showPage()
                        c.setFont(font_name, 10)
                        y = height - 20 * mm
                    current_line = word

            if current_line:
                c.drawString(x, y, current_line)
                y -= line_height
                if y < 20 * mm:
                    c.showPage()
                    c.setFont(font_name, 10)
                    y = height - 20 * mm

        c.save()
