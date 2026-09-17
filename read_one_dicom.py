import os
from pathlib import Path
import pydicom

def inspect_single_dicom():
    print("=== DICOM Metadata Inspector ===")
    
    # 1. Prompt the user for the file path
    user_input = input("Enter the path to your DICOM file (e.g., sample.dcm): ").strip()
    
    # Remove surrounding quotes if the user dragged and dropped the file into the terminal
    user_input = user_input.strip("'\"")
    file_path = Path(user_input)
    
    # 2. Check if the file actually exists
    if not file_path.exists():
        print(f"❌ Error: The file '{file_path}' does not exist. Please check the path.")
        return
        
    if not file_path.is_file():
        print(f"❌ Error: '{file_path}' is a directory, not a file.")
        return

    # 3. Read and print the metadata
    try:
        print(f"\nReading metadata for: {file_path.name}...")
        
        # Using stop_before_pixels=True loads the headers instantly without wasting memory on pixels
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        
        print("\n" + "="*50)
        print(f"  FULL DICOM HEADER DUMP")
        print("="*50)
        
        # Printing the dataset directly shows all hex tags, VRs, keywords, and values
        print(ds)
        
        print("="*50)
        print("🎉 Read complete!")
        
    except pydicom.errors.InvalidDicomError:
        print(f"❌ Error: '{file_path.name}' is not a valid DICOM file or it is corrupted.")
    except Exception as e:
        print(f"💥 An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_single_dicom()
