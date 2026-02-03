import json
import os

INPUT_FILE = "output/step4_product_understanding.json"
OUTPUT_FILE = "output/step5_to_step8_sections.json"

# ==============================
# REGULATORY RULE VERSIONING
# ==============================
RULES_META = {
    "regulatory_rules_version": "MFDS_MD_RULES_v1.1",
    "rules_last_updated": "2026-02-01",
    "notes": "Enhanced procurement-oriented regulatory interpretation"
}

# ==============================
# UTILITIES
# ==============================
def normalize_risk_class(risk_class):
    mapping = {
        "Class 1": "Class I",
        "Class 2": "Class II",
        "Class 3": "Class III",
        "Class 4": "Class IV"
    }
    return mapping.get(risk_class, risk_class)


# ==============================
# STEP-5: REGULATORY CONSIDERATIONS
# ==============================
def build_step5(product_type, risk_class):
    if product_type != "medical_device":
        return None

    content = ""

    if risk_class == "Class I":
        content = (
            "Medical devices classified as Class I in South Korea are generally subject "
            "to lower-risk regulatory pathways with proportionate regulatory oversight. "
            "Such products are typically subject to notification or simplified registration "
            "processes depending on device characteristics."
        )

    elif risk_class == "Class II":
        content = (
            "Medical devices classified as Class II in South Korea are subject to MFDS "
            "regulatory pathways applicable to moderate-risk devices. Distribution is "
            "generally conducted through a Korean License Holder (KLH). Regulatory "
            "expectations commonly include MFDS registration or certification, quality "
            "system compliance, Korean-language labeling, applicable UDI requirements, "
            "and defined post-market obligations."
        )

    elif risk_class == "Class III":
        content = (
            "Medical devices classified as Class III are subject to enhanced MFDS regulatory "
            "oversight. Regulatory pathways typically involve detailed technical evaluation, "
            "conformity assessment, and increased pre-market scrutiny prior to approval."
        )

    elif risk_class == "Class IV":
        content = (
            "Medical devices classified as Class IV are subject to the highest level of MFDS "
            "regulatory scrutiny. Regulatory pathways generally involve comprehensive "
            "pre-market approval processes supported by extensive technical and clinical "
            "evidence."
        )

    # --- Procurement interpretation ---
    content += (
        "\n\nFor procurement purposes, the following regulatory elements should be "
        "verified prior to purchase:\n"
        "• Valid MFDS approval or certification status\n"
        "• Confirmed Korean License Holder (KLH)\n"
        "• Alignment of approved intended use with clinical application\n"
        "• Applicability of UDI and post-market obligations"
    )

    content += (
        "\n\nThis overview reflects regulatory expectations based on device classification "
        "and is provided for internal procurement reference."
    )

    return {
        "section_title": "Regulatory Considerations (Procurement-Focused)",
        "content": content
    }


# ==============================
# STEP-6: DOCUMENTATION REQUIRED
# ==============================
def build_step6(product_type, risk_class):
    if product_type != "medical_device":
        return None

    content = ""

    if risk_class == "Class I":
        content = (
            "Documentation typically associated with Class I medical devices includes "
            "basic product identification details, labeling materials, and administrative "
            "documentation relevant to the supply arrangement."
        )

    elif risk_class == "Class II":
        content = (
            "For Class II medical devices, procurement is typically supported by structured "
            "documentation demonstrating regulatory compliance. Common documentation may "
            "include MFDS approval or certification references, evidence of quality system "
            "compliance (e.g., KGMP), technical specifications, Korean-language labeling and "
            "instructions for use, UDI information where applicable, and authorization "
            "documentation for the Korean License Holder (KLH)."
        )

    elif risk_class in ["Class III", "Class IV"]:
        content = (
            "For Class III and Class IV medical devices, procurement is typically supported "
            "by extensive regulatory documentation. This may include comprehensive technical "
            "documentation, safety and performance evidence, quality system documentation, "
            "and, where applicable, clinical or post-market data."
        )

    content += (
        "\n\nFrom a procurement standpoint, documentation completeness should be confirmed "
        "prior to final supplier selection to mitigate regulatory and supply risks."
    )

    return {
        "section_title": "Documentation Expectations (Procurement-Oriented)",
        "content": content
    }


# ==============================
# STEP-7: LABELING / UDI / PMS
# ==============================
def build_step7(product_type):
    if product_type != "medical_device":
        return None

    content = (
        "Medical devices supplied in South Korea are expected to comply with Korean-language "
        "labeling and instructions for use requirements. Labeling typically includes product "
        "identification details, manufacturer and importer information, intended use, and "
        "warnings appropriate to the device type."
        "\n\nDepending on device classification and regulatory pathway, Unique Device "
        "Identification (UDI) requirements may apply. Post-market surveillance (PMS) "
        "responsibilities are generally assigned to the Korean License Holder and should be "
        "considered during supplier qualification."
        "\n\nFor procurement purposes, confirmation of labeling readiness and post-market "
        "support arrangements is recommended prior to purchase."
    )

    return {
        "section_title": "Labeling, Traceability, and Post-Market Considerations",
        "content": content
    }


# ==============================
# STEP-8: PROCUREMENT IMPACT
# ==============================
def build_step8(product_type, risk_class):
    if product_type != "medical_device":
        return None

    if risk_class == "Class I":
        content = (
            "Products in this classification are generally associated with lower regulatory "
            "complexity. Procurement timelines are typically shorter, with reduced regulatory "
            "coordination requirements."
        )

    elif risk_class == "Class II":
        content = (
            "Products classified as Class II are associated with moderate regulatory "
            "complexity. Procurement planning typically requires coordination with regulatory "
            "or compliance stakeholders, confirmation of MFDS approval status, and engagement "
            "of a Korean License Holder."
        )

    else:
        content = (
            "Products classified as Class III or Class IV are associated with higher "
            "regulatory complexity. Procurement planning may involve longer preparation "
            "timelines, increased regulatory coordination, and early engagement with "
            "regulatory, quality, and legal stakeholders."
        )

    return {
        "section_title": "Procurement Impact (Decision-Relevant)",
        "content": content
    }


# ==============================
# MAIN ASSEMBLER
# ==============================
def run():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError("step4_product_understanding.json not found")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    product_type = data["meta"]["regulated_product_type"]
    risk_class_raw = data["classification"]["risk_class"]
    risk_class = normalize_risk_class(risk_class_raw)

    output = {
        **RULES_META,
        "step5_regulatory_considerations": build_step5(product_type, risk_class),
        "step6_documents_required": build_step6(product_type, risk_class),
        "step7_labeling_udi_pms": build_step7(product_type),
        "step8_procurement_impact": build_step8(product_type, risk_class)
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("[OK] Step-5 to Step-8 (procurement-focused) sections assembled successfully")


if __name__ == "__main__":
    run()
