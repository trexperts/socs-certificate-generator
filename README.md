# SOCS Certificate Generator

Batch-generates personalized PDF membership certificates for SOCS members. Pulls member data (name, year joined, email, membership type) directly from a Google Sheet and stamps each name onto the official blank shell template.

---

## Quick start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add the font
Download **Great Vibes** from Google Fonts and place `GreatVibes-Regular.ttf` in this folder:
https://fonts.google.com/specimen/Great+Vibes

### 3. Add the template PDF
Place the blank shell in this folder:
```
MembershipCertificateISCL_SHELL-03-05-19.pdf
```

### 4. Connect your Google Sheet

#### A. Create a service account
1. Go to https://console.cloud.google.com
2. Create a new project (or use an existing one)
3. Enable the **Google Sheets API** and **Google Drive API**
4. Go to **IAM & Admin → Service Accounts → Create Service Account**
5. Give it a name, click through to finish
6. Click the service account → **Keys → Add Key → Create new key → JSON**
7. Save the downloaded file as `credentials.json` in this folder

#### B. Share your Google Sheet with the service account
1. Open `credentials.json` and copy the `client_email` value
   (looks like `something@project.iam.gserviceaccount.com`)
2. Open your Google Sheet → Share → paste that email → Viewer access is enough

#### C. Set your Sheet ID
Open your Google Sheet in a browser. The URL looks like:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
```
Copy the ID and paste it into `generate_certificates.py`:
```python
SHEET_ID = "your-sheet-id-here"
```

### 5. Set up your Google Sheet columns
Your sheet must have these column headers (exact spelling, any order):

| Column | Description |
|--------|-------------|
| `name` | Full name as it should appear on the certificate |
| `year_joined` | Year joined (e.g. `2025`) |
| `email` | Email address (used for sending step) |
| `membership_type` | e.g. `Full Member`, `Associate Member` |

### 6. Generate certificates
```bash
python generate_certificates.py
```

Certificates are saved to `./output/`, one PDF per member.
A snapshot of the sheet data is also saved to `./output/recipients_export.csv`.

---

## Fallback: local CSV
If you haven't set up Google Sheets yet, the script automatically falls back to `recipients.csv` in this folder. Format:
```csv
name,year_joined,email,membership_type
John Smith MD,2025,john@example.com,Full Member
Jane Doe PhD,2024,jane@example.com,Associate Member
```

---

## Files

| File | Description |
|------|-------------|
| `generate_certificates.py` | Main batch generator |
| `requirements.txt` | Python dependencies |
| `recipients.csv` | Sample/fallback recipient list |
| `credentials.json` | Google service account key *(not committed — add yourself)* |
| `MembershipCertificateISCL_SHELL-03-05-19.pdf` | Blank template *(not committed — add yourself)* |
| `GreatVibes-Regular.ttf` | Script font *(not committed — download separately)* |

---

## Notes
- `credentials.json`, the template PDF, and the font are gitignored — never commit them
- Never commit `recipients.csv` with real member data; use `recipients_real.csv` (also gitignored)
- Generated certificates go in `output/` which is also gitignored
