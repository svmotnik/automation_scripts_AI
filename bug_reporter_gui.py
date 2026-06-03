import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import datetime
import subprocess

BASE_PATH = os.path.expanduser("~/BugReports")

class ProBugReporter:
    def get_active_window_name(self):
        try:
            wid = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            # Czyścimy nazwę okna z niedozwolonych znaków dla folderów
            name = subprocess.check_output(["xdotool", "getwindowname", wid]).decode().strip()
            return "".join([c if c.isalnum() or c in (" ", "_") else "_" for c in name])
        except: return "Unknown_Target"

    def get_next_id(self, target_folder):
        """Pobiera ID specyficzne dla danego Targetu."""
        id_file = os.path.join(target_folder, "last_id.txt")
        last_id = 0
        if os.path.exists(id_file):
            with open(id_file, "r") as f:
                try: last_id = int(f.read().strip())
                except: last_id = 0
        new_id = last_id + 1
        with open(id_file, "w") as f:
            f.write(str(new_id))
        return f"QA-{new_id:04d}"

    def __init__(self, root):
        self.root = root
        self.root.title("Bug Report System [QA Standard]")
        self.steps_entries = []
        self.env_entries = []
        self.files_to_attach = []
        self.active_window = self.get_active_window_name()
        
        header_frame = tk.Frame(root)
        header_frame.pack(fill="x", padx=10, pady=5)
        self.lbl_id = tk.Label(header_frame, text="ID: PENDING", font=("Arial", 10, "bold"), fg="red")
        self.lbl_id.pack(side="left")
        tk.Label(header_frame, text=f"Target: {self.active_window}", font=("Arial", 9, "italic"), fg="blue").pack(side="right")

        tk.Label(root, text="Summary", font=("Arial", 9, "bold")).pack(anchor="w", padx=10)
        self.txt_title = tk.Entry(root, width=70)
        self.txt_title.pack(padx=10)

        frame_meta = tk.Frame(root)
        frame_meta.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_meta, text="Severity:").pack(side="left")
        self.combo_severity = ttk.Combobox(frame_meta, values=["Blocker", "Critical", "Major", "Minor"], width=15)
        self.combo_severity.pack(side="left", padx=5)
        tk.Label(frame_meta, text="Platform:").pack(side="left", padx=(10,0))
        self.combo_platform = ttk.Combobox(frame_meta, values=["PC", "PS5", "Xbox Series X", "Switch"], width=15)
        self.combo_platform.pack(side="left", padx=5)

        env_header = tk.Frame(root)
        env_header.pack(fill="x", padx=10, pady=(5,0))
        tk.Label(env_header, text="Environment / Setup", font=("Arial", 9, "bold")).pack(side="left")
        tk.Button(env_header, text="+", command=self.add_env_field).pack(side="right")
        self.env_frame = tk.Frame(root)
        self.env_frame.pack(fill="x", padx=10)
        self.add_env_field()

        tk.Label(root, text="Build Information", font=("Arial", 9, "bold")).pack(anchor="w", padx=10)
        self.txt_build = tk.Entry(root, width=70)
        self.txt_build.pack(padx=10)

        steps_header = tk.Frame(root)
        steps_header.pack(fill="x", padx=10, pady=(10,0))
        tk.Label(steps_header, text="Steps to Reproduce", font=("Arial", 9, "bold")).pack(side="left")
        tk.Button(steps_header, text="+", command=self.add_step_field).pack(side="right")
        self.steps_frame = tk.Frame(root)
        self.steps_frame.pack(fill="x", padx=10)
        self.add_step_field()

        tk.Label(root, text="Expected Result", font=("Arial", 9, "bold")).pack(anchor="w", padx=10)
        self.txt_expected = tk.Entry(root, width=70)
        self.txt_expected.pack(padx=10)
        tk.Label(root, text="Actual Result", font=("Arial", 9, "bold")).pack(anchor="w", padx=10)
        self.txt_actual = tk.Entry(root, width=70)
        self.txt_actual.pack(padx=10)

        tk.Button(root, text="📁 Attach Evidence", command=self.select_files).pack(pady=10)
        self.lbl_attachment_status = tk.Label(root, text="No attachments", fg="red")
        self.lbl_attachment_status.pack()
        self.files_listbox = tk.Listbox(root, height=4, width=60)
        self.files_listbox.pack(padx=10, pady=5)
        
        tk.Button(root, text="SAVE REPORT", command=self.save_report, 
                  bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), height=2).pack(fill="x", padx=10, pady=10)

    def add_step_field(self):
        entry = tk.Entry(self.steps_frame, width=65)
        entry.pack(pady=2, fill="x")
        self.steps_entries.append(entry)

    def add_env_field(self):
        entry = tk.Entry(self.env_frame, width=65)
        entry.pack(pady=2, fill="x")
        self.env_entries.append(entry)

    def select_files(self):
        files = filedialog.askopenfilenames()
        if files:
            self.files_to_attach = list(files)
            self.lbl_attachment_status.config(text=f"✓ {len(self.files_to_attach)} files ready", fg="green")
            self.files_listbox.delete(0, tk.END)
            for f in self.files_to_attach:
                self.files_listbox.insert(tk.END, os.path.basename(f))

    def save_report(self):
        # Ścieżka projektu
        target_folder = os.path.join(BASE_PATH, self.active_window)
        os.makedirs(target_folder, exist_ok=True)
        
        report_id = self.get_next_id(target_folder)
        
        folder_name = f"{report_id}_{self.txt_title.get().replace(' ', '_')[:20]}"
        report_folder = os.path.join(target_folder, folder_name)
        os.makedirs(report_folder, exist_ok=True)
        
        with open(os.path.join(report_folder, "bug_report.txt"), "w", encoding="utf-8") as f:
            f.write(f"ID: {report_id}\nSUMMARY: {self.txt_title.get()}\n")
            f.write(f"SEVERITY: {self.combo_severity.get()}\nPLATFORM: {self.combo_platform.get()}\nBUILD: {self.txt_build.get()}\n\nENVIRONMENT:\n")
            for env in self.env_entries: f.write(f"- {env.get()}\n")
            f.write(f"\nEXPECTED: {self.txt_expected.get()}\nACTUAL: {self.txt_actual.get()}\n\nSTEPS:\n")
            for i, step in enumerate(self.steps_entries): f.write(f"{i+1}. {step.get()}\n")
        
        for f in self.files_to_attach:
            shutil.move(f, os.path.join(report_folder, os.path.basename(f)))
        
        if messagebox.askyesno("Success", f"Report {report_id} saved!\nOpen report folder?"):
            subprocess.Popen(["xdg-open", report_folder])
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    ProBugReporter(root)
    root.mainloop()
