import json
import os

OUTPUT_DIR = "output"

STEP1_2_FILE_OUTPUT = "output/step1_step2_static.json"
STEP1_2_FILE_ROOT = "step1_step2_static.json"
STEP4_FILE = f"{OUTPUT_DIR}/step4_product_understanding.json"
STEP5_8_FILE = f"{OUTPUT_DIR}/step5_to_step8_sections.json"
STEP9_FILE = f"{OUTPUT_DIR}/step9_conclusion.json"


def load_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Required file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def section_md(title, content):
    return f"## {title}\n\n{content}\n\n"


def run():
    if os.path.exists(STEP1_2_FILE_OUTPUT):
        step1_2 = load_json(STEP1_2_FILE_OUTPUT)
    elif os.path.exists(STEP1_2_FILE_ROOT):
        print("[INFO] Using Step 1–2 static file from repo root")
        step1_2 = load_json(STEP1_2_FILE_ROOT)
    else:
        raise FileNotFoundError(
            "Step 1–2 static file not found in output/ or repo root"
        )

    step4 = load_json(STEP4_FILE)
    step5_8 = load_json(STEP5_8_FILE)
    step9 = load_json(STEP9_FILE)

    product_name = step4["product_identity"]["product_name"]
    output_file = f"{OUTPUT_DIR}/MFDS_Procurement_Review_{product_name.replace(' ', '_')}.md"

    doc = []

    # Title
    doc.append(f"# Regulatory Review for Procuring {product_name} in South Korea\n\n")

    # Step 1
    doc.append(
        section_md(
            step1_2["step1_regulatory_authority"]["section_title"],
            step1_2["step1_regulatory_authority"]["content"]
        )
    )

    # Step 2
    doc.append(
        section_md(
            step1_2["step2_key_regulations"]["section_title"],
            step1_2["step2_key_regulations"]["content"]
        )
    )

    # Step 4 – About Device
    doc.append(
        section_md(
            step4["about_device"]["section_title"],
            step4["about_device"]["content"]
        )
    )

    # Step 4 – Classification
    doc.append(
        section_md(
            step4["classification"]["section_title"],
            step4["classification"]["content"]
        )
    )

    # Step 5–8
    for key in [
        "step5_regulatory_considerations",
        "step6_documents_required",
        "step7_labeling_udi_pms",
        "step8_procurement_impact"
    ]:
        section = step5_8.get(key)
        if section:
            doc.append(
                section_md(
                    section["section_title"],
                    section["content"]
                )
            )

    # Step 9 – Conclusion
    doc.append(
        section_md(
            step9["step9_conclusion"]["section_title"],
            step9["step9_conclusion"]["content"]
        )
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(doc))

    print(f"Master review document generated: {output_file}")


if __name__ == "__main__":
    run()
