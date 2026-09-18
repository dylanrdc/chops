import os
from pathlib import Path
import pydicom

def sort_and_rename_dicoms():
    print("\n\n=== Mammography Naming Feature Inspector (NHS3 Collection by Cizz-l Lockhart) ===\n\n")

    
    # 1. Prompt the user for the file path
    user_input = input("Enter the path to your DICOM directory (e.g., sample.dcm): ").strip()
    
    # Remove surrounding quotes (if the user dragged and dropped the file into the terminal)
    user_input = user_input.strip("'\"")
    dir_path = Path(user_input)
    
    # Check if the folder actually exists
    if not dir_path.exists():
        print(f"Error: The directory '{dir_path}' does not exist. Please check the path.")
        return
    
    if not dir_path.is_file():
        print(f"Error: '{dir_path}' is a directory, not a file.")
        return

    print(f"\n Scanning directory for DICOM Files...\n")

    # Preallocate group files by PATIENT ID (GIVEN) in dict called patient_groups
    patient_groups={}

    for file_path in dir_path.iterdir():
        if file_path.is_file():

            try: 
                # read metadata, exclude the mammography data
                ds = pydicom.dcmread(file_path, stop_before_pixels = True)
                patient_id = getattr(ds, "PATIENTID", "UNK_PAT").strip()

                if patient_id not in patient_groups:
                    patient_groups[patient_id] = []
                patient_groups[patient_id].append((file_path,ds))

            except (pydicom.errors.InvalidDicomError, PermissionError ):
                # skipping non-DICOM files, or files that cannot be read
                continue

        if not patient_groups:
            print("No valid DICOM files found in directory.")
            return


        sorted_patient_ids = sorted(patient_groups.keys())

        print(f"Found {len(patient_groups)} unique patient ID(s). Starting sorting and renaming process... \n")

        for idx, pid in enumerate(sorted_patient_ids, 1):
            print("\n" + "="*55)
            print(f"PATIENT {idx}/{len(sorted_patient_ids)}: Original Patient ID -> '{pid}'")
            print(f"Contains {len(patient_groups[pid])} files")
            print("="*55)

            # Prompt user for a custom ID for this specific patient group
            custom_id = input(f"Enter the preferred User ID for Patient '{pid}': ").strip()

            # Sanitize the user input to remove characters illegal in file names
            clean_custom_id = "".join(c for c in custom_id if c.isalnum() or c in ('-', '_')).strip()
            if not clean_custom_id:
                clean_custom_id = f"USER-{pid}"

            #Create a new output folder inside the directory
            output_folder = dir_path / pid
            output_folder.mkdir(parents=True, exist_ok=True)

            for file_path, ds in patient_groups[pid]:
                # Extract targeted features

                breast = getattr(ds, "ImageLaterality", "UNK-SIDE").strip() # RIGHT OR LEFT BREAST
                view = getattr(ds, "ViewPosition", "UNK-VIEW").strip()      # USUALLY CC or MLO
                raw_date = getattr(ds, "StudyDate", "00000000").strip()     # Formatted date 

                frames_attr = getattr(ds, "NumberofFrames", 1).strip()              # number of frames
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
                    day = raw_date[6:8]
                    formatted_date = f"{month}{year[2:4]}"
                else:
                    formatted_date = "Unknown Date"

                # Preferred naming convention
                preferred_name = f"{clean_custom_id}_{formatted_date}_{breast}_{view}.dcm"
                new_file_path = output_folder / preferred_name

                # Handle potential filename collisions (if two files have identical metadata)
                counter = 1
                while new_file_path.exists():
                    preferred_name = f"{clean_custom_id}_{formatted_date}_{breast}_{view}_{counter}.dcm"
                    new_file_path = output_folder / preferred_name
                    counter += 1

                # Move and rename the file into the sorted patient directory
                try:
                    file_path.rename(new_file_path)
                    print(f"  → Organized: {file_path.name} -> {pid}/{preferred_name}")
                except Exception as e:
                    print(f"  × Error moving file {file_path.name}: {e}")

        # display complete process 
        print("\nSorting and renaming process complete!")

    if __name__ == "__main__":
        sort_and_rename_dicoms()
                    