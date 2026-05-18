"""Draw z = f(x, y) over the region between x = g(y) and x = h(y).

Example input:
    f(x, y): x**2 + y**2
    g(y): y
    h(y): y + 2
    c: 0
    d: 2
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations


GRID_SIZE = 80
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

x_symbol, y_symbol = sp.symbols("x y")

SAFE_GLOBAL_DICT = {
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


def parse_math_expression(text: str, allowed_symbols: set[sp.Symbol]) -> sp.Expr:
    """Parse a user expression and reject variables outside allowed_symbols."""
    if not text:
        raise ValueError("math expression cannot be empty")

    local_dict = {"x": x_symbol, "y": y_symbol}

    try:
        expression = parse_expr(
            text,
            local_dict=local_dict,
            global_dict=SAFE_GLOBAL_DICT,
            transformations=standard_transformations,
            evaluate=True,
        )
    except Exception as error:
        raise ValueError(f"could not parse expression '{text}'") from error

    unexpected_symbols = expression.free_symbols - allowed_symbols
    if unexpected_symbols:
        names = ", ".join(sorted(str(symbol) for symbol in unexpected_symbols))
        raise ValueError(f"unexpected variable(s): {names}")

    return expression


def build_surface_mesh(
    f_expr: sp.Expr,
    g_expr: sp.Expr,
    h_expr: sp.Expr,
    c: float,
    d: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create X, Y, and Z arrays for the surface over the region D."""
    if c >= d:
        raise ValueError("Expected c < d so the y-interval has positive length.")

    f = sp.lambdify((x_symbol, y_symbol), f_expr, modules="numpy")
    g = sp.lambdify(y_symbol, g_expr, modules="numpy")
    h = sp.lambdify(y_symbol, h_expr, modules="numpy")

    # First sample y from c to d. Each row of the mesh belongs to one y-value.
    y_values = np.linspace(c, d, GRID_SIZE)
    g_values = np.asarray(g(y_values), dtype=float)
    h_values = np.asarray(h(y_values), dtype=float)

    if g_values.shape == ():
        g_values = np.full_like(y_values, float(g_values))
    if h_values.shape == ():
        h_values = np.full_like(y_values, float(h_values))

    if not np.all(np.isfinite(g_values)) or not np.all(np.isfinite(h_values)):
        raise ValueError("Boundary functions must produce finite numbers on c <= y <= d.")

    left_boundary = np.minimum(g_values, h_values)
    right_boundary = np.maximum(g_values, h_values)

    # For each fixed y, x moves from the smaller boundary value to the larger
    # one. This also handles cases where g(y) and h(y) switch left/right sides.
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


def save_input_record(output_path: Path, values: dict[str, str]) -> None:
    """Save the user's input values beside the generated chart."""
    lines = [
        f"f(x,y) = {values['f']}",
        f"g(y) = {values['g']}",
        f"h(y) = {values['h']}",
        f"c = {values['c']}",
        f"d = {values['d']}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_surface(
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    z_grid: np.ndarray,
    f_expr: sp.Expr,
    input_values: dict[str, str],
) -> tuple[Path, Path]:
    """Plot the computed surface and autosave the chart before showing it."""
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    surface = ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")

    # The first and last columns are the left and right boundary curves.
    ax.plot(
        x_grid[:, 0],
        y_grid[:, 0],
        z_grid[:, 0],
        color="black",
        linewidth=2,
        label="left boundary",
    )
    ax.plot(
        x_grid[:, -1],
        y_grid[:, -1],
        z_grid[:, -1],
        color="crimson",
        linewidth=2,
        label="right boundary",
    )

    ax.set_title(f"Surface z = {sp.sstr(f_expr)}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.legend()
    fig.colorbar(surface, ax=ax, shrink=0.65, pad=0.12, label="z value")

    plt.tight_layout()

    # Save before plt.show(); saving after show can produce blank files.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    png_path = OUTPUT_DIR / f"surface_{timestamp}.png"
    txt_path = OUTPUT_DIR / f"surface_{timestamp}.txt"
    fig.savefig(png_path, dpi=150)
    save_input_record(txt_path, input_values)

    print(f"Saved chart to: {png_path}")
    print(f"Saved input record to: {txt_path}")

    plt.show()
    return png_path, txt_path


def main() -> int:
    """Read input, build the mesh, save the image, and show the surface plot."""
    print("Surface plotter for z = f(x, y)")
    print("Region: c <= y <= d and x lies between g(y) and h(y)")
    print("Use Python syntax: x**2, not x^2")
    print("Example: f = x**2 + y**2, g = y, h = y + 2, c = 0, d = 2")
    print()

    try:
        input_values = {
            "f": input("Enter f(x, y): ").strip(),
            "g": input("Enter g(y): ").strip(),
            "h": input("Enter h(y): ").strip(),
            "c": input("Enter c: ").strip(),
            "d": input("Enter d: ").strip(),
        }

        f_expr = parse_math_expression(input_values["f"], {x_symbol, y_symbol})
        g_expr = parse_math_expression(input_values["g"], {y_symbol})
        h_expr = parse_math_expression(input_values["h"], {y_symbol})
        c = read_float_from_text(input_values["c"], "c")
        d = read_float_from_text(input_values["d"], "d")

        x_grid, y_grid, z_grid = build_surface_mesh(f_expr, g_expr, h_expr, c, d)
        plot_surface(x_grid, y_grid, z_grid, f_expr, input_values)
    except (ValueError, TypeError, SyntaxError, sp.SympifyError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 1

    return 0


def read_float_from_text(text: str, name: str) -> float:
    """Convert stored input text to a finite float with a clear field name."""
    try:
        expression = parse_math_expression(text, set())
        value = float(expression.evalf())
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a real number or numeric expression") from error

    if not np.isfinite(value):
        raise ValueError(f"{name} must be a finite number")

    return value


if __name__ == "__main__":
    raise SystemExit(main())
