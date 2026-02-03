import streamlit as st
import subprocess
import os
import sys

st.set_page_config(page_title="Regulatory Procurement Review", layout="centered")

st.title("Regulatory Procurement Review Tool")

# --- Inputs ---
country = st.selectbox(
    "Select Country",
    ["South Korea (MFDS)"]
)

product = st.text_input(
    "Enter Medical Device Name",
    placeholder="e.g. Skin Infrared Thermometer"
)

run = st.button("Generate Review")

OUTPUT_DIR = "output"

# --- Action ---
if run:
    if not product.strip():
        st.error("Please enter a product name.")
    else:
        with st.spinner("Generating regulatory review..."):
            cmd = [
                sys.executable,
                "run_mfds_review_poc.py",
                "--product",
                product
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

        if result.returncode != 0:
            st.error("Error during review generation")

            if result.stderr:
                st.subheader("Pipeline error (stderr)")
                st.code(result.stderr)

            if result.stdout:
                st.subheader("Pipeline output (stdout)")
                st.code(result.stdout)

        else:
            st.success("Regulatory review generated successfully")

            # --- Robust file discovery (DO NOT GUESS FILE NAME) ---
            if not os.path.exists(OUTPUT_DIR):
                st.warning("Output directory not found.")
            else:
                generated_files = [
                    f for f in os.listdir(OUTPUT_DIR)
                    if f.lower().startswith("mfds_procurement_review")
                ]

                if not generated_files:
                    st.warning("Review document not found.")
                else:
                    latest_file = max(
                        generated_files,
                        key=lambda f: os.path.getmtime(os.path.join(OUTPUT_DIR, f))
                    )

                    file_path = os.path.join(OUTPUT_DIR, latest_file)

                    st.download_button(
                        label="Download Review Document",
                        data=open(file_path, "rb"),
                        file_name=latest_file,
                        mime="text/markdown"
                    )
