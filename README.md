# ISCL Certificate Generator

Batch-generates personalized PDF membership certificates for the International Society for Cutaneous Lymphomas. Stamps each recipient's name and year joined onto the official blank shell template.

---

## How it works

Each certificate is produced by overlaying the recipient's name (in a matching script font) onto the blank PDF shell template. No design tools needed — just a CSV of names and Python.

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add the font
Download **Great Vibes** from Google Fonts:
https://fonts.google.com/specimen/Great+Vibes

Place `GreatVibes-Regular.ttf` in this folder.

### 3. Add the template
Place your blank shell PDF in this folder:
```
MembershipCertificateISCL_SHELL-03-05-19.pdf
```

### 4. Prepare your recipients
Edit `recipients.csv` — one row per member:
```csv
name,year_joined
John Smith MD,2025
Jane Doe PhD,2024
```

### 5. Generate
```bash
python generate_certificates.py
```

Certificates are saved to `./output/`, one PDF per recipient named like:
```
John_Smith_MD_certificate.pdf
```

---

## Font size auto-scaling

The script automatically reduces the font size for longer names so nothing overflows the name zone:

| Name length | Font size |
|-------------|-----------|
| ≤ 22 chars  | 48pt      |
| 23–30 chars | 42pt      |
| 31+ chars   | 36pt      |

---

## Files

| File | Description |
|------|-------------|
| `generate_certificates.py` | Main batch generator |
| `recipients.csv` | Sample recipient list (replace with your real data) |
| `requirements.txt` | Python dependencies |
| `MembershipCertificateISCL_SHELL-03-05-19.pdf` | Blank template *(add manually — not committed)* |
| `GreatVibes-Regular.ttf` | Script font *(download separately — not committed)* |

---

## Notes

- The template PDF and font are **not included** in this repo (font license / org asset).
- Never commit a `recipients.csv` with real member data — add it to `.gitignore` or use `recipients_real.csv` (already ignored).
- Generated certificates go in `output/` which is also gitignored.
