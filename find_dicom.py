import pydicom

# Get the list of absolute paths to all downloaded test files
paths = pydicom.data.get_testdata_files()

# Print the folder containing them
if paths:
    from pathlib import Path
    print("Your test data is located here:")
    print(Path(paths[0]).parent)
else:
    print("No files found. Run pydicom.data.fetch_data_files() first.")

