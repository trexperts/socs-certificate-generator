"""
ISCL Certificate Batch Generator
==================================
Stamps each recipient's name and year joined onto the blank shell PDF template.

Setup:
    pip install -r requirements.txt
    # Place GreatVibes-Regular.ttf in this folder (fonts.google.com/specimen/Great+Vibes)
    # Place MembershipCertificateISCL_SHELL-03-05-19.pdf in this folder

Usage:
    python generate_certificates.py
"""

import csv
import io
import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Configuration ─────────────────────────────────────────────────────────────
TEMPLATE_PATH = "MembershipCertificateISCL_SHELL-03-05-19.pdf"
FONT_PATH     = "GreatVibes-Regular.ttf"
CSV_PATH      = "recipients.csv"
OUTPUT_DIR    = "output"

W, H = 792, 612   # landscape letter — matches the template exactly

# Name placement — centered in the blank zone between "awarded to" and body text
NAME_X         = W / 2
NAME_Y         = 319    # PDF points from bottom of page

# Year joined — centered below the body paragraph
YEAR_X         = W / 2
YEAR_Y         = 210
# ──────────────────────────────────────────────────────────────────────────────


def register_fonts():
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(
            f"\nFont not found: {FONT_PATH}\n"
            "Download Great Vibes at https://fonts.google.com/specimen/Great+Vibes\n"
            "and place GreatVibes-Regular.ttf in this folder."
        )
    pdfmetrics.registerFont(TTFont("GreatVibes", FONT_PATH))


def get_font_size(name: str) -> int:
    """Auto-scale font for long names so they fit the name zone."""
    if len(name) > 30:
        return 36
    if len(name) > 22:
        return 42
    return 48


def make_certificate(recipient_name: str, year_joined: str, output_path: str):
    """Overlay name + year onto the template and save to output_path."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(W, H))

    # Recipient name in script font, centered
    c.setFont("GreatVibes", get_font_size(recipient_name))
    c.setFillColorRGB(0.05, 0.05, 0.05)
    c.drawCentredString(NAME_X, NAME_Y, recipient_name)

    # Year joined, centered below body paragraph
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.drawCentredString(YEAR_X, YEAR_Y, f"Year Joined: {year_joined}")

    c.save()
    packet.seek(0)

    overlay  = PdfReader(packet).pages[0]
    template = PdfReader(TEMPLATE_PATH).pages[0]
    template.merge_page(overlay)

    writer = PdfWriter()
    writer.add_page(template)
    with open(output_path, "wb") as f:
        writer.write(f)


def safe_filename(name: str) -> str:
    return (
        name.replace(" ", "_")
            .replace(",", "")
            .replace(".", "")
            .replace("/", "")
        + "_certificate.pdf"
    )


def main():
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(
            f"\nTemplate not found: {TEMPLATE_PATH}\n"
            "Place the blank shell PDF in this folder."
        )

    register_fonts()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("recipients.csv is empty — add your members and re-run.")
        return

    total  = len(rows)
    errors = []
    print(f"Generating {total} certificate{'s' if total != 1 else ''}...\n")

    for i, row in enumerate(rows, 1):
        name = row.get("name", "").strip()
        year = row.get("year_joined", "").strip() or "2025"

        if not name:
            print(f"  Row {i}: skipped (empty name)")
            continue

        out = os.path.join(OUTPUT_DIR, safe_filename(name))
        try:
            make_certificate(name, year, out)
        except Exception as e:
            errors.append((i, name, str(e)))
            print(f"  Row {i}: ERROR — {name}: {e}")
            continue

        if i % 50 == 0 or i == total:
            print(f"  {i}/{total} complete")

    print(f"\n✓ Done — certificates in ./{OUTPUT_DIR}/")
    if errors:
        print(f"⚠  {len(errors)} error(s) — see above.")


if __name__ == "__main__":
    main()
