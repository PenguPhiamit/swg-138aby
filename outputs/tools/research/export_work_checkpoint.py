"""Export an explicitly scoped local documentation checkpoint; no chat API access."""
from datetime import datetime
from pathlib import Path
import hashlib
import json
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'output/pdf/SWG-project-checkpoint-2026-10-14.pdf'
SOURCES = [
    'outputs/Documentation-support/available-work-20261014.md',
    'outputs/Documentation-support/C26-telemetry.md',
    'outputs/Documentation-support/R2-idempotence-proposal.md',
    'outputs/Documentation-support/server-species-census.md',
    'outputs/Documentation-support/C23-hoth-gameplay.md',
    'outputs/Documentation-support/hoth-release-gate.md',
    'outputs/Documentation-support/server-resource-and-implementation-census.md',
    'outputs/Documentation-support/server-world-census.md',
    'outputs/Documentation-support/farming-asset-download-queue.md',
    'outputs/Farming-assets/README.md',
    'outputs/Documentation-support/creature-handler-top-tier-plan.md',
    'outputs/Documentation-support/darksaber-ghostfire-feasibility.md',
    'outputs/SWG-feature-register.md',
    'outputs/SWG-roadmap.md',
]


def run():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont('Body', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Heading', 'C:/Windows/Fonts/arialbd.ttf'))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('TextLocal', fontName='Body', fontSize=9, leading=13,
                             spaceAfter=5, wordWrap='CJK', alignment=TA_LEFT))
    styles.add(ParagraphStyle('HeadingLocal', fontName='Heading', fontSize=13, leading=17,
                             spaceBefore=10, spaceAfter=7, keepWithNext=True))
    story = [Paragraph('SWG project documentation checkpoint', styles['Title']),
             Paragraph(datetime.now().strftime('%Y-%m-%d %H:%M local time'), styles['TextLocal']),
             Spacer(1, 16),
             Paragraph('Private local working record', styles['HeadingLocal']),
             Paragraph('This PDF captures the named project documents below. It is not a verbatim export of the chat, '
                       'an exhaustive asset census, a completed gameplay acceptance, or approval to deploy. '
                       'Source documents contain historical checkpoints; later dated corrections take precedence. '
                       'C26 C++ is unbuilt and untested; Hoth release remains NO-GO. '
                       'No credentials, database backups or private account files are included.', styles['TextLocal'])]
    manifest = []
    for relative in SOURCES:
        path = ROOT / relative
        raw = path.read_bytes()
        manifest.append(dict(path=relative, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
        story.append(Paragraph(escape(relative), styles['TextLocal']))
    for record in manifest:
        story += [PageBreak(), Paragraph(escape(record['path']), styles['HeadingLocal']),
                  Paragraph('SHA-256: ' + record['sha256'], styles['TextLocal'])]
        lines = (ROOT / record['path']).read_text(encoding='utf-8-sig').splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 4))
            elif line.startswith('#'):
                story.append(Paragraph(escape(line.lstrip('# ')), styles['HeadingLocal']))
            else:
                # Keep table rows legible as wrapped text in this archival snapshot.
                story.append(Paragraph(escape(line), styles['TextLocal']))

    def footer(canvas, doc):
        canvas.setFont('Body', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(42, 25, 'Private SWG checkpoint | 14 October 2026')
        canvas.drawRightString(570, 25, str(doc.page))

    SimpleDocTemplate(str(DEST), pagesize=(612, 792), leftMargin=42, rightMargin=42,
                      topMargin=40, bottomMargin=42, title='SWG project documentation checkpoint').build(
                          story, onFirstPage=footer, onLaterPages=footer)
    DEST.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(DEST)


if __name__ == '__main__':
    run()
