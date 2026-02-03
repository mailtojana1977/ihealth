import subprocess
import sys
import os
import argparse

SCRIPTS = [
    "mfds_step3_to_step4_poc.py",
    "mfds_step5_to_step8_assembler_poc.py",
    "mfds_step9_conclusion_assembler_poc.py",
    "mfds_master_review_assembler.py"
]


def run_script(script_name, product_name):
    print(f"\n>> Running {script_name}...")
    result = subprocess.run(
        [sys.executable, script_name, "--product", product_name],
        capture_output=True,
        text=True,
        cwd=os.getcwd() 
    )

    if result.returncode != 0:
        print(f"[ERROR] {script_name}")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", required=True, help="Medical device name to search in MFDS")
    args = parser.parse_args()

    product_name = args.product

    print("Starting MFDS Procurement Review Pipeline")
    print(f"Product selected: {product_name}")

    # Sanity check
    for script in SCRIPTS:
        if not os.path.exists(script):
            print(f"[ERROR] Missing script: {script}")
            sys.exit(1)

    # Execute pipeline
    for script in SCRIPTS:
        run_script(script, product_name)

    print("\n[OK] MFDS Procurement Review Document generated successfully")


if __name__ == "__main__":
    run()
