"""Draw z = f(x, y) over the region between x = g(y) and x = h(y), c ≤ y ≤ d

=========
Author: Moquz27 - Phan Gia Kiet - 2551131
For more project like this: https://github.com/Moquz27/calc2_q2
=========
"""



from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations


GRID_SIZE = 450
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

x_symbol, y_symbol = sp.symbols("x y")

SAFE_GLOBAL_DICT = {
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


### 	Parse biểu thức toán học 
def parse_math_expression(text: str, allowed_symbols: set[sp.Symbol]) -> sp.Expr:
    
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

### Tạo mesh cho miền giữa g(Y) và h(Y))
def build_surface_mesh(
    f_expr: sp.Expr,
    g_expr: sp.Expr,
    h_expr: sp.Expr,
    c: float,
    d: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
     
    if c >= d:
        raise ValueError("Expected c < d so the y-interval has positive length.")
    # khai báo hàm funtion
    f = sp.lambdify((x_symbol, y_symbol), f_expr, modules="numpy")
    g = sp.lambdify(y_symbol, g_expr, modules="numpy")
    h = sp.lambdify(y_symbol, h_expr, modules="numpy")

    # First sample y from c to d. Each row of the mesh belongs to one y-value.
    y_values = np.linspace(c, d, GRID_SIZE)
    g_values = np.asarray(g(y_values), dtype=float)
    h_values = np.asarray(h(y_values), dtype=float)
    #kiểm tra input của g và h là hằng số hay hàm số
    if g_values.shape == ():
        g_values = np.full_like(y_values, float(g_values))
    if h_values.shape == ():
        h_values = np.full_like(y_values, float(h_values))
    # kiểm tra hàm có chứa số vô cực không
    if not np.all(np.isfinite(g_values)) or not np.all(np.isfinite(h_values)):
        raise ValueError("Boundary functions must produce finite numbers on c <= y <= d.")
    #khai báo biến 2 biên
    left_boundary = np.minimum(g_values, h_values)
    right_boundary = np.maximum(g_values, h_values)

     
     #tạo mesh x y
    t_values = np.linspace(0.0, 1.0, GRID_SIZE)
    y_grid = np.repeat(y_values[:, np.newaxis], GRID_SIZE, axis=1)
    x_grid = left_boundary[:, np.newaxis] + (
        right_boundary - left_boundary
    )[:, np.newaxis] * t_values[np.newaxis, :]
    #tạo z
    z_grid = np.asarray(f(x_grid, y_grid), dtype=float)
    if z_grid.shape == ():
        z_grid = np.full_like(x_grid, float(z_grid))
    # validate
    if not np.all(np.isfinite(z_grid)):
        raise ValueError("f(x, y) must produce finite z-values on the sampled region.")

    return x_grid, y_grid, z_grid, y_values, g_values, h_values

### lưu input 
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

### vẽ đồ thị 3d
def plot_surface(
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    z_grid: np.ndarray,
    y_values: np.ndarray,
    g_values: np.ndarray,
    h_values: np.ndarray,
    f_expr: sp.Expr,
    input_values: dict[str, str],
) -> tuple[Path, Path]:
    # vẽ char và lưu chart
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    #vẽ chart
    surface = ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")
    # tính z value của 2 đừng biên nhằm vẽ 2 đường biên ở dạng 3d
    f = sp.lambdify((x_symbol, y_symbol), f_expr, modules="numpy")
    g_z_values = np.asarray(f(g_values, y_values), dtype=float)
    h_z_values = np.asarray(f(h_values, y_values), dtype=float)
    # valtdate toàn bộ đều là điểm hữu hạn
    if not np.all(np.isfinite(g_z_values)) or not np.all(np.isfinite(h_z_values)):
        raise ValueError("Boundary curves must produce finite z-values.")

    #vẽ 2 đường biên
    ax.plot(
        g_values,
        y_values,
        g_z_values,
        color="black",
        linewidth=2,
        label="x = g(y)",
    )
    ax.plot(
        h_values,
        y_values,
        h_z_values,
        color="crimson",
        linewidth=2,
        label="x = h(y)",
    )
    # thêm metadata cho chart
    ax.set_title(f"Surface z = {sp.sstr(f_expr)}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.legend()
    fig.colorbar(surface, ax=ax, shrink=0.65, pad=0.12, label="z value")

    plt.tight_layout()

    
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

### pipeline
def main() -> int:
     
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

        x_grid, y_grid, z_grid, y_values, g_values, h_values = build_surface_mesh(
            f_expr, g_expr, h_expr, c, d
        )
        plot_surface(
            x_grid,
            y_grid,
            z_grid,
            y_values,
            g_values,
            h_values,
            f_expr,
            input_values,
        )
    except (ValueError, TypeError, SyntaxError, sp.SympifyError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
   

    return 0

### chuyển cd sang số thực
def read_float_from_text(text: str, name: str) -> float:
    
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
