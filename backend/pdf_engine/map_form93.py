"""
Maps application data -> fields.json for Form 93 (Application for Allotment of PAN).
Coordinates were extracted from the official Form 93 PDF's text/line structure
(pdfplumber) and hand-verified against rendered page images.

Input `app` dict keys (matches the `applications` table already used by the
hrsoftech-pan-portal backend):
  full_name, gender ('male'/'female'/'transgender'), dob ('YYYY-MM-DD'),
  aadhaar_number, residence_address {line1, line2, post_office, city,
  district, state, country, pincode}, office_address {...same keys...},
  residential_status ('resident'/'non_resident'/'rnor'),
  passport_number, tin, mobile_country_code, mobile, email,
  landline_std_code, landline_number, source_of_income (list of:
  'salary','business','house_property','capital_gains','other','none'),
  single_parent ('yes'/'no'), father_name, mother_name,
  parent_on_card ('father'/'mother'),
  ao_area_code, ao_type, ao_range_code, ao_no,
  ra_name, ra_pan, ra_aadhaar, ra_address {...}, ra_mobile_country_code,
  ra_mobile, ra_email, ra_landline_std_code, ra_landline_number,
  communication_address ('residence'/'ra'/'office'),
  documents_applicant (list of: 'identity','address','dob'),
  documents_ra (list of: 'identity','address')
"""

PDF_W, PDF_H = 595.276, 841.89001


def _split_name(full_name):
    parts = (full_name or "").split()
    first = parts[0] if parts else ""
    middle = " ".join(parts[1:-1]) if len(parts) > 2 else ""
    last = parts[-1] if len(parts) > 1 else ""
    return first, middle, last


def _text_field(page, description, left, top, bottom, text, right=560, font_size=9):
    return {
        "page_number": page,
        "description": description,
        "field_label": description,
        "label_bounding_box": [max(left - 15, 0), top, left, bottom],
        "entry_bounding_box": [left + 4, top - 0.5, right, bottom + 0.5],
        "entry_text": {"text": str(text), "font_size": font_size},
    }


def _tick(page, description, cx, top, bottom, half_w=6):
    return {
        "page_number": page,
        "description": description,
        "field_label": description,
        "label_bounding_box": [cx - half_w, top - 3.2, cx + half_w, top - 0.4],
        "entry_bounding_box": [cx - half_w, top - 0.3, cx + half_w, bottom + 0.3],
        "entry_text": {"text": "X", "font_size": min(6, bottom - top - 0.6)},
    }


def build_fields(app: dict):
    fields = []
    add = fields.append

    def T(description, page, left, top, bottom, text, right=560, font_size=8):
        if text:
            add(_text_field(page, description, left, top, bottom, text, right, font_size))

    def TICK(description, page, cx, top, bottom):
        add(_tick(page, description, cx, top, bottom))

    ra = app.get("ra_address", {}) or {}
    res = app.get("residence_address", {}) or {}
    off = app.get("office_address", {}) or {}

    # ---------------- PAGE 1 ----------------
    first, middle, last = _split_name(app.get("full_name", ""))
    T("First Name", 1, 87.2, 198.6, 205.6, first)
    T("Middle Name", 1, 93.5, 212.0, 219.0, middle)
    T("Last Name", 1, 86.8, 225.7, 232.7, last)
