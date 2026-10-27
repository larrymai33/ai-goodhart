"""Assemble and render current finite-cost proofs using installed libraries only."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
TITLE='Finite label costs for certifying best-of-N risk'
SOURCE_NAMES=('main.md','appendices.md','references.md')
MIN_DISPLAY_SIZE=9.0


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=HERE/'manuscript.pdf')
    parser.add_argument('--extra-packages',type=Path,
                        help='Optional existing package directory; never installs anything')
    args=parser.parse_args(argv)
    if args.extra_packages:
        if not args.extra_packages.is_dir():
            parser.error('--extra-packages must already exist')
        sys.path.append(str(args.extra_packages.resolve()))
    base=load('finite_cost_archived_renderer',ROOT/'paper/build_pdf.py')
    formatting=load('finite_cost_math_formatter',HERE/'format_math.py')
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.platypus import PageBreak,Table,TableStyle
    width=496

    class Renderer(base.Renderer):
        def __init__(self,scratch):
            super().__init__(scratch)
            self.display_count=0
            self.row_count=0
            self.minimum_display_size=12.0
            self.styles['PaperBody'].leading=13.5
            self.styles['PaperBody'].autoLeading='max'
            self.styles['PaperCell'].autoLeading='max'
            self.styles['PaperTitle'].keepWithNext=True
            self.styles.add(base.ParagraphStyle('EquationTag',fontName='Times-Roman',
                                                fontSize=9,leading=10,alignment=TA_RIGHT))

        def math_image(self,expression,size=10.5):
            return super().math_image(formatting.normalize_math(expression),size)

        def inline(self,text,size=10.5):
            # Section names remain readable in PDF; external references stay clickable.
            text=re.sub(r'\[([^\]]+)\]\(#[^)]+\)',r'\1',text)
            def external(match):
                label,target=match.groups()
                if '://' in target:
                    return match.group()
                target_path=(HERE/target.split('#')[0]).resolve()
                if not target_path.is_relative_to(ROOT):
                    raise ValueError('local manuscript link leaves repository: '+target)
                suffix=('#'+target.split('#',1)[1]) if '#' in target else ''
                url='https://github.com/larrymai33/ai-goodhart/blob/v0.14/'+target_path.relative_to(ROOT).as_posix()+suffix
                return '['+label+']('+url+')'
            text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',external,text)
            return super().inline(text,size)

        def paragraph(self,text,style='PaperBody',bullet=None):
            return base.Paragraph(self.inline(text,self.styles[style].fontSize),
                                  self.styles[style],bulletText=bullet)

        def display(self,expression):
            rows,tag=formatting.display_rows(expression)
            self.display_count+=1
            self.row_count+=len(rows)
            table=[]
            available=width-40 if tag else width
            for index,row in enumerate(rows):
                path,w,h=self.math_image(row,12)
                scale=min(1.0,available/w)
                effective=12*scale
                self.minimum_display_size=min(self.minimum_display_size,effective)
                if effective<MIN_DISPLAY_SIZE:
                    raise ValueError(f'Display {tag or self.display_count} shrinks to {effective:.2f} pt; split its row: {row}')
                label=self.paragraph('('+tag+')','EquationTag') if tag and index==len(rows)-1 else ''
                table.append([base.Image(str(path),w*scale,h*scale),label] if tag
                             else [base.Image(str(path),w*scale,h*scale)])
            item=Table(table,colWidths=[available,40] if tag else [available],hAlign='CENTER')
            item.setStyle(TableStyle([('ALIGN',(0,0),(0,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                      ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
                                      ('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1)]))
            return [base.Spacer(1,2),item,base.Spacer(1,7)]

        def parse_document(self,source):
            result=[]
            cursor=0
            for match in re.finditer(r'(?ms)^\$\$\s*\n(.*?)^\$\$\s*$',source):
                prose=source[cursor:match.start()]
                if '$$' in prose:
                    raise ValueError('unparsed display math before '+str(match.start()))
                prose_items=super().parse(prose)
                # Keep a short formula introduction attached to its display.
                introduction=[]
                if prose_items and isinstance(prose_items[-1],base.Paragraph):
                    plain=prose_items[-1].getPlainText()
                    if len(plain)<220:
                        introduction=[prose_items.pop()]
                if introduction:
                    while (prose_items and isinstance(prose_items[-1],base.Paragraph)
                           and getattr(prose_items[-1].style,'keepWithNext',False)):
                        introduction.insert(0,prose_items.pop())
                result.extend(prose_items)
                display_items=self.display(match.group(1))
                result.append(base.KeepTogether(introduction+display_items))
                cursor=match.end()
            if '$$' in source[cursor:]:
                raise ValueError('unparsed display math at end of source')
            result.extend(super().parse(source[cursor:]))
            return result

    sources=[(HERE/name).read_text(encoding='utf-8') for name in SOURCE_NAMES]
    if not sources[0].lstrip().startswith('# '+TITLE+'\n'):
        raise ValueError('main title must match PDF metadata')
    renderer=Renderer(ROOT/'artifacts/local/finite-cost-paper-build/math')
    story=[]
    for index,source in enumerate(sources):
        if index:
            story.append(PageBreak())
        story.extend(renderer.parse_document(source))
    combined='\n\n'.join(sources).rstrip()+'\n'
    (HERE/'manuscript.md').write_text(combined,encoding='utf-8',newline='\n')
    output=args.out.resolve()
    if output.suffix.lower()!='.pdf':
        parser.error('--out must be a PDF path')
    output.parent.mkdir(parents=True,exist_ok=True)
    def footer(canvas,document):
        canvas.saveState()
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(base.colors.HexColor('#526170'))
        canvas.drawString(58,30,'Finite audit costs | v0.14 evidence consolidation | AI-assisted draft')
        canvas.drawRightString(554,30,str(document.page))
        canvas.restoreState()
    document=base.SimpleDocTemplate(str(output),pagesize=(612,792),
                                    leftMargin=52,rightMargin=52,topMargin=42,bottomMargin=51,
                                    title=TITLE,author='Larry Mai; substantial Codex assistance disclosed',
                                    subject='Fixed-table minimax label cost; no independent human review',
                                    pageCompression=1)
    document.build(story,onFirstPage=footer,onLaterPages=footer)
    print(json.dumps({'output':str(output),'display_equations':renderer.display_count,
                      'display_rows':renderer.row_count,
                      'minimum_display_base_size_pt':renderer.minimum_display_size}))


if __name__=='__main__':
    main()
