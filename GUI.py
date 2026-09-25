import customtkinter as ctk
from tkinter import filedialog

# Initialize the CustomTkinter window
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

class PathSelectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mammography DICOM Renaming Tool - Select Target Folder")
        self.geometry("600x150")

        # Create a label/title
        self.label = ctk.CTkLabel(self, text="Select a Target Folder:", font=("Arial", 14, "bold"))
        self.label.pack(pady=(15, 5), padx=20, anchor="w")

        # Frame to hold the entry box and button side-by-side
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.selection_frame.pack(fill="x", padx=20, pady=5)

        # Entry widget to display the selected path
        self.path_entry = ctk.CTkEntry(self.selection_frame, placeholder_text="No folder selected")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Browse button
        self.browse_button = ctk.CTkButton(self.selection_frame, text="Browse...", width=100, command=self.browse_folder)
        self.browse_button.pack(side="right")

    def browse_folder(self):
        # Open the standard directory selection dialog
        selected_directory = filedialog.askdirectory(title="Select a Folder")
        
        if selected_directory:
            # Clear previous text and insert the new path
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, selected_directory)

            print(selected_directory)  # Print the selected directory to the console

if __name__ == "__main__":
    app = PathSelectorApp()
    app.mainloop()
