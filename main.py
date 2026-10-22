import sys
import time

import jinja2
from pathlib import Path
import pandas as pd

from GUI import get_target_files

PROGRAM_DIR = Path(__file__).parent
TEMPLATE_DIR = PROGRAM_DIR / Path("templates") # jinja template directory
CONFIG_DIR = PROGRAM_DIR / Path("configs") # configuration files directory
OUTPUT_DIR = PROGRAM_DIR / Path("runs") # output directory for generated RELAP input files

def parse_parameters(excel_file: str, sheet_name: int | str = 0) -> dict:
    """Reads a three-column sheet (Code, Parameter, Value) and nests the parameters under their respective codes."""
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

def main(CONFIG_PATH, TEMPLATE_PATH, EXCEL_PATH, sheet_name):

    print("=============== RUN CONFIGURATION ===============")
    print(f"Selected configuration file: {CONFIG_PATH}")
    print(f"Selected template file: {TEMPLATE_PATH}")
    print(f"Selected Excel file: {EXCEL_PATH}")
    print(f"Selected sheet name: {sheet_name}")
    print("=================================================")

    meta_data = {
        "config_file": str(CONFIG_PATH),
        "template_file": str(TEMPLATE_PATH),
        "excel_file": str(EXCEL_PATH),
        "sheet_name": sheet_name,
    }

    template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
            undefined=jinja2.StrictUndefined,  # Raises error if variable is missing
            trim_blocks=True,
            lstrip_blocks=True,
        )
    template = template_env.get_template(TEMPLATE_PATH.name)

    param_dict = parse_parameters(EXCEL_PATH, sheet_name)
    print(param_dict)
    rendered_content = template.render(param_dict)

    output_filename = f"{TEMPLATE_PATH.stem}_{time.time()}.i"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH = OUTPUT_DIR / output_filename
    OUTPUT_PATH.write_text(rendered_content)

if __name__ == "__main__":
    config_file, template_file, excel_file, sheet_name = get_target_files()
    CONFIG_PATH = CONFIG_DIR / config_file if config_file else None
    TEMPLATE_PATH = TEMPLATE_DIR / template_file if template_file else None
    EXCEL_PATH = excel_file if excel_file else None

    if not all([CONFIG_PATH, TEMPLATE_PATH, EXCEL_PATH, sheet_name]):
        print("Error: GUI did not provide all required file paths and sheet name.")
        sys.exit(1)

    main(CONFIG_PATH, TEMPLATE_PATH, EXCEL_PATH, sheet_name)

    sys.stdout.flush()