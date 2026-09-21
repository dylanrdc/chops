import os
import shutil
from pathlib import Path
import pydicom
"""


Mammography NH3 Feature Inspector (managed by @nhclo)
written by @n2dyd

"""

def sort_and_rename_dicoms():
    print("\n\n=== Mammography Naming Feature Inspector (managed by @nhclo) ===\n\n")
    
    # Prompt the user for the file path
    user_input = input("Enter the path to your DICOM directory: ").strip()
    
    # Remove surrounding quotes (if the user dragged and dropped the folder into the terminal)
    user_input = user_input.strip("'\"")
    dir_path = Path(user_input)
    
    # Check if the folder actually exists
    if not dir_path.exists():
        print(f"Error: The directory '{dir_path}' does not exist. Please check the path.")
        return
        
    if not dir_path.is_dir():
        print(f"Error: '{dir_path}' is a file, not a directory.")
        return

    print(f"\nScanning directory for DICOM Files...\n")
    
    # Group files by Patient ID preallocation
    patient_groups = {}
    skipped_non_mammo = 0

    for file_path in dir_path.iterdir():
        if file_path.is_file():
            try:
                # Read metadata, stopping before pixel data for speed
                ds = pydicom.dcmread(file_path, stop_before_pixels=True)
                modality = str(getattr(ds, "Modality", "")).strip().upper()
                if modality  !="MG":
                        skipped_non_mammo += 1
                        continue
                
                # Fetch element values safely as strings
                patient_id = str(getattr(ds, "PatientID", "UNK_PAT")).strip()
                if not patient_id or patient_id.lower() == "none":
                    patient_id = "UNK_PAT"
                
                if patient_id not in patient_groups:
                    patient_groups[patient_id] = []
                patient_groups[patient_id].append((file_path, ds))
            except (pydicom.errors.InvalidDicomError, PermissionError):
                # Skipping non-DICOM files or unreadable files
                continue


    # Report if no valid DICOM files were found
    if not patient_groups:
        print("No valid DICOM files found in directory.")
        return

    # Report the number of non-mammography files skipped
    print(f"Skipped {skipped_non_mammo} non-mammography file(s) (Modality != 'MG').")

    sorted_patient_ids = sorted(patient_groups.keys())
    print(f"Found {len(patient_groups)} unique patient ID(s). Starting sorting and renaming process... \n")

    for idx, pid in enumerate(sorted_patient_ids, 1):
        print("\n" + "="*55)
        print(f"PATIENT {idx}/{len(sorted_patient_ids)}: Original Patient ID -> '{pid}'")
        print(f"Contains {len(patient_groups[pid])} files")
        patient_name = str(getattr(patient_groups[pid][0][1], "PatientName", "UNK_NAME")).strip()
        print(f"Patient Name (from DICOM): {patient_name}")
        print("="*55)
        
        # Prompt user for a custom ID for this specific patient group
        custom_id = input(f"Enter the preferred User ID for Patient '{pid}': ").strip()
        
        # Sanitize the user input
        clean_custom_id = "".join(c for c in custom_id if c.isalnum() or c in ('-', '_')).strip()
        if not clean_custom_id:
            clean_custom_id = f"USER-{pid}"

        # --- Calculate Year Range ---
        years = set()
        for file_path, ds in patient_groups[pid]:
            raw_date = str(getattr(ds, "StudyDate", "")).strip()
            if len(raw_date) == 8 and raw_date.isdigit():
                years.add(int(raw_date[0:4]))

        if years:
            earliest_year = min(years)
            latest_year = max(years)
            if earliest_year == latest_year:
                year_range_str = f"_{earliest_year}"
            else:
                year_range_str = f"_{earliest_year}-{latest_year}"
        else:
            year_range_str = "_UnknownYears"

        # Base valid folder format: UserID_Years
        standard_folder_name = f"{clean_custom_id}{year_range_str}"
        standard_output_folder = dir_path / standard_folder_name

        for file_path, ds in patient_groups[pid]:
            # --- 1. Robust Breast Laterality Check ---
            breast = str(getattr(ds, "ImageLaterality", "") or getattr(ds, "FrameLaterality", "") or getattr(ds, "Laterality", "")).strip()
            
            # Fallback to Segmented or Sequence-based laterality if root is missing
            if not breast or breast.lower() == "none" or breast == "":
                if "AnatomicalOrientationType" in ds:
                    breast = str(ds.AnatomicalOrientationType).strip()
            
            # Deep sequence nesting lookup for laterality
            if not breast or breast.lower() == "none" or breast == "":
                if "SharedFunctionalGroupsSequence" in ds and len(ds.SharedFunctionalGroupsSequence) > 0:
                    shared_seq = ds.SharedFunctionalGroupsSequence[0]
                    if "FrameAnatomySequence" in shared_seq and len(shared_seq.FrameAnatomySequence) > 0:
                        fa_seq = shared_seq.FrameAnatomySequence[0]
                        breast = str(getattr(fa_seq, "FrameLaterality", "")).strip()

            if not breast or breast.lower() == "none" or breast == "":
                breast = "UNK-SIDE"
                
            # --- 2. Robust View Position & Code Meaning Check ---
            view = str(getattr(ds, "ViewPosition", "")).strip()
            
            # Fallback 1: Check View Code Sequence -> Code Meaning (Common in digital mammography/tomos)
            if not view or view.lower() == "none" or view == "":
                if "ViewCodeSequence" in ds and len(ds.ViewCodeSequence) > 0:
                    code_meaning = str(getattr(ds.ViewCodeSequence[0], "CodeMeaning", "")).lower()
                    if "oblique" in code_meaning:
                        view = "MLO"
                    elif "cranio-caudal" in code_meaning or "craniocaudal" in code_meaning:
                        view = "CC"
                    elif code_meaning:
                        # Fallback to keeping it compact if it is a custom string
                        view = "".join([w.upper() for w in code_meaning.split() if w])

            # Fallback 2: Check original angle direction attribute
            if not view or view.lower() == "none" or view == "":
                view = str(getattr(ds, "PositionerPrimaryAngleDirection", "")).strip()
                
            # Fallback 3: Dig into multi-frame/tomo functional groups for View Code sequence
            if not view or view.lower() == "none" or view == "":
                if "SharedFunctionalGroupsSequence" in ds and len(ds.SharedFunctionalGroupsSequence) > 0:
                    shared_seq = ds.SharedFunctionalGroupsSequence[0]
                    if "VisualEvaluationSequence" in shared_seq and len(shared_seq.VisualEvaluationSequence) > 0:
                        # Some vendors store positioning variants here
                        view_attr = getattr(shared_seq.VisualEvaluationSequence[0], "ViewPosition", "")
                        if view_attr:
                            view = str(view_attr).strip()

            if not view or view.lower() == "none" or view == "":
                view = "UNK-VIEW"

            # --- 3. Extract Meta Information ---
            raw_date = str(getattr(ds, "StudyDate", "00000000")).strip()
            
            # Extract NumberOfFrames
            frames_attr = getattr(ds, "NumberOfFrames", 1)
            try:
                frames = int(frames_attr) if frames_attr is not None else 1
            except (ValueError, TypeError):
                frames = 1

            tomo_suffix = ""
            if frames > 1:
                print(f"Detected Tomosynthesis for {file_path.name}")
                tomo_suffix = "_tomo"

            # Clean up the date components
            if len(raw_date) == 8 and raw_date.isdigit():
                year = raw_date[0:4]
                month = raw_date[4:6]
                formatted_date = f"{month}{year[2:4]}"
            else:
                formatted_date = "UnknownDate"

            # Check if this file is missing metadata features
            is_unknown = (breast == "UNK-SIDE" or view == "UNK-VIEW")

            # Route to the appropriate folder structure
            if is_unknown:
                tomo_type_folder = "TOMO" if frames > 1 else "NON-TOMO"
                output_folder = standard_output_folder / "UNK_PATIENTS" / tomo_type_folder
                current_folder_log_name = f"UNK_PATIENTS/{tomo_type_folder}"
            else:
                output_folder = standard_output_folder
                current_folder_log_name = standard_folder_name

            # Ensure the designated output folder exists
            output_folder.mkdir(parents=True, exist_ok=True)

            # Preferred naming convention
            preferred_name = f"{clean_custom_id}_{formatted_date}_{breast}_{view}{tomo_suffix}.dcm"
            
            # Clean illegal file system string elements
            preferred_name = preferred_name.replace("/", "-").replace("\\", "-")
            new_file_path = output_folder / preferred_name

            # Handle potential filename collisions
            counter = 2
            while new_file_path.exists():
                preferred_name = f"{clean_custom_id}_{formatted_date}_{breast}_{view}{tomo_suffix}_{counter}.dcm"
                preferred_name = preferred_name.replace("/", "-").replace("\\", "-")
                new_file_path = output_folder / preferred_name
                counter += 1

            # Copy the file instead of moving it
            try:
                shutil.copy2(file_path, new_file_path)
                print(f" → Organized (Copied): {file_path.name} -> {current_folder_log_name}/{preferred_name}")
            except Exception as e:
                print(f" × Error copying file {file_path.name}: {e}")

    print("\nSorting and renaming process complete!")

if __name__ == "__main__":
    sort_and_rename_dicoms()
