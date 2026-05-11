# Surface Plotter – Design and Algorithm Report

## 1. Introduction

The goal of this project is to build a simple Python program that visualizes a
surface in three dimensions. The surface has the explicit form:

```text
z = f(x,y)
```

The surface is not plotted over an arbitrary rectangle. Instead, it is plotted
over the projection region:

```text
D = {(x,y) | c <= y <= d and g(y) <= x <= h(y)}
```

The assignment requires the user to enter:

- `f(x,y)`: the surface height function,
- `g(y)`: the left boundary curve for `x`,
- `h(y)`: the right boundary curve for `x`,
- `c`: the lower bound for `y`,
- `d`: the upper bound for `y`.

The program in `surface_plot.py` reads these inputs from the terminal, builds a
numerical grid over the region `D`, computes `z = f(x,y)`, plots the surface
with Matplotlib, and automatically saves the result.

## 2. Problem Analysis

The projection region `D` may not be a rectangle in the `xOy` plane. For each
fixed value of `y`, the allowed interval for `x` is:

```text
g(y) <= x <= h(y)
```

Because both boundaries depend on `y`, the left and right edges of the region
can curve. If we directly create a rectangular mesh using global `x` and `y`
ranges, many generated points may lie outside `D`. That approach would require
extra filtering or masking.

The technical difficulty is that the valid `x` interval changes as `y` changes.
This naturally leads to transforming a simple rectangular parameter domain into
the curved region `D`. The code uses a parameter `t` to move from `g(y)` to
`h(y)` for each sampled value of `y`.

## 3. Design Goals

The program is designed to be clear and appropriate for an undergraduate
multivariable calculus assignment. The main design goals are:

- keep the code simple and readable,
- use safe mathematical expression parsing,
- avoid Python `eval()`,
- use NumPy for numerical arrays and vectorized computation,
- use SymPy for symbolic parsing and `lambdify()`,
- use Matplotlib for 3D visualization,
- keep the algorithm general enough for many choices of `g(y)` and `h(y)`,
- avoid unnecessary classes, frameworks, or complex architecture.

The implementation is intentionally procedural. Each function has a focused
role: parse expressions, validate and build the mesh, save input records, and
plot the result.

## 4. Possible Approaches

### 4.1 Direct Rectangular Grid

One possible approach is to choose a global range for `x`, choose a range for
`y`, and create a rectangular grid directly in the `xOy` plane.

The advantage is that this method is easy to understand and easy to code.
However, it is not well matched to the given region. Since the valid `x` range
depends on `y`, a direct rectangular grid may include many points outside `D`.
It may also be difficult to choose correct global `x` bounds without first
analyzing `g(y)` and `h(y)`.

### 4.2 Rectangular Grid with Masking

Another approach is to create a large rectangular grid and then mask all points
that do not satisfy:

```text
g(y) <= x <= h(y)
```

This method is more flexible than a plain rectangular grid. However, it wastes
computation on points that are later discarded. It can also make surface
plotting less clean because masked regions may create gaps or irregular edges.
For a beginner-friendly calculus visualization, this adds complexity that is
not necessary.

### 4.3 Parameterization-Based Mesh (Chosen Approach)

The chosen approach is to parameterize the valid `x` values using:

```text
x = g(y) + t(h(y)-g(y))
```

where:

```text
c <= y <= d
0 <= t <= 1
```

This approach generates only points that belong to the region `D`, assuming
`g(y) <= h(y)`. It also works naturally with NumPy broadcasting and produces a
clean rectangular numerical mesh in the parameter variables `(y,t)`.

This method is chosen because it directly follows the mathematical definition
of the region and remains simple to implement.

## 5. Mathematical Foundation

### 5.1 Projection Region

The projection region is:

```text
D = {(x,y) | c <= y <= d and g(y) <= x <= h(y)}
```

This means that `y` moves from `c` to `d`. For each fixed `y`, the value of `x`
moves from the left boundary `g(y)` to the right boundary `h(y)`.

### 5.2 Parameterization Formula

The program introduces a parameter `t`:

```text
0 <= t <= 1
```

Then it defines:

```text
x = g(y) + t(h(y)-g(y))
```

The parameter domain is the rectangle:

```text
(y,t) in [c,d] x [0,1]
```

### 5.3 Why This Works

When `t = 0`:

```text
x = g(y)
```

When `t = 1`:

```text
x = h(y)
```

When `0 < t < 1`, the value of `x` lies between `g(y)` and `h(y)`. Therefore,
if `g(y) <= h(y)`, every generated point satisfies:

```text
g(y) <= x <= h(y)
```

The rectangular parameter domain `[c,d] x [0,1]` is mapped into the curved
projection region `D`.

## 6. Numerical Algorithm

### Step 1 — Read User Input

The program reads five strings from the terminal:

- `f(x, y)`,
- `g(y)`,
- `h(y)`,
- `c`,
- `d`.

The values are stored in the `input_values` dictionary so they can also be
saved later in the output `.txt` file.

### Step 2 — Parse Mathematical Expressions

The strings for `f`, `g`, and `h` are parsed using SymPy `parse_expr()`. The
program checks that the expressions only use allowed variables. Then, inside
`build_surface_mesh()`, the symbolic expressions are converted to numerical
functions using `sp.lambdify()`.

### Step 3 — Generate Numerical Samples

The code uses:

```python
GRID_SIZE = 80
```

It samples `y` with:

```python
np.linspace(c, d, GRID_SIZE)
```

and samples `t` with:

```python
np.linspace(0.0, 1.0, GRID_SIZE)
```

### Step 4 — Construct the Mesh

The boundary functions are evaluated on the sampled `y` values. The program
stores them as `left_boundary` and `right_boundary`.

Then it constructs:

```python
y_grid = np.repeat(y_values[:, np.newaxis], GRID_SIZE, axis=1)
x_grid = left_boundary[:, np.newaxis] + (
    right_boundary - left_boundary
)[:, np.newaxis] * t_values[np.newaxis, :]
```

This uses NumPy broadcasting. The term `left_boundary[:, np.newaxis]` makes the
left boundary a column. The term `t_values[np.newaxis, :]` makes the parameter
values a row. Multiplying them creates a full two-dimensional grid.

### Step 5 — Evaluate the Surface

After the mesh is built, the program evaluates:

```text
Z = f(X,Y)
```

In code, this is:

```python
z_grid = np.asarray(f(x_grid, y_grid), dtype=float)
```

Because the function was created with `lambdify(..., modules="numpy")`, it can
evaluate the entire NumPy grid at once.

### Step 6 — Visualize the Surface

The function `plot_surface()` creates a Matplotlib 3D figure and draws the
surface using:

```python
ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")
```

The plot also includes labels, a title, a colorbar, and two boundary curves.

## 7. Expression Parsing and Safety

The program does not use Python `eval()`. This is important because `eval()`
would execute arbitrary Python code from user input, which is unsafe.

Instead, the code uses:

```python
parse_expr(...)
```

with a controlled `local_dict`:

```python
local_dict = {"x": x_symbol, "y": y_symbol}
```

It also defines `SAFE_GLOBAL_DICT`, which limits the available symbolic
constructs and mathematical functions. The supported functions and constants
include:

```text
sin, cos, tan, exp, log, sqrt, Abs, pi, E
```

After parsing, the code checks:

```python
unexpected_symbols = expression.free_symbols - allowed_symbols
```

This ensures that:

- `f(x,y)` may only use `x` and `y`,
- `g(y)` may only use `y`,
- `h(y)` may only use `y`.

If the expression contains unexpected variables, the program raises a
`ValueError`.

## 8. Numerical Grid Construction

`GRID_SIZE` controls the number of samples in each parameter direction. In the
current code:

```python
GRID_SIZE = 80
```

If `GRID_SIZE = n`, then the program creates `n` samples for `y` and `n`
samples for `t`. The resulting surface mesh contains approximately `n²`
points.

The main arrays are:

- `x_grid`: all sampled `x` coordinates in the region,
- `y_grid`: all sampled `y` coordinates,
- `z_grid`: computed surface heights.

The code also handles the case where `g(y)` or `h(y)` is a constant expression.
If a boundary evaluates to a scalar, it is expanded with `np.full_like()` so it
matches the shape of `y_values`.

The program checks that boundary arrays and `z_grid` contain only finite
values. This prevents invalid plots caused by `nan` or `inf`.

## 9. Input Validation

The program validates input in several places:

- `c` and `d` must be valid finite numbers.
- `c < d`.
- `f` may only use `x` and `y`.
- `g` and `h` may only use `y`.
- `g(y) <= h(y)` on the sampled `y` values.
- boundary values must be finite.
- `Z` values must be finite.

If validation fails, the program stops plotting and prints a clear error
message to the terminal.

The check for `g(y) <= h(y)` is numerical. It is performed on the sampled grid,
not as a symbolic proof over the entire interval `[c,d]`.

## 10. Surface Visualization

The program uses Matplotlib 3D axes:

```python
ax = fig.add_subplot(111, projection="3d")
```

The surface is drawn with:

```python
ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")
```

The plot includes:

- a title,
- labels for the `x`, `y`, and `z` axes,
- a colorbar for the `z` value,
- a legend.

The code also plots two boundary curves:

- `x = g(y)`,
- `x = h(y)`.

These curves are taken from the first and last columns of the mesh. They help
the viewer see the boundary of the projection region on the 3D surface.

## 11. Automatic Output Saving

The current `surface_plot.py` includes autosave behavior.

Before showing the plot, the program creates the output folder:

```python
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

where:

```python
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
```

It saves the chart as a timestamped `.png` file:

```text
surface_YYYYMMDD_HHMMSS.png
```

It also saves the input values as a matching `.txt` file:

```text
surface_YYYYMMDD_HHMMSS.txt
```

The figure is saved with:

```python
fig.savefig(png_path, dpi=150)
```

This happens before:

```python
plt.show()
```

Saving before `plt.show()` is safer because some Matplotlib backends may clear
or alter the figure after the display window is closed.

## 12. Complexity Discussion

Let:

```text
n = GRID_SIZE
```

The mesh has about:

```text
n²
```

points. Therefore, the time complexity is approximately:

```text
O(n²)
```

The memory complexity is also approximately:

```text
O(n²)
```

because the program stores `x_grid`, `y_grid`, and `z_grid`.

A larger `GRID_SIZE` creates a smoother surface but requires more time and
memory. A smaller `GRID_SIZE` runs faster but may make the surface look rougher.

## 13. Limitations

The program only supports explicit surfaces:

```text
z = f(x,y)
```

It does not directly support implicit surfaces such as:

```text
x² + y² + z² = 1
```

Some functions may be undefined on part of the region `D`. For example, a
square root may receive a negative value at some sampled points. In that case,
the program can raise an invalid input error because the resulting values are
not finite.

Floating-point precision may also create small visual artifacts near boundaries
or singular points.

The validation is numerical, not a symbolic proof. It checks sampled points
rather than proving every condition for all real values in `[c,d]`.

If the user wants to plot a full sphere, it must be split into upper and lower
halves because a full sphere is not a single-valued function `z = f(x,y)`.

## 14. Example Walkthrough

Consider the example:

```text
f(x,y) = x**2 + y**2
g(y) = y
h(y) = y + 2
c = 0
d = 2
```

1. The program samples `y` from `0` to `2`.
2. It samples `t` from `0` to `1`.
3. It computes:

```text
x = y + t((y + 2) - y)
```

This simplifies to:

```text
x = y + 2t
```

4. When `t = 0`, `x = y`.
5. When `t = 1`, `x = y + 2`.
6. When `0 < t < 1`, `x` lies between `y` and `y + 2`.
7. The program computes:

```text
z = x² + y²
```

8. Finally, Matplotlib draws the surface over the generated region and the
program saves both the chart and input record.

## 15. Conclusion

The program solves the assignment by using a parameterization-based mesh. This
matches the mathematical definition of the region:

```text
D = {(x,y) | c <= y <= d and g(y) <= x <= h(y)}
```

Compared with direct rectangular sampling, the chosen method avoids generating
many invalid points outside the region. It also keeps the implementation simple
and suitable for vectorized NumPy computation.

Overall, the solution balances mathematical correctness, numerical simplicity,
visualization quality, and code readability.
