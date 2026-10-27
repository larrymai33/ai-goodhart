# Sharp-cost manuscript

[Read the ten-page manuscript](manuscript.pdf) or its [Markdown source](manuscript.md). This manuscript consolidates the frozen v0.7 results at commit `ba573d604e3810d7edc9780d57ffea0ff8785296`. Its date is October 26, 2026. It is AI-assisted research, with no external peer review or real-model validation.

The complete arbitrary-grid theorem proof and monotone-family counterexample are included, together with the analytical example showing poor certification power on a safe nonzero table. This consolidation adds no new scientific measurements. All ten rendered pages were visually inspected; the 44 displayed equations retain a 12 pt base size. Mathematical notation is also available in the source because the PDF equations are raster images.

## Render with existing libraries

From the repository root:

```console
python paper/sharp-cost/build_pdf.py --out artifacts/local/sharp-cost-draft.pdf
```

The default input is `paper/sharp-cost/manuscript.md`; the default output is `paper/sharp-cost/manuscript.pdf`. Both defaults are resolved relative to the script, so the command can also run from another working directory. Use `--source` and `--out` to choose different paths.

The wrapper imports the unchanged [earlier renderer](../build_pdf.py). The command above requires Python with ReportLab, Matplotlib, and Pillow importable. The recorded build used the pre-existing Python 3.11 scientific installation, with the pre-existing bundled ReportLab package directory appended to `sys.path`; the bundled Python runtime alone did not contain Matplotlib. The artifact manifest records the library versions and both renderer files as build inputs. The wrapper performs no downloads, package installation, model calls, or numerical experiments. Intermediate equation images go in the ignored `artifacts/local/sharp-cost-paper-build/math` directory.

Prose and links remain PDF text. Equations use Matplotlib's bundled STIX fonts at 240 DPI and are embedded as images; the Markdown source preserves their searchable notation. The wrapper sizes inline math to its paragraph style, preserves explicit Markdown hard breaks, and rejects any display that would scale below a 9 pt base size. Split overlong displays in the source instead of shrinking them further. PDF metadata and the footer identify this manuscript separately from the earlier research note.

Rebuilds may differ across library versions, and PDF files include build metadata. Byte-identical PDF reproduction is not claimed. Rebuilding this document does not rerun or modify the frozen scientific artifacts; follow the repository's reproduction instructions to verify those artifacts separately.

## Verify recorded file integrity

The [artifact manifest](artifact-manifest.json) records SHA-256 hashes under the `sha256` key, with paths relative to the repository root. From that root, the following standard-library Python code verifies the recorded files:

```python
import hashlib
import json
from pathlib import Path

manifest = json.loads(Path('paper/sharp-cost/artifact-manifest.json').read_text(encoding='utf-8'))
for name, expected in manifest['sha256'].items():
    actual = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'Hash mismatch: {name}')
print(f"Verified {len(manifest['sha256'])} recorded files")
```

This checks file integrity. It does not recompute the numerical results, establish a proof, or provide independent replication or review.
