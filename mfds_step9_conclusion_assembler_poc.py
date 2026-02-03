import json
import os

STEP4_FILE = "output/step4_product_understanding.json"
STEP5_8_FILE = "output/step5_to_step8_sections.json"
OUTPUT_FILE = "output/step9_conclusion.json"


def normalize_risk_class(risk_class):
    mapping = {
        "Class 1": "Class I",
        "Class 2": "Class II",
        "Class 3": "Class III",
        "Class 4": "Class IV"
    }
    return mapping.get(risk_class, risk_class)


def build_step9_conclusion(product_type, risk_class, approval_number=None):
    disclaimer_required = False

    if product_type != "medical_device":
        content = (
            "Based on the available public information, the product is identified within "
            "its regulated category under the MFDS framework. Regulatory and procurement "
            "considerations are expected to vary depending on the applicable classification "
            "and regulatory pathway."
        )
        disclaimer_required = True

    else:
        if risk_class == "Class I":
            content = (
                "Based on the available public information and the identified classification, "
                "the product is considered a lower-risk medical device under the MFDS "
                "regulatory framework. From a procurement perspective, the product may be "
                "considered suitable for sourcing provided that applicable MFDS notification "
                "requirements, labeling compliance, and supplier authorization are verified "
                "prior to purchase."
            )

        elif risk_class == "Class II":
            content = (
                "Based on the available public information and the identified Class II "
                "classification, the product is considered to fall within a moderate-risk "
                "category under the MFDS regulatory framework. From a procurement perspective, "
                "the product may be considered suitable for sourcing provided that MFDS "
                "approval or certification status, Korean License Holder authorization, "
                "approved intended use alignment, and documentation completeness are verified "
                "prior to purchase."
            )

        elif risk_class == "Class III":
            content = (
                "Based on the available public information and the identified Class III "
                "classification, the product is considered a higher-risk medical device under "
                "the MFDS regulatory framework. Procurement activities for this product should "
                "be supported by early and thorough regulatory planning, including confirmation "
                "of MFDS approval status, documentation readiness, and regulatory timelines "
                "prior to sourcing decisions."
            )

        elif risk_class == "Class IV":
            content = (
                "Based on the available public information and the identified Class IV "
                "classification, the product is subject to the highest level of regulatory "
                "oversight under the MFDS framework. Procurement decisions for this product "
                "should be supported by comprehensive regulatory planning, extensive "
                "documentation review, and early engagement with regulatory and compliance "
                "stakeholders prior to sourcing."
            )

        else:
            content = (
                "Based on the available public information, the product is subject to MFDS "
                "regulatory oversight. Procurement and regulatory expectations should be "
                "confirmed based on the applicable classification during formal regulatory "
                "assessment."
            )
            disclaimer_required = True

    # Apply disclaimer ONLY when confidence is insufficient
    if not approval_number or risk_class == "Unknown" or disclaimer_required:
        content += (
            " This conclusion is based on publicly available information and general "
            "regulatory expectations and is provided for internal procurement reference "
            "only. Formal regulatory confirmation is required prior to submission, import, "
            "or market supply."
        )

    return {
        "section_title": "Conclusion and Procurement Recommendation",
        "content": content
    }


def run():
    if not os.path.exists(STEP4_FILE):
        raise FileNotFoundError("step4_product_understanding.json not found")

    if not os.path.exists(STEP5_8_FILE):
        raise FileNotFoundError("step5_to_step8_sections.json not found")

    with open(STEP4_FILE, "r", encoding="utf-8") as f:
        step4 = json.load(f)

    product_type = step4["meta"]["regulated_product_type"]
    risk_class_raw = step4["classification"]["risk_class"]
    risk_class = normalize_risk_class(risk_class_raw)
    approval_number = step4["classification"].get("approval_number")

    output = {
        "step9_conclusion": build_step9_conclusion(
            product_type,
            risk_class,
            approval_number=approval_number
        )
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("[OK] Step-9 conclusion assembled successfully")


if __name__ == "__main__":
    run()
