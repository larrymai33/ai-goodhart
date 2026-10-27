"""Typography-only conversion of the manuscript's supported TeX subset.

Scientific Markdown stays unchanged. Alignment rows become separate displays;
tags are returned for textual labels. Unsupported environments fail explicitly.
"""
import re


def _explicit_arguments(expression,command,count):
    pattern=re.compile(r'\\'+command+r'(?![A-Za-z])')
    output=[]
    start=0
    for match in pattern.finditer(expression):
        if match.start()<start:
            continue
        output.append(expression[start:match.start()])
        cursor=match.end()
        arguments=[]
        for _ in range(count):
            while cursor<len(expression) and expression[cursor].isspace():
                cursor+=1
            if cursor==len(expression):
                raise ValueError('missing argument for '+command)
            first=cursor
            if expression[cursor]=='{':
                depth=1
                cursor+=1
                while cursor<len(expression) and depth:
                    if expression[cursor]=='{': depth+=1
                    if expression[cursor]=='}': depth-=1
                    cursor+=1
                if depth:
                    raise ValueError('unclosed argument for '+command)
                arguments.append(expression[first:cursor])
            elif expression[cursor]=='\\':
                atom=re.match(r'\\(?:[A-Za-z]+|.)',expression[cursor:])
                if atom is None:
                    raise ValueError('incomplete command argument')
                cursor+=len(atom.group())
                arguments.append('{'+expression[first:cursor]+'}')
            else:
                cursor+=1
                arguments.append('{'+expression[first:cursor]+'}')
        output.append('\\'+command+''.join(arguments))
        start=cursor
    output.append(expression[start:])
    return ''.join(output)


def normalize_math(expression):
    expression=re.sub(r'[\r\n]+',' ',expression.strip())
    expression=re.sub(r'\\(?:text|hbox)\{([^{}]*)\}',
                      lambda m:r'\mathrm{'+m.group(1).replace(' ',r'\ ')+'}',expression)
    expression=re.sub(r'\{\\rm\s+([^{}]*)\}',lambda m:r'{\mathrm{'+m.group(1)+'}}',expression)
    expression=re.sub(r'\\tfrac(?![A-Za-z])',r'\\frac',expression)
    for command,count in (('binom',2),('frac',2),('sqrt',1),('mathbb',1),('mathbf',1),('mathcal',1)):
        expression=_explicit_arguments(expression,command,count)
    expression=re.sub(r'\\le(?![A-Za-z])',r'\\leq',expression)
    expression=re.sub(r'\\ge(?![A-Za-z])',r'\\geq',expression)
    expression=re.sub(r'\\square(?![A-Za-z])',lambda _:r'\mathrm{QED}',expression)
    # Fixed-size delimiters allow a multirow display's delimiters to span rows.
    expression=expression.replace(r'\left.','').replace(r'\right.','')
    expression=re.sub(r'\\(?:left|right|boxed)(?![A-Za-z])','',expression)
    return expression


def display_rows(expression):
    tags=re.findall(r'\\tag\{([^{}]+)\}',expression)
    if len(tags)>1:
        raise ValueError('a display may have only one equation tag')
    expression=re.sub(r'\\tag\{[^{}]+\}','',expression)
    begins=re.findall(r'\\begin\{([^}]+)\}',expression)
    ends=re.findall(r'\\end\{([^}]+)\}',expression)
    if begins!=ends or any(value!='aligned' for value in begins) or len(begins)>1:
        raise ValueError('only a single complete aligned environment is supported')
    expression=expression.replace(r'\begin{aligned}','').replace(r'\end{aligned}','')
    rows=re.split(r'\\\\(?:\[[^\]]+\])?',expression)
    rows=tuple(normalize_math(row.replace('&','').strip()) for row in rows if row.strip())
    if not rows:
        raise ValueError('empty display')
    return rows,tags[0] if tags else None
