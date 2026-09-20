# Mammography DICOM Sorter & Renamer

A robust Python command-line utility designed to organize, sort, and rename Mammography and Tomosynthesis DICOM files. 

This script addresses a common issue in medical imaging datasets: **missing or nested metadata tags** (like `ViewPosition` or `ImageLaterality`). It utilizes deep-sequence fallback mapping to read vendor-specific tags, significantly reducing unclassifiable files (`UNK-VIEW` and `UNK-SIDE`).

## Features

- Deep Metadata Parsing: Looks beyond root-level tags into `ViewCodeSequence`, `SharedFunctionalGroupsSequence`, and `FrameAnatomySequence` to extract viewing angles (e.g., CC, MLO) and laterality.
- Smart Mapping: Automatically parses descriptive fields (like `"medio-lateral oblique"` or `"cranio-caudal"`) and maps them to standard shorthand (`MLO`, `CC`).
- Tomosynthesis Detection: Detects multi-frame 3D volumes and appends a `_tomo` suffix to distinguish them from standard 2D mammograms.
- Interactive Batch Processing: Groups images by `PatientID`, calculates chronological study year ranges for folder naming, and prompts you for clean, custom anonymized user IDs.
- Collision Protection: Ensures no files are overwritten by appending incremental counters if files share identical view properties.
- Safe Operations: Copies files to their new structure using `shutil.copy2` (preserving file timestamps), leaving your original dataset completely untouched.

## Output Structure Example

```text
Target_Directory/
│
├── USER-001_2022-2025/
│   ├── USER-001_1022_L_CC.dcm
│   ├── USER-001_1022_L_MLO.dcm
│   └── USER-001_0425_R_CC_tomo.dcm
│
└── USER-001_2022-2025/UNK_PATIENTS/
    ├── NON-TOMO/
    │   └── USER-001_1223_UNK-SIDE_UNK-VIEW.dcm
    └── TOMO/
        └── USER-001_1223_L_UNK-VIEW_tomo.dcm
```

##  Getting Started

### Prerequisites

You need **Python 3.7+** and `pydicom` installed.

```bash
pip install pydicom
```

### Installation

1. Clone this repository or download the script file:
   ```bash
   git clone https://github.com/dylanrdc/chops.git
   ```

2. Run the script:
   ```bash
   python sort_renamer.py
   ```

### How to Use

1. **Provide Directory**: Drag and drop your raw DICOM folder into the terminal or type the path manually when prompted.
2. **Assign Custom IDs**: The script groups files by their internal `PatientID` and asks you what you want to name the output folder for that specific patient (e.g., `Patient_A` or `Subj_005`). 
3. **Review**: Watch the terminal output trace each file as it maps, resolves sequences, and successfully copies into its newly sorted destination.

## Metadata Fallback Logic

When standard fields are empty, the script searches the following locations in order:

| Target Feature | Extraction Priority Order |
| :--- | :--- |
| **Laterality** | `ImageLaterality` ➔ `FrameLaterality` ➔ `AnatomicalOrientationType` ➔ `SharedFunctionalGroupsSequence.FrameAnatomySequence.FrameLaterality` |
| **View Position** | `ViewPosition` ➔ `ViewCodeSequence.CodeMeaning` (mapped to CC/MLO) ➔ `PositionerPrimaryAngleDirection` ➔ `SharedFunctionalGroupsSequence.VisualEvaluationSequence.ViewPosition` |

---
*Maintained for processing medical imaging datasets seamlessly.*

