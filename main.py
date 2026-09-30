import jinja2
from pathlib import Path
import itertools
import yaml

CONFIG_PATH = Path("configs/config1.yaml")
TEMPLATE_DIR = Path("templates")

def main():
    # 1. Load base configuration
    with CONFIG_PATH.open() as f:
        base_params = yaml.safe_load(f)

    template_filename = base_params.get("template_filename")

    # 2. Get the Jinja2 template environment and load the template
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        undefined=jinja2.StrictUndefined,  # Raises error if variable is missing
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = template_env.get_template(template_filename)

    # Formats floats into Fortran-compatible scientific notation or fixed width
    def relap_float(val, precision=5):
        return f"{val:.{precision}E}"

    template_env.filters["rfloat"] = relap_float

    # 3. Define parameter sweep (e.g., grid or sampled via SALib)
    sweep_params = {
        "k_fluid": [0.45, 0.50, 0.55, 0.60],
        "heat_flux": [1000.0, 1200.0, 1400.0],
    }

    # 4. Generate RELAP input files across runs
    output_base = Path("runs")
    for run_id, combination in enumerate(
        itertools.product(*sweep_params.values())
    ):
        current_params = base_params.copy()
        current_params.update(dict(zip(sweep_params.keys(), combination)))

        run_dir = output_base / f"run_{run_id:04d}"
        run_dir.mkdir(parents=True, exist_ok=True)

        rendered_content = template.render(current_params)
        (run_dir / "input.dat").write_text(rendered_content)

if __name__ == "__main__":
    main()