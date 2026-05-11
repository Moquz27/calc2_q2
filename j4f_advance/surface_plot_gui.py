"""Tkinter GUI for plotting z = f(x, y) over a calculus region D.

This file intentionally avoids top-level imports of numpy, matplotlib, and
sympy. The loading window checks those packages first so the GUI can explain
missing dependencies instead of crashing immediately.
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


GRID_SIZE = 80
REQUIRED_PACKAGES = ("numpy", "matplotlib", "sympy")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"

DEPENDENCIES = {}


def find_missing_packages() -> list[str]:
    """Check required packages without importing the plotting stack yet."""
    importlib_util = importlib.import_module("importlib.util")
    missing_packages = []
    for package_name in REQUIRED_PACKAGES:
        if importlib_util.find_spec(package_name) is None:
            missing_packages.append(package_name)
    return missing_packages


def load_dependencies() -> dict[str, object]:
    """Import plotting packages only after the dependency check succeeds."""
    return {
        "np": importlib.import_module("numpy"),
        "matplotlib": importlib.import_module("matplotlib"),
        "plt": importlib.import_module("matplotlib.pyplot"),
        "sp": importlib.import_module("sympy"),
        "sympy_parser": importlib.import_module("sympy.parsing.sympy_parser"),
    }


def install_missing_packages(packages: list[str]) -> subprocess.CompletedProcess[str]:
    """Install packages with the same Python interpreter that runs this file."""
    command = [sys.executable, "-m", "pip", "install", *packages]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def parse_math_expression(
    text: str,
    allowed_symbols: set[object],
    sp: object,
    x_symbol: object,
    y_symbol: object,
) -> object:
    """Parse user math input with SymPy and reject unexpected variables."""
    if not text:
        raise ValueError("math expression cannot be empty")

    parser = DEPENDENCIES["sympy_parser"]
    local_dict = {"x": x_symbol, "y": y_symbol}
    safe_global_dict = {
        "__builtins__": {},
        "Integer": sp.Integer,
        "Float": sp.Float,
        "Rational": sp.Rational,
        "Symbol": sp.Symbol,
        "Add": sp.Add,
        "Mul": sp.Mul,
        "Pow": sp.Pow,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "exp": sp.exp,
        "log": sp.log,
        "sqrt": sp.sqrt,
        "Abs": sp.Abs,
        "pi": sp.pi,
        "E": sp.E,
    }

    try:
        expression = parser.parse_expr(
            text,
            local_dict=local_dict,
            global_dict=safe_global_dict,
            transformations=parser.standard_transformations,
            evaluate=True,
        )
    except Exception as error:
        raise ValueError(f"could not parse expression '{text}'") from error

    unexpected_symbols = expression.free_symbols - allowed_symbols
    if unexpected_symbols:
        names = ", ".join(sorted(str(symbol) for symbol in unexpected_symbols))
        raise ValueError(f"unexpected variable(s): {names}")

    return expression


def read_float(text: str, label: str, np: object) -> float:
    """Convert one entry value to a finite float."""
    try:
        value = float(text)
    except ValueError as error:
        raise ValueError(f"{label} must be a number") from error

    if not np.isfinite(value):
        raise ValueError(f"{label} must be a finite number")

    return value


def build_surface_mesh(
    f_expr: object,
    g_expr: object,
    h_expr: object,
    c: float,
    d: float,
    x_symbol: object,
    y_symbol: object,
) -> tuple[object, object, object]:
    """Create X, Y, Z arrays using y in [c,d] and x = g(y) + t(h(y)-g(y))."""
    np = DEPENDENCIES["np"]
    sp = DEPENDENCIES["sp"]

    if c >= d:
        raise ValueError("Expected c < d so the y-interval has positive length.")

    f = sp.lambdify((x_symbol, y_symbol), f_expr, modules="numpy")
    g = sp.lambdify(y_symbol, g_expr, modules="numpy")
    h = sp.lambdify(y_symbol, h_expr, modules="numpy")

    y_values = np.linspace(c, d, GRID_SIZE)
    left_boundary = np.asarray(g(y_values), dtype=float)
    right_boundary = np.asarray(h(y_values), dtype=float)

    if left_boundary.shape == ():
        left_boundary = np.full_like(y_values, float(left_boundary))
    if right_boundary.shape == ():
        right_boundary = np.full_like(y_values, float(right_boundary))

    if not np.all(np.isfinite(left_boundary)) or not np.all(np.isfinite(right_boundary)):
        raise ValueError("Boundary functions must produce finite numbers on c <= y <= d.")

    if np.any(left_boundary > right_boundary):
        raise ValueError(
            "Expected g(y) <= h(y) on the interval [c,d]. "
            "If you entered the boundary functions in reverse order, "
            "swap g(y) and h(y)."
        )

    # The parameter t fills each horizontal slice from x = g(y) to x = h(y).
    t_values = np.linspace(0.0, 1.0, GRID_SIZE)
    y_grid = np.repeat(y_values[:, np.newaxis], GRID_SIZE, axis=1)
    x_grid = left_boundary[:, np.newaxis] + (
        right_boundary - left_boundary
    )[:, np.newaxis] * t_values[np.newaxis, :]

    z_grid = np.asarray(f(x_grid, y_grid), dtype=float)
    if z_grid.shape == ():
        z_grid = np.full_like(x_grid, float(z_grid))

    if not np.all(np.isfinite(z_grid)):
        raise ValueError("f(x, y) must produce finite z-values on the sampled region.")

    return x_grid, y_grid, z_grid


def save_plot_inputs(output_path: Path, values: dict[str, str]) -> None:
    """Save the input values beside the generated PNG."""
    lines = [
        f"f(x,y) = {values['f']}",
        f"g(y) = {values['g']}",
        f"h(y) = {values['h']}",
        f"c = {values['c']}",
        f"d = {values['d']}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_and_save_surface(values: dict[str, str]) -> tuple[Path, Path]:
    """Parse entries, draw the surface, and save PNG plus TXT outputs."""
    np = DEPENDENCIES["np"]
    matplotlib = DEPENDENCIES["matplotlib"]
    plt = DEPENDENCIES["plt"]
    sp = DEPENDENCIES["sp"]
    x_symbol, y_symbol = sp.symbols("x y")

    f_expr = parse_math_expression(values["f"], {x_symbol, y_symbol}, sp, x_symbol, y_symbol)
    g_expr = parse_math_expression(values["g"], {y_symbol}, sp, x_symbol, y_symbol)
    h_expr = parse_math_expression(values["h"], {y_symbol}, sp, x_symbol, y_symbol)
    c = read_float(values["c"], "c", np)
    d = read_float(values["d"], "d", np)

    x_grid, y_grid, z_grid = build_surface_mesh(
        f_expr, g_expr, h_expr, c, d, x_symbol, y_symbol
    )

    # Hide Matplotlib's default toolbar before creating the figure window.
    matplotlib.rcParams["toolbar"] = "None"

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    surface = ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")

    ax.plot(x_grid[:, 0], y_grid[:, 0], z_grid[:, 0], color="black", linewidth=2, label="x = g(y)")
    ax.plot(
        x_grid[:, -1],
        y_grid[:, -1],
        z_grid[:, -1],
        color="crimson",
        linewidth=2,
        label="x = h(y)",
    )

    ax.set_title(f"Surface z = {sp.sstr(f_expr)}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.legend()
    fig.colorbar(surface, ax=ax, shrink=0.65, pad=0.12, label="z value")
    plt.tight_layout()

    # Save before plt.show(); saving after show can produce blank files on some systems.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    png_path = OUTPUT_DIR / f"surface_{timestamp}.png"
    txt_path = OUTPUT_DIR / f"surface_{timestamp}.txt"
    fig.savefig(png_path, dpi=150)
    save_plot_inputs(txt_path, values)

    plt.show()
    return png_path, txt_path


def create_main_gui() -> None:
    """Open the main input window after packages are ready."""
    root = tk.Tk()
    root.title("Surface Plotter")
    root.geometry("520x330")
    root.resizable(False, False)

    main_frame = ttk.Frame(root, padding=18)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(main_frame, text="Surface Plotter", font=("Segoe UI", 16, "bold")).grid(
        row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
    )

    defaults = {
        "f": "x**2 + y**2",
        "g": "y",
        "h": "y + 2",
        "c": "0",
        "d": "2",
    }
    labels = {
        "f": "f(x,y)",
        "g": "g(y)",
        "h": "h(y)",
        "c": "c",
        "d": "d",
    }
    entries = {}

    for row_index, key in enumerate(("f", "g", "h", "c", "d"), start=1):
        ttk.Label(main_frame, text=labels[key]).grid(row=row_index, column=0, sticky="w", pady=5)
        entry = ttk.Entry(main_frame, width=42)
        entry.insert(0, defaults[key])
        entry.grid(row=row_index, column=1, sticky="ew", pady=5)
        entries[key] = entry

    def collect_values() -> dict[str, str]:
        return {key: entry.get().strip() for key, entry in entries.items()}

    def plot_surface_from_entries() -> None:
        try:
            png_path, txt_path = plot_and_save_surface(collect_values())
        except Exception as error:
            messagebox.showerror("Invalid input", str(error), parent=root)
            return

        messagebox.showinfo(
            "Plot saved",
            f"Saved chart:\n{png_path}\n\nSaved input file:\n{txt_path}",
            parent=root,
        )

    def clear_entries() -> None:
        for key, entry in entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, defaults[key])

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=7, column=0, columnspan=2, sticky="e", pady=(18, 0))

    ttk.Button(button_frame, text="Plot Surface", command=plot_surface_from_entries).pack(
        side="left", padx=(0, 8)
    )
    ttk.Button(button_frame, text="Clear", command=clear_entries).pack(side="left", padx=(0, 8))
    ttk.Button(button_frame, text="Exit", command=root.destroy).pack(side="left")

    main_frame.columnconfigure(1, weight=1)
    root.mainloop()


def start_loading_flow() -> None:
    """Show loading UI, check packages, and install only after user approval."""
    loading_root = tk.Tk()
    loading_root.title("Surface Plotter")
    loading_root.geometry("360x150")
    loading_root.resizable(False, False)

    frame = ttk.Frame(loading_root, padding=18)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Surface Plotter", font=("Segoe UI", 14, "bold")).pack(anchor="w")
    status_text = tk.StringVar(value="Checking required packages...")
    ttk.Label(frame, textvariable=status_text).pack(anchor="w", pady=(12, 8))

    progress_bar = ttk.Progressbar(frame, mode="determinate", maximum=100, value=10)
    progress_bar.pack(fill="x")

    def close_loading_and_open_main() -> None:
        loading_root.destroy()
        create_main_gui()

    def fail_and_exit(message: str) -> None:
        progress_bar.stop()
        messagebox.showerror("Surface Plotter", message, parent=loading_root)
        loading_root.destroy()

    def finish_if_ready() -> None:
        global DEPENDENCIES
        try:
            DEPENDENCIES = load_dependencies()
        except Exception as error:
            fail_and_exit(f"Required packages are installed but could not be imported:\n{error}")
            return

        status_text.set("Ready.")
        progress_bar.configure(mode="determinate", value=100)
        loading_root.after(350, close_loading_and_open_main)

    def install_worker(packages: list[str]) -> None:
        result = install_missing_packages(packages)

        def finish_install() -> None:
            if result.returncode != 0:
                fail_and_exit(
                    "Package installation failed.\n\n"
                    f"Command: {sys.executable} -m pip install {' '.join(packages)}\n\n"
                    f"{result.stderr.strip() or result.stdout.strip()}"
                )
                return

            messagebox.showinfo(
                "Surface Plotter",
                "Packages installed successfully. The application will now restart.",
                parent=loading_root,
            )
            os.execv(sys.executable, [sys.executable] + sys.argv)

        loading_root.after(0, finish_install)

    def begin_check() -> None:
        missing_packages = find_missing_packages()
        progress_bar.configure(value=40)

        if not missing_packages:
            finish_if_ready()
            return

        package_list = ", ".join(missing_packages)
        should_install = messagebox.askyesno(
            "Missing packages",
            f"Missing packages: {package_list}\n\nDo you want to install them now?",
            parent=loading_root,
        )

        if not should_install:
            fail_and_exit(
                "The program cannot run without these packages:\n" + package_list
            )
            return

        # pip install is blocking, so it runs in a worker thread to keep Tk responsive.
        status_text.set("Installing missing packages...")
        progress_bar.configure(mode="indeterminate")
        progress_bar.start(12)
        worker = threading.Thread(target=install_worker, args=(missing_packages,), daemon=True)
        worker.start()

    loading_root.after(250, begin_check)
    loading_root.mainloop()


def main() -> int:
    start_loading_flow()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
