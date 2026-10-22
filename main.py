import sys
import time

import jinja2
from pathlib import Path
import pandas as pd
from datetime import datetime

from GUI import get_target_files

PROGRAM_DIR = Path(__file__).parent
TEMPLATE_DIR = PROGRAM_DIR / Path("templates") # jinja template directory
CONFIG_DIR = PROGRAM_DIR / Path("configs") # configuration files directory
OUTPUT_DIR = PROGRAM_DIR / Path("runs") # output directory for generated RELAP input files

def parse_parameters(excel_file: str, sheet_name: int | str = 0) -> dict:
    """Reads a three-column sheet (Code, Parameter, Value) and nests the parameters under their respective codes.
    Args:
        excel_file (str): Path to the Excel file.
        sheet_name (int | str, optional): Sheet name or index in the Excel file. Defaults to 0.
    Returns:
        dict: Nested dictionary with codes as keys and their parameters as sub-dictionaries.
    """

    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    param_dict = {}
    for code, param, value in zip(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2]):
        code = str("c"+str(code))  # Prefix with 'c' to ensure it's a valid key
        value = str(value)
        try:
            value = float(value)
            value = int(value) if value.is_integer() else value
        except ValueError:
            pass  # Keep value as string if it cannot be converted to float
        if code not in param_dict:
            param_dict[code] = {}
        param_dict[code][param] = value
        
    return param_dict

def main(CONFIG_PATH, TEMPLATE_PATH, EXCEL_PATH, sheet_name, note):
    """Main function to generate RELAP input file based on provided configuration, template, and Excel data.
    Args:
        CONFIG_PATH (Path): Path to the selected configuration file.
        TEMPLATE_PATH (Path): Path to the selected Jinja template file.
        EXCEL_PATH (Path): Path to the selected Excel file containing parameters.
        sheet_name (int | str): Sheet name or index in the Excel file to read parameters from.
        note (str): User-provided note for the run.
    
    Returns:
        None
    """

    # Print the selected paths and sheet name for verification
    print("=============== RUN CONFIGURATION ===============")
    print(f"Selected configuration file: {CONFIG_PATH}")
    print(f"Selected template file: {TEMPLATE_PATH}")
    print(f"Selected Excel file: {EXCEL_PATH}")
    print(f"Selected sheet name: {sheet_name}")
    print(f"User note: {note}")
    print("=================================================")

    # Create a metadata dictionary to store the paths and sheet name for reference
    current_time = datetime.now()
    meta_data = {
        "config_file": str(CONFIG_PATH),
        "template_file": str(TEMPLATE_PATH),
        "excel_file": str(EXCEL_PATH),
        "sheet_name": sheet_name,
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": note
    }

    # Set up the Jinja2 environment and load the template
    template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
            undefined=jinja2.StrictUndefined,  # Raises error if variable is missing
            trim_blocks=True,
            lstrip_blocks=True,
        )
    template = template_env.get_template(TEMPLATE_PATH.name)

    # Parse parameters from the Excel file and render the template
    param_dict = parse_parameters(EXCEL_PATH, sheet_name)
    param_dict["meta_data"] = meta_data  # Add metadata to the parameter dictionary
    print(param_dict)
    rendered_content = template.render(param_dict)

    # Generate a unique output filename based on the note or template name and current timestamp
    if note:
        sanitized_note = "".join(c if c.isalnum() or c in ('_') else '_' for c in note).strip()
        output_filename = f"{sanitized_note}_{current_time.strftime("%Y-%m-%d_%H_%M_%S")}.i"
    else:
        output_filename = f"{TEMPLATE_PATH.stem}_{current_time.strftime("%Y-%m-%d_%H_%M_%S")}.i"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH = OUTPUT_DIR / output_filename
    OUTPUT_PATH.write_text(rendered_content)


if __name__ == "__main__":
    # get file paths and sheet name from GUI
    config_file, template_file, excel_file, sheet_name, note = get_target_files()
    CONFIG_PATH = CONFIG_DIR / config_file if config_file else None
    TEMPLATE_PATH = TEMPLATE_DIR / template_file if template_file else None
    EXCEL_PATH = excel_file if excel_file else None

    # Check if all required paths and sheet name are provided
    if not all([CONFIG_PATH, TEMPLATE_PATH, EXCEL_PATH, sheet_name]):
        print("Error: GUI did not provide all required file paths and sheet name.")
        sys.exit(1)

    # Run the main function with the provided paths and sheet name
    main(CONFIG_PATH, TEMPLATE_PATH, EXCEL_PATH, sheet_name, note)

    # Flush the output to ensure all print statements are displayed before the program exits
    sys.stdout.flush()