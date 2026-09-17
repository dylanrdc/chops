import os
from pathlib import Path
import pydicom

def inspect_single_dicom():
    print("\n\n=== Mammography Naming Feature Inspector (NHS3 Collection by Cizz-l Lockhart) ===\n\n")

    
    # 1. Prompt the user for the file path
    user_input = input("Enter the path to your DICOM file (e.g., sample.dcm): ").strip()
    
    # Remove surrounding quotes if the user dragged and dropped the file into the terminal
    user_input = user_input.strip("'\"")
    file_path = Path(user_input)
    
    # Check if the file actually exists
    if not file_path.exists():
        print(f"Error: The file '{file_path}' does not exist. Please check the path.")
        return
        
    if not file_path.is_file():
        print(f"Error: '{file_path}' is a directory, not a file.")
        return

    # Read and print the metadata
    try:
        ds = pydicom.dcmread(file_path, stop_before_pixels = True)

        # extract the features that we care about: Extract targeted features (using fall back defaults)
        breast = getattr(ds, "ImageLaterality", "UNK-SIDE").strip()   # Usually 'R' or 'L'
        view = getattr(ds, "ViewPosition", "UNK-VIEW").strip()        # Usually 'CC' or 'MLO'
        raw_date = getattr(ds, "StudyDate", "00000000").strip()      # Formatted as YYYYMMDD
        
        # Clean up the date components
        if len(raw_date) == 8 and raw_date.isdigit():
            year = raw_date[0:4]
            month = raw_date[4:6]
            day = raw_date[6:8]
            formatted_date = f"{month}{year[2:4]}"
        else:
            year, month, day = "0000", "00", "00"
            formatted_date = "Unknown Date"

        # Print the extracted features first so you see them
        print("\n" + "="*45)
        print("EXTRACTED DICOM METADATA:")
        print("="*45)
        print(f"  • Original Patient ID in File: {getattr(ds, 'PatientID', 'N/A')}")
        print(f"  • Breast Laterality:          {breast} ({'Right' if breast == 'R' else 'Left' if breast == 'L' else 'Unknown'})")
        print(f"  • View Position:              {view}")
        print(f"  • Acquisition Year:           {year}")
        print(f"  • Full Study Date:            {formatted_date}")
        print("="*45)

        # 3. Prompt user for a custom ID
        custom_id = input("Enter the preferred User ID for this file: ").strip()
        
        # Sanitize the user input to remove characters illegal in file names
        clean_custom_id = "".join(c for c in custom_id if c.isalnum() or c in ('-', '_')).strip()
        if not clean_custom_id:
            clean_custom_id = "USER-ID-REQUIRED"

        # 4. Preview your custom filename rule
        # Convention: UserID_Year_Breast_View.dcm
        preferred_name = f"{clean_custom_id}_{year}_{breast}_{view}.dcm"
        
        print("\n" + "="*45)
        print("PREVIEW OF PREFERRED FILENAME CONVENTION:")
        print(f"{preferred_name}")
        print("="*45)
        
    except pydicom.errors.InvalidDicomError:
        print(f"Error: '{file_path.name}' is not a valid DICOM file or it is corrupted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_single_dicom()
