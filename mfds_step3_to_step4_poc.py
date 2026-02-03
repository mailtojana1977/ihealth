from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os
import requests
import argparse


# ================= CONFIG =================
MFDS_SEARCH_URL = "https://emedi.mfds.go.kr/search/data/MNU20237#list"
SEARCH_LABEL = "명칭"
SEARCH_BUTTON_TEXT = "검색"

parser = argparse.ArgumentParser()
parser.add_argument("--product", required=False, default="oximeter")
parser.add_argument(
    "--show-browser",
    action="store_true",
    help="Show browser during MFDS data collection (debug only)"
)
args, _ = parser.parse_known_args()

SEARCH_VALUE = args.product
SHOW_BROWSER = args.show_browser

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ==========================================


# ================= UTILITIES =================

def safe_json_parse(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1].strip()
    return json.loads(content)


def normalize_risk_class(raw):
    if not raw:
        return "Unknown"
    raw = raw.strip()
    if raw.lower().startswith("class"):
        return raw
    return f"Class {raw}"


def call_llm(raw_text):
    prompt = f"""
You are a regulatory analyst assistant.

The text below is raw evidence from MFDS (South Korea).
Your task is to extract and translate product information.

Rules:
- Do NOT invent approval or compliance claims
- Preserve original Korean text
- Translate faithfully
- If intended use is not explicit, derive a conservative functional use
  based on device description and common clinical usage
- Clearly flag derived interpretations
- Output STRICT JSON only (no markdown, no commentary)

Required JSON schema:
{{
  "product_name": {{ "original_ko": "", "translated_en": "" }},
  "device_description": {{ "original_ko": "", "translated_en": "" }},
  "intended_use": {{ "original_ko": "", "translated_en": "" }},
  "risk_class": "",
  "approval_number": "",
  "approval_date": "",
  "confidence_notes": ""
}}

MFDS TEXT:
\"\"\"{raw_text[:12000]}\"\"\"
"""

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cautious regulatory analyst who outputs valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        },
        timeout=60
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenAI API error [{response.status_code}]: {response.text}"
        )

    content = response.json()["choices"][0]["message"]["content"]
    return safe_json_parse(content)


META = {
    "regulated_product_type": "medical_device",
    "country": "South Korea",
    "regulatory_authority": "MFDS"
}


def build_about_device(p, derived=False, confidence_note=None):
    text = (
        f"The {p['product_name']} is a regulated product listed in the MFDS public "
        f"product database."
    )

    if p.get("device_description"):
        text += (
            f" Based on publicly available listing information, it is a medical "
            f"device designed to {p['device_description'].rstrip('.')}."
        )

    if p.get("intended_use"):
        text += f" It is intended to {p['intended_use'].rstrip('.')}."

    if derived:
        text += (
            " Where explicit intended use was not clearly stated in the MFDS listing, "
            "a conservative functional use has been derived for procurement reference "
            "based on device description and common clinical application."
        )

    if confidence_note:
        text += f" Confidence note: {confidence_note.strip()}"

    text += (
        " This description is derived from interpreted information available in MFDS "
        "public product listings and is provided for internal procurement reference only."
    )

    return text


def build_classification(p):
    text = (
        f"According to publicly available information in the MFDS e-Medi system, "
        f"the device is listed as a {p['risk_class']} medical device in South Korea."
    )

    if p.get("approval_number"):
        text += f" The MFDS record includes an approval reference number ({p['approval_number']})."

    text += (
        " This classification information is reported as identified in MFDS public records "
        "and is provided for internal reference and procurement planning purposes only."
    )

    return text


# ================= MAIN =================

def run():
    print("MFDS Step 3 to Step 4 started")

    raw_evidence = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not SHOW_BROWSER)
        page = browser.new_page()

        page.goto(MFDS_SEARCH_URL, timeout=60000)
        page.wait_for_load_state("networkidle")

        page.get_by_label(SEARCH_LABEL).fill(SEARCH_VALUE)
        page.get_by_role("button", name=SEARCH_BUTTON_TEXT, exact=True).click()

        try:
            page.wait_for_selector("table tbody tr", timeout=10000)
            page.locator("table tbody tr").first.locator("a").first.click()
            page.wait_for_load_state("networkidle")

            visible_text = page.locator("body").inner_text()

            raw_evidence = {
                "source_url": page.url,
                "page_title": page.title(),
                "access_date": datetime.utcnow().isoformat(),
                "visible_text": visible_text,
                "human_verified": False
            }

            with open(f"{OUTPUT_DIR}/step3_raw_evidence.json", "w", encoding="utf-8") as f:
                json.dump(raw_evidence, f, ensure_ascii=False, indent=2)

            print("[OK] Step 3 evidence captured")

        except Exception:
            print("[WARN] No valid MFDS product found in public listings")

        browser.close()

    if not raw_evidence:
        print("[WARN] Falling back to conservative Step-4 output")

        step4_output = {
            "meta": META,
            "product_identity": {"product_name": SEARCH_VALUE},
            "about_device": {
                "section_title": "About the Device",
                "content": (
                    "No publicly available MFDS product listing with normal status was "
                    "identified for this product designation at the time of review. "
                    "This description is based on general product understanding and is "
                    "provided for internal procurement reference only."
                )
            },
            "classification": {
                "section_title": "Classification",
                "content": (
                    "Public MFDS classification information could not be identified "
                    "from available listings. Risk classification and regulatory "
                    "pathway should be confirmed through formal regulatory assessment."
                ),
                "risk_class": "Unknown",
                "approval_number": "",
                "approval_date": ""
            },
            "evidence_traceability": {
                "source_url": MFDS_SEARCH_URL,
                "accessed_at": datetime.utcnow().isoformat()
            }
        }

        with open(f"{OUTPUT_DIR}/step4_product_understanding.json", "w", encoding="utf-8") as f:
            json.dump(step4_output, f, indent=2, ensure_ascii=False)

        print("[OK] Step 4 generated with conservative fallback")
        return

    interpreted = call_llm(raw_evidence["visible_text"])

    derived_intended_use = False
    if not interpreted["intended_use"]["translated_en"]:
        interpreted["intended_use"]["translated_en"] = interpreted["device_description"]["translated_en"]
        derived_intended_use = True

    procurement = {
        "product_name": interpreted["product_name"]["translated_en"] or SEARCH_VALUE,
        "device_description": interpreted["device_description"]["translated_en"],
        "intended_use": interpreted["intended_use"]["translated_en"],
        "risk_class": normalize_risk_class(interpreted["risk_class"]),
        "approval_number": interpreted["approval_number"],
        "approval_date": interpreted["approval_date"],
        "confidence_notes": interpreted.get("confidence_notes")
    }

    step4_understanding = {
        "meta": META,
        "product_identity": {"product_name": procurement["product_name"]},
        "about_device": {
            "section_title": "About the Device",
            "content": build_about_device(
                procurement,
                derived=derived_intended_use,
                confidence_note=procurement.get("confidence_notes")
            )
        },
        "classification": {
            "section_title": "Classification",
            "content": build_classification(procurement),
            "risk_class": procurement["risk_class"],
            "approval_number": procurement["approval_number"],
            "approval_date": procurement["approval_date"]
        },
        "evidence_traceability": {
            "source_url": raw_evidence["source_url"],
            "accessed_at": raw_evidence["access_date"]
        }
    }

    with open(f"{OUTPUT_DIR}/step4_product_understanding.json", "w", encoding="utf-8") as f:
        json.dump(step4_understanding, f, indent=2, ensure_ascii=False)

    print("[OK] Step 4 product understanding generated")
    print("[OK] Script completed cleanly")


if __name__ == "__main__":
    run()
