"""Render the v0.7 sharp-cost manuscript with existing local libraries."""

import argparse
import importlib.util
from pathlib import Path
import re
import warnings


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('manuscript.md')
OUTPUT = Path(__file__).with_name('manuscript.pdf')
INHERITED_RENDERER = ROOT / 'paper' / 'build_pdf.py'
SCRATCH = ROOT / 'artifacts' / 'local' / 'sharp-cost-paper-build' / 'math'
TITLE = 'Sharp zero-table audit costs for finite best-of-N families'
PAPER_DATE = 'October 26, 2026'
MIN_DISPLAY_SIZE = 9.0
LINE_BREAK = 'ZZSHARPCOSTLINEBREAKZZ'


def load_renderer():
    """Reuse the archived note's renderer without editing or executing its CLI."""
    spec = importlib.util.spec_from_file_location(
        'ai_goodhart_archived_paper_renderer', INHERITED_RENDERER)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load inherited renderer: {INHERITED_RENDERER}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_renderer()


class Renderer(base.Renderer):
    """Apply manuscript typography and a display-legibility guard."""

    def __init__(self, scratch):
        super().__init__(scratch)
        self.display_count = 0
        self.minimum_display_size = 12.0
        self.styles['PaperTitle'].spaceAfter = 15
        self.styles['PaperBody'].leading = 14.2
        self.styles['PaperBody'].autoLeading = 'max'
        self.styles['PaperCell'].autoLeading = 'max'

    def inline(self, text, size=10.5):
        # The inherited parser joins prose lines. Preserve explicit Markdown
        # hard breaks, including an author line followed by its provenance.
        return super().inline(text, size).replace(LINE_BREAK, '<br/>')

    def paragraph(self, text, style='PaperBody', bullet=None):
        paragraph_style = self.styles[style]
        return base.Paragraph(self.inline(text, paragraph_style.fontSize),
                              paragraph_style, bulletText=bullet)

    def math_image(self, expression, size=10.5):
        path, width, height = super().math_image(expression, size)
        # In the inherited parser, only display math is requested at 12 pt.
        # Width-based scaling must never silently create unreadable displays.
        if size == 12:
            self.display_count += 1
            effective_size = 12 * min(1.0, base.WIDTH / width)
            self.minimum_display_size = min(self.minimum_display_size,
                                            effective_size)
            if effective_size < MIN_DISPLAY_SIZE:
                raise ValueError(
                    f'Display math would shrink to {effective_size:.2f} pt '
                    f'(minimum {MIN_DISPLAY_SIZE:g} pt). Split it into '
                    f'separate displays or shorten the notation: {expression}')
            if effective_size < 11:
                warnings.warn(
                    f'Display math scales to {effective_size:.2f} pt: '
                    f'{expression}', stacklevel=2)
        return path, width, height

    def parse(self, source):
        if LINE_BREAK in source:
            raise ValueError(f'Source contains reserved token {LINE_BREAK}')
        if re.search('[\u2010-\u2015]', source):
            raise ValueError('Use ASCII hyphens in the manuscript source')
        source = re.sub(r' {2,}\r?\n', f' {LINE_BREAK}\n', source)
        lines = source.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        if not lines or not lines[0].startswith('# '):
            raise ValueError('The manuscript must begin with a level-one title')
        title = lines.pop(0)[2:].strip()
        if title != TITLE:
            raise ValueError(f'Manuscript title must match PDF metadata: {TITLE}')
        if any(line.lstrip().startswith('# ') for line in lines):
            raise ValueError('Use only one level-one manuscript title')
        # The original renderer hardcodes body-size inline math in its title.
        # Construct this title separately so math follows the 22 pt title font.
        return [self.paragraph(title, 'PaperTitle')] + super().parse('\n'.join(lines))


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(base.colors.HexColor('#c6cdd4'))
    canvas.line(58, 43, 554, 43)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(base.colors.HexColor('#526170'))
    canvas.drawString(58, 30, 'Sharp zero-table audit costs | v0.7 consolidation | AI-assisted')
    canvas.drawRightString(554, 30, str(document.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--out', type=Path, default=OUTPUT)
    args = parser.parse_args()
    source_path = args.source.expanduser().resolve(strict=True)
    output_path = args.out.expanduser().resolve()
    if output_path.suffix.lower() != '.pdf':
        parser.error('--out must have the .pdf extension')
    if source_path == output_path:
        parser.error('--source and --out must be different paths')
    renderer = Renderer(SCRATCH)
    story = renderer.parse(source_path.read_text(encoding='utf-8'))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # SimpleDocTemplate adds 6 pt of padding inside each frame edge. These
    # margins therefore give prose, tables, and displays the same 496 pt width,
    # with their visible edges at 58 and 554 pt on US Letter paper.
    document = base.SimpleDocTemplate(
        str(output_path), pagesize=(612, 792),
        leftMargin=52, rightMargin=52, topMargin=42, bottomMargin=51,
        title=TITLE,
        author='Larry Mai; substantial Codex assistance disclosed in the manuscript',
        subject=f'Consolidation of v0.7 results; {PAPER_DATE}; '
                'AI-assisted research with no external peer review or real-model validation',
        creator='ai-goodhart sharp-cost manuscript renderer (ReportLab and Matplotlib)',
        keywords='best-of-N, finite families, zero-table audits, v0.7 consolidation',
        pageCompression=1)
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'Rendered manuscript: {output_path}')
    print(f'Displays: {renderer.display_count}; '
          f'minimum effective display size: {renderer.minimum_display_size:.2f} pt')


if __name__ == '__main__':
    main()
