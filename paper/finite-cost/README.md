# Current finite-cost manuscript

[Read the PDF](manuscript.pdf) or the [assembled Markdown](manuscript.md).
The v0.14.1 document consolidates v0.14 evidence from commit
`765ac51cc26fc3b3fd54bca2d23fc64285a2df65`; it adds no new theorem or
scientific measurement. The earlier v0.3 and v0.7 PDFs remain unchanged.

The main result is the all-finite-grid characterization of expected distinct
label cost, with a cached likelihood upper construction and a matching
dyadic subcensus regime. Appendices A–C include every project-specific lemma
needed for those results. The secondary original-instance checkpoint and
lower-certificate proofs remain separate and are linked explicitly. See the
[source map](source-map.md) for exact correspondence and the
[review guide](../../docs/review-guide.md) for the recommended reading order.

The 31-page PDF has 186 display blocks, 217 display rows, 116 distinct
equation labels, and 14 references. All display base sizes are 12 points.
Mathematical expressions are raster images rendered at 240 dpi; PDF prose
is searchable, but use the Markdown for searchable and copyable equations.
The renderer supports this document's restricted syntax, not arbitrary TeX.

## Build with existing local libraries

From the repository root, with Python, ReportLab, Matplotlib, and Pillow
already available:

```powershell
python -B paper/finite-cost/build_pdf.py --out artifacts/local/finite-cost-rebuild.pdf
```

If ReportLab is in another existing package directory, supply
`--extra-packages 'ABSOLUTE_EXISTING_PACKAGE_DIRECTORY'`. This option only
adds that directory to Python's import search path; it installs nothing.
No TeX engine, network access, model weights, or model API is required.
The build also assembles `manuscript.md` from `main.md`, `appendices.md`,
and `references.md`. Equation images are cached under ignored
`artifacts/local/finite-cost-paper-build/math/`.

The distributed build used Python 3.11.0, Matplotlib 3.7.1, Pillow 12.3.0,
and ReportLab 4.4.9. PDF metadata and rendering-library differences can
change rebuilt bytes; byte-identical PDF rebuilding is not promised.

## Verify distributed files

The [artifact manifest](artifact-manifest.json) pins the distributed PDF,
Markdown, build code, source map, formatter tests, primary-source follow-up,
and relevant frozen scientific files. Run from the repository root:

```powershell
@'
import hashlib, json
from pathlib import Path
manifest = json.loads(Path('paper/finite-cost/artifact-manifest.json').read_text())
for name, expected in manifest['sha256'].items():
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit('Checksum mismatch: ' + name)
print('All distributed-file hashes match.')
'@ | python -B -S -
```

Formatter regressions and the full software suite are separate checks:

```powershell
python -B -S -m unittest discover -s tests -p test_finite_cost_format.py -v
python -B -O -S -m unittest discover -s tests -p test_finite_cost_format.py -v
python -B -m unittest discover -s tests -q
```

The full suite uses existing scientific packages for earlier experiment
tests. The review guide gives the separate exact-result reproduction
commands; rebuilding a PDF does not rerun those scientific calculations.

## Review and limits

Separate agent contexts checked the frozen-source correspondence, proof
dependencies, constants, equation references, formatter behavior, and page
layout. All pages were rendered and visually inspected. These checks took
place within the same assisted research session: they are not independent
human peer review, formal verification, or evidence of scientific priority.

The owner is Larry Mai. Codex substantially developed the research and this
manuscript. Larry reported having personally checked none of it so far.
No real-model evaluation or external outreach was performed. The exact-label
oracle, supplied margin, fixed pools, and all-pass certificate are material
assumptions. The final 2011 weighted-query journal comparison remains open;
the [new primary-slide follow-up](../../docs/weighted-query-followup.md)
explicitly credits earlier sampling and deterministic truncation mechanisms.
Field impact and fellowship competitiveness have not been established.
