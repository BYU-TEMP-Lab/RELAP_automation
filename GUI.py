from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import yaml


class FileSelectionDialog:
    """
    A standalone tkinter dialog for selecting configuration and template files.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("File Selection")
        self.root.resizable(False, False)

        self.config_dir = Path("configs")
        self.template_dir = Path("templates")

        self.selected_config = None
        self.config_data = None
        self.user_note = None

        # Ensure directories exist to prevent runtime FileNotFoundError
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        self._build_ui()
        self._populate_dropdowns()

    def _build_ui(self):
        # Configuration File Selection
        ttk.Label(self.root, text="Configuration File:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.config_var = tk.StringVar()
        self.config_cb = ttk.Combobox(
            self.root, textvariable=self.config_var, state="readonly", width=40
        )
        self.config_cb.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.config_cb.bind("<<ComboboxSelected>>", self._on_select)

        # Scrollable YAML Content Display
        self.yaml_text = ScrolledText(
            self.root, width=50, height=12, wrap=tk.WORD, state="disabled"
        )
        self.yaml_text.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew"
        )

        # User notes text input
        ttk.Label(self.root, text="Note:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.note_var = tk.StringVar()
        note = ttk.Entry(self.root, width=50, textvariable=self.note_var)
        note.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Action Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Confirm", command=self._on_confirm).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self.root.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _populate_dropdowns(self):
        config_files = [
            f.name
            for f in self.config_dir.iterdir()
            if f.is_file() and f.suffix in {".yaml", ".yml"}
        ]
        self.config_cb["values"] = config_files

        if config_files:
            self.config_cb.current(0)
            # self._update_display(config_files[0])

    def _set_text_content(self, text: str):
        """Helper to safely write to a disabled/read-only ScrolledText widget."""
        self.yaml_text.config(state="normal")
        self.yaml_text.delete("1.0", tk.END)
        self.yaml_text.insert(tk.END, text)
        self.yaml_text.config(state="disabled")

    def _update_display(self, selected_config_name: str):
        config_path = self.config_dir / selected_config_name

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}

            total_width = 50
            display_string = "".join(
                f"{f'=={key}'.ljust(total_width, '=')}\n{value}\n\n"
                for key, value in config_data.items()
            )
            self._set_text_content(display_string)

            try:
                self.template_filename = Path(config_data.get("template_filename"))
                self.excel_filepath = Path(config_data.get("excel_filepath"))
                self.sheet_name = config_data.get("sheet_name")
            except Exception as e:
                self._set_text_content(f"Error converting configuration values to Path objects:\n{e}")
                return None

            if not all([self.template_filename, self.excel_filepath, self.sheet_name]):
                err_string = (
                    "Error: Expected YAML keys: 'template_filename', 'excel_filepath', 'sheet_name', but received:\n")
                for key in config_data:
                    err_string += f"  - {key}\n"
                self._set_text_content(err_string)

                return None           

            return config_data  # Return the loaded configuration data for further use

        except Exception as e:
            self._set_text_content(f"Error loading configuration:\n{e}")
            return None

    def _on_select(self, event):
        selected_config_name = self.config_var.get()
        self.selected_config = Path(selected_config_name)
        
        if selected_config_name:
            self.config_data = self._update_display(selected_config_name)
        else:
            self._set_text_content("")

    def _on_confirm(self):
        if not self.config_var.get() or not self.selected_config:
            messagebox.showerror(
                "Selection Error",
                "A configuration file must be loaded before confirming. Please select a configuration file.",
            )
            return

        self.user_note = self.note_var.get()  # Capture user notes

        self.root.destroy()


def get_target_files() -> tuple:
    """
    Initializes the tkinter event loop and returns the selected Path objects.
    """
    root = tk.Tk()
    root.eval("tk::PlaceWindow . center")

    dialog = FileSelectionDialog(root)
    root.mainloop()

    # Allow pending Tk events to drain completely
    try:
        root.update()
    except tk.TclError:
        # print(tk.TclError)
        pass

    return dialog.selected_config, dialog.template_filename, dialog.excel_filepath, dialog.sheet_name, dialog.user_note