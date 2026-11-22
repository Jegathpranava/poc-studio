"""Generate the .docx and .pdf evaluation fixtures (fictional content only).

Run from services/api: uv run python ../../eval/fixtures/_make_binary_fixtures.py
The PDF is hand-written (Helvetica text streams) so no PDF writer dependency is needed.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from docx import Document

HERE = Path(__file__).parent

DOCX_NAME = "fintech-02-ledgerleaf-onboarding-brd.docx"
PDF_NAME = "healthcare-03-lumen-radiology-brief.pdf"

DOCX_TITLE = "Business Requirements: SME Lending Onboarding Assistant"
DOCX_SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Stakeholders",
        [
            "Executive sponsor: Octavia Marchetti-Wray, chief risk officer. Day-to-day owner: Vesper "
            "Lindholm-Achebe, head of underwriting. Users: a team of 14 underwriters and 5 onboarding "
            "specialists across two offices.",
            "Applicants are owners of restaurants, trades businesses, small shops and online sellers. Most "
            "apply from a phone and upload photographs of paper documents, which is why document quality "
            "checks matter so much at the start of the process.",
            "The lender processes about 1,800 applications a month and expects volume to double within two "
            "years, so the current manual review approach cannot simply be staffed up.",
        ],
    ),
    (
        "Overview",
        [
            "Ledgerleaf Credit (fictional) is a fintech lender that offers working capital loans of 10,000 to "
            "250,000 dollars to small businesses. Applicants upload bank statements, tax filings and incorporation "
            "documents, and an underwriting team checks them by hand. "
            "Contact for this request: lending-ops@ledgerleaf.example.com.",
            "This document describes a proof of concept for an onboarding and document verification assistant "
            "in the fintech lending sector.",
        ],
    ),
    (
        "Problems today",
        [
            "Applicants take an average of 9 days from first upload to a credit decision, and 38 percent abandon "
            "the application before a decision.",
            "Underwriters spend about 55 minutes per application reading bank statements, categorising "
            "transactions and checking that figures match across documents.",
            "Document problems such as blurred scans, missing pages and mismatched business names are found late, "
            "after the applicant has waited several days.",
            "Know-your-customer checks are repeated because the information is typed into three systems.",
        ],
    ),
    (
        "Goals",
        [
            "Reduce time from first upload to decision from 9 days to 3 days.",
            "Reduce underwriter handling time per application from 55 minutes to 20 minutes.",
            "Reduce abandonment from 38 percent to under 25 percent.",
            "Keep a human underwriter responsible for every credit decision.",
        ],
    ),
    (
        "Must-have features",
        [
            "1. Instant document check: when an applicant uploads a file, the system tells them within a minute "
            "if it is unreadable, incomplete or does not match the business name on the application.",
            "2. Bank statement analysis: extract transactions, categorise income and expenses, compute average "
            "monthly revenue, volatility and obligations, and present a one-page cash flow summary with the "
            "source lines.",
            "3. Cross-document consistency check: compare figures across statements, tax filings and the "
            "application, and flag differences above a set tolerance.",
            "4. Underwriter review screen: a single screen with the summary, flags, applicant history and a "
            "drafted credit memo that the underwriter edits and signs.",
        ],
    ),
    (
        "Nice-to-have features",
        [
            "A status page for applicants showing what has been received and what is still needed.",
            "A weekly report of turnaround time and flag rates by loan size.",
        ],
    ),
    (
        "Constraints",
        [
            "Applicant financial data is confidential. For the proof of concept only synthetic statements "
            "may be used.",
            "No credit decision may be made or communicated by the system. It only prepares information for "
            "the underwriter.",
            "The explanation of each flag must be readable by a compliance reviewer, and every flag must cite "
            "the source document and page.",
            "Hosting must be in the same region as our existing data, and no applicant data may be used to "
            "train external models.",
        ],
    ),
    (
        "Budget and timeline",
        [
            "The credit committee approved 70,000 dollars for the proof of concept, including model usage and "
            "hosting during evaluation.",
            "A working prototype is needed for the committee meeting on 9 September. Work should begin by the "
            "first week of July.",
        ],
    ),
    (
        "Success measures",
        [
            "Document check agrees with a human reviewer on at least 95 percent of 200 synthetic uploads.",
            "Cash flow summaries match the underwriter figures within 2 percent on 50 test applications.",
            "At least 85 percent of consistency flags are judged useful by underwriters.",
        ],
    ),
    (
        "Action items",
        [
            "Vesper Lindholm-Achebe (head of underwriting) to supply 200 synthetic applications with statements "
            "and the expected figures by 20 June.",
            "Ignatz Boateng (compliance) to review the flag wording and the data handling approach by 30 June.",
            "Philomena Crewe (engineering) to confirm the hosting region and the document storage options by "
            "25 June.",
            "The supplier to submit an architecture outline, model cost table and a clickable mock-up by 5 July.",
        ],
    ),
]
DOCX_TABLE = [
    ("Metric", "Today", "Target"),
    ("Days to decision", "9", "3"),
    ("Minutes per application", "55", "20"),
    ("Abandonment rate", "38 percent", "25 percent or lower"),
]

PDF_TITLE = "Project Brief: Radiology Report Follow-up Tracker"
PDF_SECTIONS: list[tuple[str, list[str]]] = [
    (
        "0. Background",
        [
            "Lumen completes about 41,000 studies a month across CT, MRI, ultrasound and X-ray. Reports are "
            "dictated by 22 radiologists and finalised in the radiology information system. Referring doctors "
            "receive the report through a portal or by fax, and the care coordination team of seven people "
            "handles scheduling questions by phone.",
            "The medical advisory board has asked for evidence that automated support can make follow-up "
            "tracking safer without adding work for radiologists, who are already under time pressure.",
        ],
    ),
    (
        "1. Summary",
        [
            "Lumen Imaging Partners (fictional) operates six outpatient imaging centres. Radiologists sometimes "
            "recommend follow-up imaging in a report, for example a repeat scan of a small lung nodule in six "
            "months. These recommendations are buried in free text and are often not acted on. This healthcare "
            "brief asks for a proof of concept that finds these recommendations and tracks them to completion. "
            "Contact: informatics@lumen-imaging.example.com.",
        ],
    ),
    (
        "2. Problem",
        [
            "About 11 percent of reports contain a follow-up recommendation. An internal audit of 400 reports "
            "found that 27 percent of recommended follow-ups had no scheduled appointment after 90 days.",
            "Missed follow-ups create clinical risk and liability exposure. Today the quality team reviews a "
            "random sample of 3 percent of reports by hand.",
            "Reports are written in free text with no structured field for follow-up, and referring doctors "
            "are notified only by the report itself.",
        ],
    ),
    (
        "3. Objectives",
        [
            "Identify at least 95 percent of follow-up recommendations in reports, with a precision of at "
            "least 85 percent.",
            "Reduce recommended follow-ups with no appointment after 90 days from 27 percent to under 10 percent.",
            "Reduce quality team review effort by 60 percent.",
        ],
    ),
    (
        "4. Must-have features",
        [
            "Recommendation detection: read each finalised report and extract the finding, the recommended "
            "action, the modality and the recommended time frame, citing the sentence it came from.",
            "Follow-up worklist: a ranked list for the care coordination team showing overdue and upcoming "
            "follow-ups, with the patient contact preference and the referring doctor.",
            "Outreach drafting: draft a letter or message to the patient and a notification to the referring "
            "doctor, which a coordinator reviews and sends.",
            "Closure tracking: mark a follow-up as complete when a matching exam is found, or record a reason "
            "such as patient declined or no longer clinically needed.",
        ],
    ),
    (
        "5. Constraints",
        [
            "The proof of concept may use only synthetic or fully de-identified reports.",
            "A radiologist or coordinator reviews every extracted recommendation before any message is sent. "
            "The system gives no clinical advice.",
            "Reports must not leave the Lumen cloud account. Any language model must be reachable through a "
            "private endpoint in production.",
            "A full audit trail of extractions, edits and messages is required.",
        ],
    ),
    (
        "5a. Data and access",
        [
            "Lumen will provide reports as plain text exports with patient identifiers removed, together with "
            "the modality, exam date and referring practice. Appointment data will be provided as a separate "
            "file keyed by a pseudonymous patient number so that closure tracking can be demonstrated.",
            "Radiologists will label a sample of reports to mark where a follow-up recommendation appears and "
            "what it asks for. Two radiologists will label the same 100 reports so that agreement between "
            "them can be measured and used as the ceiling for system accuracy.",
        ],
    ),
    (
        "6. Budget and schedule",
        [
            "Budget for the proof of concept: 58,000 dollars, all in.",
            "The prototype must be ready for the medical advisory board on 12 March. Pilot at two centres is "
            "planned for the second quarter.",
        ],
    ),
    (
        "7. Success measures",
        [
            "Recall of at least 95 percent on 300 de-identified reports labelled by two radiologists.",
            "Coordinators can process a worklist item in under 2 minutes.",
            "Zero messages sent without human approval during the pilot.",
        ],
    ),
    (
        "8. Action items",
        [
            "Dr. Anneliese Ravensworth (chief radiologist) to provide 300 de-identified reports and labels by "
            "15 January.",
            "Bertrand Okonjo (care coordination manager) to document the current follow-up process and one week "
            "of worklist examples by 22 January.",
            "Yusra Delaney-Cole (privacy officer) to confirm the de-identification method by 29 January.",
            "The supplier to share an architecture outline and cost table by 5 February.",
        ],
    ),
]


def make_docx(path: Path) -> None:
    doc = Document()
    doc.add_heading(DOCX_TITLE, level=0)
    for heading, paras in DOCX_SECTIONS:
        doc.add_heading(heading, level=1)
        for text in paras:
            doc.add_paragraph(text)
    doc.add_heading("Target metrics", level=1)
    table = doc.add_table(rows=len(DOCX_TABLE), cols=3)
    for r, row in enumerate(DOCX_TABLE):
        for c, value in enumerate(row):
            table.cell(r, c).text = value
    doc.save(str(path))


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(path: Path) -> None:
    """Write a minimal multi-page PDF using the built-in Helvetica fonts."""
    page_lines: list[list[tuple[str, int, str]]] = [[]]  # (font, size, text)
    budget = 0

    def add(font: str, size: int, text: str) -> None:
        nonlocal budget
        need = size + 6
        if budget + need > 700:
            page_lines.append([])
            budget = 0
        page_lines[-1].append((font, size, text))
        budget += need

    add("F2", 18, PDF_TITLE)
    add("F1", 6, "")
    for heading, paras in PDF_SECTIONS:
        add("F2", 13, heading)
        for para in paras:
            for line in textwrap.wrap(para, 88):
                add("F1", 10, line)
            add("F1", 6, "")

    objects: list[bytes] = [b"", b""]  # 1 catalog and 2 pages, filled in below
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")  # 3
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")  # 4
    page_ids: list[int] = []
    for lines in page_lines:
        y = 780
        ops = ["BT"]
        for font, size, text in lines:
            ops.append(f"/{font} {size} Tf 1 0 0 1 56 {y} Tm ({_esc(text)}) Tj")
            y -= size + 6
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1", "replace")
        objects.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        cid = len(objects)
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents {cid} 0 R "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> >>".encode()
        )
        page_ids.append(len(objects))
    kids = " ".join(f"{i} 0 R" for i in page_ids)
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for n, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode() + b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    path.write_bytes(bytes(out))


if __name__ == "__main__":
    make_docx(HERE / DOCX_NAME)
    make_pdf(HERE / PDF_NAME)
    print("wrote", DOCX_NAME, PDF_NAME)
