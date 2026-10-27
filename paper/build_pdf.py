"""Render the research note with existing ReportLab/Matplotlib; no downloads."""

import argparse
import hashlib
import html
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
from matplotlib import mathtext
from matplotlib.font_manager import FontProperties
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                               LongTable, TableStyle, Preformatted, KeepTogether)


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 612 - 2 * 58
DPI = 240


class Renderer:
    def __init__(self, scratch):
        self.scratch = scratch
        scratch.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle('PaperTitle', fontName='Times-Bold', fontSize=22,
                                       leading=25, spaceAfter=14))
        self.styles.add(ParagraphStyle('PaperBody', fontName='Times-Roman', fontSize=10.5,
                                       leading=14, spaceAfter=7, alignment=TA_JUSTIFY))
        self.styles.add(ParagraphStyle('PaperHeading', fontName='Times-Bold', fontSize=13,
                                       leading=16, spaceBefore=13, spaceAfter=7, keepWithNext=True))
        self.styles.add(ParagraphStyle('PaperSubheading', fontName='Times-Bold', fontSize=11,
                                       leading=14, spaceBefore=8, spaceAfter=5, keepWithNext=True))
        self.styles.add(ParagraphStyle('PaperCell', fontName='Times-Roman', fontSize=9,
                                       leading=11.5, spaceAfter=0))
        self.styles.add(ParagraphStyle('PaperCode', fontName='Courier', fontSize=8,
                                       leading=10, spaceAfter=8))

    def math_image(self, expression, size=10.5):
        # A bundled font and mathtext avoid any TeX or font installation.
        expression = expression.strip().replace('\\displaystyle', '')
        expression = re.sub(r'\\le(?![A-Za-z])', r'\\leq', expression)
        expression = re.sub(r'\\ge(?![A-Za-z])', r'\\geq', expression)
        key = hashlib.sha256((str(size) + expression).encode()).hexdigest()[:24]
        path = self.scratch / (key + '.png')
        if not path.exists():
            with matplotlib.rc_context({'mathtext.fontset': 'stix', 'text.usetex': False}):
                mathtext.math_to_image('$' + expression + '$', str(path),
                                      prop=FontProperties(size=size), dpi=DPI, format='png')
        with PILImage.open(path) as img:
            width, height = img.size
        return path, width * 72 / DPI, height * 72 / DPI

    def inline(self, text, size=10.5):
        tokens = []
        def hold(value):
            tokens.append(value)
            return f'ZZTOKEN{len(tokens)-1}ZZ'
        def math(match):
            path, width, height = self.math_image(match.group(1), size)
            return hold(f'<img src="{path.as_posix()}" width="{width:.3f}" height="{height:.3f}" valign="-2"/>')
        text = text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2011', '-')
        text = re.sub(r'\$([^$\n]+)\$', math, text)
        text = re.sub(r'`([^`]+)`', lambda m: hold('<font name="Courier" size="8.5">' + html.escape(m.group(1)) + '</font>'), text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                      lambda m: hold('<link href="' + html.escape(m.group(2), quote=True) + '" color="#234e70">' + html.escape(m.group(1)) + '</link>'), text)
        text = html.escape(text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
        for index, value in enumerate(tokens):
            text = text.replace(f'ZZTOKEN{index}ZZ', value)
        return text

    def paragraph(self, text, style='PaperBody', bullet=None):
        return Paragraph(self.inline(text, 9 if style == 'PaperCell' else 10.5),
                         self.styles[style], bulletText=bullet)

    def parse(self, source):
        lines = source.splitlines()
        result, i = [], 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith('# '):
                title = self.inline(line[2:]).replace('for reusable', 'for<br/>reusable')
                result.append(Paragraph(title, self.styles['PaperTitle']))
                i += 1
            elif line.startswith('## '):
                result.append(self.paragraph(line[3:], 'PaperHeading'))
                i += 1
            elif line.startswith('### '):
                result.append(self.paragraph(line[4:], 'PaperSubheading'))
                i += 1
            elif line.startswith('$$'):
                content = line[2:]
                if content.endswith('$$') and content:
                    expression = content[:-2]
                    i += 1
                else:
                    block = [content] if content else []
                    i += 1
                    while i < len(lines) and lines[i].strip() != '$$':
                        block.append(lines[i].strip())
                        i += 1
                    if i == len(lines):
                        raise ValueError('unclosed display math')
                    i += 1
                    expression = ' '.join(block)
                path, width, height = self.math_image(expression, 12)
                scale = min(1., WIDTH / width)
                result.append(KeepTogether([Spacer(1, 3), Image(str(path), width*scale, height*scale), Spacer(1, 9)]))
            elif line.startswith('|'):
                table = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    cells = [cell.strip() for cell in lines[i].strip().strip('|').split('|')]
                    if not all(re.fullmatch(r':?-+:?', cell.replace(' ', '')) for cell in cells):
                        table.append([self.paragraph(cell, 'PaperCell') for cell in cells])
                    i += 1
                columns = len(table[0])
                widths = [WIDTH / columns] * columns
                if columns > 2:
                    widths = [WIDTH * .31] + [WIDTH * .69 / (columns-1)] * (columns-1)
                item = LongTable(table, colWidths=widths, repeatRows=1, hAlign='LEFT')
                item.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf1f4')),
                    ('LINEABOVE',(0,0),(-1,0),.6,colors.HexColor('#34485c')),
                    ('LINEBELOW',(0,0),(-1,0),.4,colors.HexColor('#34485c')),
                    ('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#34485c')),
                    ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
                result.append(KeepTogether([item, Spacer(1, 9)]))
            elif line.startswith('```'):
                i += 1
                code = []
                while i < len(lines) and not lines[i].startswith('```'):
                    code.append(lines[i])
                    i += 1
                i += 1
                result.append(Preformatted('\n'.join(code), self.styles['PaperCode'], maxLineLength=95))
            elif line.startswith('- '):
                result.append(self.paragraph(line[2:], bullet='-'))
                i += 1
            else:
                block = [line]
                i += 1
                while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#', '$$', '|', '```', '- ')):
                    block.append(lines[i].strip())
                    i += 1
                result.append(self.paragraph(' '.join(block)))
        return result


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#c6cdd4'))
    canvas.line(58, 43, 554, 43)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#526170'))
    canvas.drawString(58, 30, 'Finite-pool corrections | Research note | AI-assisted; no external peer review')
    canvas.drawRightString(554, 30, str(document.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'paper' / 'paper.md')
    parser.add_argument('--out', type=Path, default=ROOT / 'paper' / 'paper.pdf')
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    renderer = Renderer(ROOT / 'artifacts' / 'local' / 'paper-build' / 'math')
    document = SimpleDocTemplate(str(args.out), pagesize=(612,792), leftMargin=58, rightMargin=58,
                                 topMargin=48, bottomMargin=57, title='Finite-pool corrections for reusable best-of-N audits',
                                 author='Larry Mai; substantial Codex assistance disclosed in the note',
                                 subject='Finite-pool envelope theorem and reproducible audit comparisons',
                                 pageCompression=1)
    document.build(renderer.parse(args.source.read_text(encoding='utf-8')), onFirstPage=footer, onLaterPages=footer)
    print('Rendered research note:', args.out)


if __name__ == '__main__':
    main()
