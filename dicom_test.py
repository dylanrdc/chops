import os
import shutil
from pathlib import Path
import pydicom

# --- 1. YOUR EXACT FUNCTION ---
def organize_dicom_by_patient_id(source_dir, output_dir=None):
    source_path = Path(source_dir)
    dest_path = Path(output_dir) if output_dir else source_path

    for file_path in source_path.iterdir():
        if file_path.is_dir():
            continue

        try:
            ds = pydicom.dcmread(file_path, stop_before_pixels=True)
            patient_id = getattr(ds, 'PatientID', '').strip()
            if not patient_id:
                patient_id = "Unknown_Patient"

            clean_patient_id = "".join(c for c in patient_id if c.isalnum() or c in (' ', '_', '-')).strip()
            patient_folder = dest_path / clean_patient_id
            patient_folder.mkdir(parents=True, exist_ok=True)

            target_file_path = patient_folder / file_path.name
            shutil.move(str(file_path), str(target_file_path))
            print(f"Moved: {file_path.name} -> Folder: {clean_patient_id}")

        except pydicom.errors.InvalidDicomError:
            print(f"Skipped (Not a valid DICOM file): {file_path.name}")
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")


# --- 2. EXECUTION CODE WITH AUTOMATIC PATH FINDING ---
if __name__ == "__main__":
    # 1. Dynamically locate the pydicom test folder using the library itself
    paths = pydicom.data.get_testdata_files()
    
    if not paths:
        print("No toy files found. Fetching them first...")
        pydicom.data.fetch_data_files()
        paths = pydicom.data.get_testdata_files()

    # Get the parent directory of the first found test file
    toy_data_source = Path(paths[0]).parent
    print(f"Automatically located toy data at: {toy_data_source}")

    # 2. Setup a safe local directory sandbox
    LOCAL_TEST_DIR = Path("./my_test_sandbox")
    LOCAL_TEST_DIR.mkdir(exist_ok=True)

    print("Step 1: Safely copying toy data to your local sandbox...")
    copied_count = 0
    
    # Loop through the files found in the dynamic path
    for file_path in toy_data_source.iterdir():
        if file_path.is_file():
            try:
                # Validate and copy out of the hidden system directory
                pydicom.dcmread(file_path, stop_before_pixels=True)
                shutil.copy(file_path, LOCAL_TEST_DIR / f"{file_path.stem}.dcm")
                copied_count += 1
            except Exception:
                continue 

    print(f"--> Copied {copied_count} files into '{LOCAL_TEST_DIR.resolve()}'\n")
    print("Step 2: Running your organization function...")
    
    # 3. Run your function on the safe local copy
    organize_dicom_by_patient_id(source_dir=LOCAL_TEST_DIR)
    
    print(f"\nSuccess! Check './my_test_sandbox' to see the sorted patient folders.")
