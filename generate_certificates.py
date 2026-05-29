"""
SOCS Certificate Batch Generator
==================================
Pulls member data from a Google Sheet and generates a personalized PDF
certificate for each recipient.

Google Sheet columns expected (in any order):
    name            - Full name as it should appear on the certificate
    year_joined     - Year they joined (e.g. 2025)
    email           - Email address (used for sending, not on certificate)
    membership_type - e.g. Full Member, Associate Member, Honorary Member

Setup:
    1. pip install -r requirements.txt
    2. Create a Google Cloud service account and download credentials.json
       (see README.md for step-by-step instructions)
    3. Share your Google Sheet with the service account email
    4. Set SHEET_ID below to your Google Sheet ID
    5. Place GreatVibes-Regular.ttf and the template PDF in this folder
    6. Run: python generate_certificates.py

Output:
    ./output/<Name>_certificate.pdf  — one per recipient
    ./output/recipients_export.csv   — exported snapshot of the sheet data
"""

import csv
import io
import os

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Configuration ─────────────────────────────────────────────────────────────
SHEET_ID      = "YOUR_GOOGLE_SHEET_ID_HERE"   # from the sheet URL
SHEET_NAME    = "Sheet1"                       # tab name in your Google Sheet

TEMPLATE_PATH = "MembershipCertificateISCL_SHELL-03-05-19.pdf"
FONT_PATH     = "GreatVibes-Regular.ttf"
CREDS_PATH    = "credentials.json"            # Google service account key
OUTPUT_DIR    = "output"

W, H = 792, 612   # landscape letter

NAME_X = W / 2
NAME_Y = 319
YEAR_X = W / 2
YEAR_Y = 210
# ──────────────────────────────────────────────────────────────────────────────


def load_sheet_data() -> list:
    """Pull member rows from Google Sheets via service account credentials."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        raise ImportError(
            "\nMissing Google Sheets libraries. Run:\n"
            "    pip install -r requirements.txt\n"
        )

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds  = Credentials.from_service_account_file(CREDS_PATH, scopes=scopes)
    client = gspread.authorize(creds)
    sheet  = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    rows   = sheet.get_all_records()
    print(f"  Loaded {len(rows)} rows from Google Sheet")
    return rows


def load_csv_fallback() -> list:
    """Fallback: load from local recipients.csv if Google Sheets isn't configured."""
    path = "recipients.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Neither Google Sheets credentials nor {path} found.\n"
            "Add credentials.json and set SHEET_ID, or provide recipients.csv."
        )
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_members() -> list:
    """Load member data — Google Sheets if configured, else local CSV."""
    if SHEET_ID == "YOUR_GOOGLE_SHEET_ID_HERE":
        print("INFO: SHEET_ID not set — falling back to local recipients.csv")
        return load_csv_fallback()
    if not os.path.exists(CREDS_PATH):
        print(f"INFO: {CREDS_PATH} not found — falling back to local recipients.csv")
        return load_csv_fallback()
    print("Connecting to Google Sheets...")
    return load_sheet_data()


def register_fonts():
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(
            f"\nFont not found: {FONT_PATH}\n"
            "Download Great Vibes at https://fonts.google.com/specimen/Great+Vibes\n"
            "and place GreatVibes-Regular.ttf in this folder."
        )
    pdfmetrics.registerFont(TTFont("GreatVibes", FONT_PATH))


def get_font_size(name: str) -> int:
    if len(name) > 30:
        return 36
    if len(name) > 22:
        return 42
    return 48


def make_certificate(recipient_name: str, year_joined: str, output_path: str):
    """Stamp name + year onto the template PDF."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(W, H))

    c.setFont("GreatVibes", get_font_size(recipient_name))
    c.setFillColorRGB(0.05, 0.05, 0.05)
    c.drawCentredString(NAME_X, NAME_Y, recipient_name)

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


def export_csv_snapshot(members: list):
    """Save a local snapshot of the sheet data for reference."""
    if not members:
        return
    path = os.path.join(OUTPUT_DIR, "recipients_export.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=members[0].keys())
        writer.writeheader()
        writer.writerows(members)
    print(f"  Snapshot saved to {path}")


def main():
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(
            f"\nTemplate not found: {TEMPLATE_PATH}\n"
            "Place the blank shell PDF in this folder."
        )

    register_fonts()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    members = get_members()
    if not members:
        print("No members found — nothing to generate.")
        return

    export_csv_snapshot(members)

    total  = len(members)
    errors = []
    print(f"\nGenerating {total} certificate{'s' if total != 1 else ''}...\n")

    for i, row in enumerate(members, 1):
        name            = str(row.get("name", "")).strip()
        year            = str(row.get("year_joined", "2025")).strip() or "2025"
        email           = str(row.get("email", "")).strip()           # available for email step
        membership_type = str(row.get("membership_type", "")).strip() # available for filtering

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

    print(f"\nDone — certificates saved to ./{OUTPUT_DIR}/")
    if errors:
        print(f"WARNING: {len(errors)} error(s) — see above.")


if __name__ == "__main__":
    main()
