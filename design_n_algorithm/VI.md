# Surface Plotter – Design and Algorithm Report

## 1. Introduction

Mục tiêu của code là tạo ra một surface trong không gian 3D, có dạng:

```text
z = f(x,y)
```

Mặt này được vẽ trên một hành chiếu xuống mặt phẳng `xOy`:

```text
D = {(x,y) | c <= y <= d and g(y) <= x <= h(y)}
```

Đề bài yêu cầu người dùng nhập:

- `f(x,y)`: hàm độ cao của mặt,
- `g(y)`: đường biên trái theo biến `x`,
- `h(y)`: đường biên phải theo biến `x`,
- `c`: cận dưới của `y`,
- `d`: cận trên của `y`.

File `surface_plot.py` đọc các giá trị này từ terminal/cmd, sinh lưới số trên miền
`D`, tính `z = f(x,y)`, vẽ mặt bằng Matplotlib, và tự động lưu kết quả.

## 2. Problem Analysis

Miền chiếu `D` có thể không phải là hình chữ nhật trong mặt phẳng `xOy`. Với
mỗi giá trị `y` cố định, khoảng hợp lệ của `x` là:

```text
g(y) <= x <= h(y)
```

Vì hai biên đều phụ thuộc vào `y`, cạnh trái và cạnh phải của miền có thể là
đường cong. Nếu tạo lưới chữ nhật trực tiếp theo một khoảng `x` toàn cục và một
khoảng `y`, nhiều điểm sinh ra có thể nằm ngoài miền `D`. Khi đó cần thêm bước
lọc hoặc mask các điểm không hợp lệ.

Khó khăn kỹ thuật nằm ở chỗ khoảng hợp lệ của `x` thay đổi theo `y`. Điều này
dẫn tới ý tưởng biến đổi một miền tham số chữ nhật đơn giản thành miền cong
`D`. Code sử dụng tham số `t` để chạy từ `g(y)` đến `h(y)` với mỗi giá trị `y`
được lấy mẫu.

## 3. Design Goals

Chương trình được thiết kế để rõ ràng và phù hợp với một bài tập Giải tích
nhiều biến ở bậc đại học. Các mục tiêu thiết kế chính là:

- giữ code đơn giản, dễ đọc,
- parse biểu thức toán học một cách an toàn,
- không dùng Python `eval()`,
- dùng NumPy cho mảng số và tính toán vector hóa,
- dùng SymPy cho symbolic parsing và `lambdify()`,
- dùng Matplotlib cho trực quan hóa 3D,
- giữ thuật toán đủ tổng quát cho nhiều lựa chọn `g(y)` và `h(y)`,
- tránh class, framework, hoặc kiến trúc phức tạp không cần thiết.

Implementation được viết theo kiểu thủ tục. Mỗi hàm có một nhiệm vụ rõ ràng:
parse biểu thức, validate và sinh mesh, lưu input record, và vẽ kết quả.

## 4. Possible Approaches

### 4.1 Direct Rectangular Grid

Một hướng làm là chọn một khoảng toàn cục cho `x`, chọn một khoảng cho `y`, rồi
tạo lưới chữ nhật trực tiếp trên mặt phẳng `xOy`.

Ưu điểm của cách này là dễ hiểu và dễ code. Tuy nhiên, nó không khớp tốt với
miền đã cho. Vì khoảng hợp lệ của `x` phụ thuộc vào `y`, lưới chữ nhật trực
tiếp có thể chứa nhiều điểm nằm ngoài `D`. Ngoài ra, việc chọn cận toàn cục cho
`x` cũng không đơn giản nếu chưa phân tích trước `g(y)` và `h(y)`.

### 4.2 Rectangular Grid with Masking

Một hướng khác là tạo một lưới chữ nhật lớn, sau đó mask các điểm không thỏa:

```text
g(y) <= x <= h(y)
```

Cách này linh hoạt hơn lưới chữ nhật thuần túy. Tuy nhiên, nó lãng phí tính
toán cho các điểm sau đó bị loại bỏ. Nó cũng có thể làm surface plot kém sạch
hơn vì vùng bị mask có thể tạo ra khoảng trống hoặc biên không đều. Với một bài
trực quan hóa calculus thân thiện cho người học, mức phức tạp này là không cần
thiết.

### 4.3 Parameterization-Based Mesh (Chosen Approach)

Hướng được chọn là tham số hóa các giá trị `x` hợp lệ bằng công thức:

```text
x = g(y) + t(h(y)-g(y))
```

trong đó:

```text
c <= y <= d
0 <= t <= 1
```

Cách này chỉ sinh các điểm thuộc miền `D`, với điều kiện `g(y) <= h(y)`. Nó
cũng hoạt động tự nhiên với NumPy broadcasting và tạo ra một lưới số chữ nhật
sạch trong các biến tham số `(y,t)`.

Cách này được chọn vì nó đi trực tiếp từ định nghĩa toán học của miền và vẫn
đơn giản để cài đặt.

## 5. Mathematical Foundation

### 5.1 Projection Region

Miền chiếu là:

```text
D = {(x,y) | c <= y <= d and g(y) <= x <= h(y)}
```

Điều này có nghĩa là `y` chạy từ `c` đến `d`. Với mỗi `y` cố định, giá trị `x`
chạy từ biên trái `g(y)` đến biên phải `h(y)`.

### 5.2 Parameterization Formula

Chương trình giới thiệu tham số `t`:

```text
0 <= t <= 1
```

Sau đó định nghĩa:

```text
x = g(y) + t(h(y)-g(y))
```

Miền tham số là hình chữ nhật:

```text
(y,t) in [c,d] x [0,1]
```

### 5.3 Why This Works

Khi `t = 0`:

```text
x = g(y)
```

Khi `t = 1`:

```text
x = h(y)
```

Khi `0 < t < 1`, giá trị `x` nằm giữa `g(y)` và `h(y)`. Vì vậy, nếu
`g(y) <= h(y)`, mọi điểm được sinh ra đều thỏa:

```text
g(y) <= x <= h(y)
```

Miền tham số chữ nhật `[c,d] x [0,1]` được ánh xạ sang miền chiếu cong `D`.

## 6. Numerical Algorithm

### Step 1 — Read User Input

Chương trình đọc năm chuỗi từ terminal:

- `f(x, y)`,
- `g(y)`,
- `h(y)`,
- `c`,
- `d`.

Các giá trị này được lưu trong dictionary `input_values` để có thể ghi lại vào
file `.txt` sau khi vẽ thành công.

### Step 2 — Parse Mathematical Expressions

Các chuỗi `f`, `g`, và `h` được parse bằng SymPy `parse_expr()`. Chương trình
kiểm tra biểu thức chỉ dùng các biến được phép. Sau đó, trong
`build_surface_mesh()`, các biểu thức symbolic được chuyển thành hàm số bằng
`sp.lambdify()`.

### Step 3 — Generate Numerical Samples

Code sử dụng:

```python
GRID_SIZE = 80
```

Chương trình lấy mẫu `y` bằng:

```python
np.linspace(c, d, GRID_SIZE)
```

và lấy mẫu `t` bằng:

```python
np.linspace(0.0, 1.0, GRID_SIZE)
```

### Step 4 — Construct the Mesh

Các hàm biên được tính trên các giá trị `y` đã lấy mẫu. Chương trình lưu chúng
vào `left_boundary` và `right_boundary`.

Sau đó chương trình tạo:

```python
y_grid = np.repeat(y_values[:, np.newaxis], GRID_SIZE, axis=1)
x_grid = left_boundary[:, np.newaxis] + (
    right_boundary - left_boundary
)[:, np.newaxis] * t_values[np.newaxis, :]
```

Đoạn này dùng NumPy broadcasting. `left_boundary[:, np.newaxis]` biến biên trái
thành một cột. `t_values[np.newaxis, :]` biến các giá trị tham số thành một
hàng. Khi nhân chúng với nhau, NumPy tạo ra một lưới hai chiều đầy đủ.

### Step 5 — Evaluate the Surface

Sau khi mesh được tạo, chương trình tính:

```text
Z = f(X,Y)
```

Trong code, bước này là:

```python
z_grid = np.asarray(f(x_grid, y_grid), dtype=float)
```

Vì hàm được tạo bằng `lambdify(..., modules="numpy")`, nó có thể tính trực tiếp
trên toàn bộ NumPy grid.

### Step 6 — Visualize the Surface

Hàm `plot_surface()` tạo một figure 3D bằng Matplotlib và vẽ mặt bằng:

```python
ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")
```

Biểu đồ cũng có nhãn trục, tiêu đề, colorbar, và hai đường biên.

## 7. Expression Parsing and Safety

Chương trình không dùng Python `eval()`. Điều này quan trọng vì `eval()` có thể
thực thi code Python tùy ý từ input của người dùng, không an toàn.

Thay vào đó, code dùng:

```python
parse_expr(...)
```

với `local_dict` được kiểm soát:

```python
local_dict = {"x": x_symbol, "y": y_symbol}
```

Code cũng định nghĩa `SAFE_GLOBAL_DICT`, giới hạn các cấu trúc symbolic và hàm
toán học được phép. Các hàm và hằng số được hỗ trợ gồm:

```text
sin, cos, tan, exp, log, sqrt, Abs, pi, E
```

Sau khi parse, code kiểm tra:

```python
unexpected_symbols = expression.free_symbols - allowed_symbols
```

Điều này đảm bảo:

- `f(x,y)` chỉ được dùng `x` và `y`,
- `g(y)` chỉ được dùng `y`,
- `h(y)` chỉ được dùng `y`.

Nếu biểu thức chứa biến không hợp lệ, chương trình raise `ValueError`.

## 8. Numerical Grid Construction

`GRID_SIZE` điều khiển số mẫu theo mỗi hướng tham số. Trong code hiện tại:

```python
GRID_SIZE = 80
```

Nếu `GRID_SIZE = n`, chương trình tạo `n` mẫu cho `y` và `n` mẫu cho `t`. Mesh
cuối cùng có khoảng `n²` điểm.

Các mảng chính là:

- `x_grid`: tất cả tọa độ `x` được lấy mẫu trong miền,
- `y_grid`: tất cả tọa độ `y` được lấy mẫu,
- `z_grid`: các độ cao của mặt sau khi tính `f(x,y)`.

Code cũng xử lý trường hợp `g(y)` hoặc `h(y)` là biểu thức hằng. Nếu một biên
trả về scalar, nó được mở rộng bằng `np.full_like()` để có cùng shape với
`y_values`.

Chương trình kiểm tra các mảng biên và `z_grid` chỉ chứa giá trị hữu hạn. Điều
này tránh các biểu đồ không hợp lệ do `nan` hoặc `inf`.

## 9. Input Validation

Chương trình validate input ở nhiều bước:

- `c` và `d` phải là số hữu hạn.
- `c < d`.
- `f` chỉ được dùng `x` và `y`.
- `g` và `h` chỉ được dùng `y`.
- `g(y) <= h(y)` trên các giá trị `y` đã lấy mẫu.
- các giá trị biên phải hữu hạn.
- các giá trị `Z` phải hữu hạn.

Nếu validation thất bại, chương trình dừng plotting và in thông báo lỗi rõ ràng
ra terminal.

Kiểm tra `g(y) <= h(y)` là kiểm tra số học trên sampled grid. Nó không phải là
một chứng minh symbolic cho toàn bộ khoảng `[c,d]`.

## 10. Surface Visualization

Chương trình dùng Matplotlib 3D axes:

```python
ax = fig.add_subplot(111, projection="3d")
```

Mặt được vẽ bằng:

```python
ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")
```

Biểu đồ gồm:

- tiêu đề,
- nhãn cho các trục `x`, `y`, và `z`,
- colorbar cho giá trị `z`,
- legend.

Code cũng vẽ hai đường biên:

- `x = g(y)`,
- `x = h(y)`.

Hai đường này được lấy từ cột đầu và cột cuối của mesh. Chúng giúp người xem
nhìn rõ biên của miền chiếu trên mặt 3D.

## 11. Automatic Output Saving

Phiên bản hiện tại của `surface_plot.py` có chức năng autosave.

Trước khi hiển thị biểu đồ, chương trình tạo thư mục output:

```python
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

trong đó:

```python
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
```

Chương trình lưu biểu đồ thành file `.png` có timestamp:

```text
surface_YYYYMMDD_HHMMSS.png
```

Nó cũng lưu input của người dùng thành file `.txt` cùng timestamp:

```text
surface_YYYYMMDD_HHMMSS.txt
```

Figure được lưu bằng:

```python
fig.savefig(png_path, dpi=150)
```

Bước này xảy ra trước:

```python
plt.show()
```

Lưu trước `plt.show()` an toàn hơn vì một số backend của Matplotlib có thể làm
thay đổi hoặc clear figure sau khi cửa sổ hiển thị bị đóng.

## 12. Complexity Discussion

Gọi:

```text
n = GRID_SIZE
```

Mesh có khoảng:

```text
n²
```

điểm. Vì vậy, độ phức tạp thời gian xấp xỉ:

```text
O(n²)
```

Độ phức tạp bộ nhớ cũng xấp xỉ:

```text
O(n²)
```

vì chương trình lưu `x_grid`, `y_grid`, và `z_grid`.

`GRID_SIZE` lớn hơn cho surface mượt hơn nhưng tốn thời gian và bộ nhớ hơn.
`GRID_SIZE` nhỏ hơn chạy nhanh hơn nhưng surface có thể thô hơn.

## 13. Limitations

Chương trình chỉ hỗ trợ các mặt dạng tường minh:

```text
z = f(x,y)
```

Chương trình không trực tiếp hỗ trợ các mặt implicit như:

```text
x² + y² + z² = 1
```

Một số hàm có thể không xác định trên một phần miền `D`. Ví dụ, căn bậc hai có
thể nhận giá trị âm tại một số điểm lấy mẫu. Khi đó chương trình có thể báo lỗi
input không hợp lệ vì giá trị sinh ra không hữu hạn.

Sai số floating-point cũng có thể tạo artifact nhỏ gần biên hoặc gần điểm kỳ
dị.

Validation là numerical, không phải symbolic proof. Nó kiểm tra các điểm được
lấy mẫu thay vì chứng minh điều kiện cho mọi giá trị thực trong `[c,d]`.

Nếu muốn vẽ một sphere đầy đủ, cần tách thành nửa trên và nửa dưới, vì một
sphere đầy đủ không phải là một hàm đơn trị `z = f(x,y)`.

## 14. Example Walkthrough

Xét ví dụ:

```text
f(x,y) = x**2 + y**2
g(y) = y
h(y) = y + 2
c = 0
d = 2
```

1. Chương trình lấy mẫu `y` từ `0` đến `2`.
2. Chương trình lấy mẫu `t` từ `0` đến `1`.
3. Chương trình tính:

```text
x = y + t((y + 2) - y)
```

Công thức này rút gọn thành:

```text
x = y + 2t
```

4. Khi `t = 0`, `x = y`.
5. Khi `t = 1`, `x = y + 2`.
6. Khi `0 < t < 1`, `x` nằm giữa `y` và `y + 2`.
7. Chương trình tính:

```text
z = x² + y²
```

8. Cuối cùng, Matplotlib vẽ mặt trên miền đã sinh và chương trình lưu cả biểu
đồ lẫn input record.

## 15. Conclusion

Chương trình giải bài toán bằng cách dùng parameterization-based mesh. Cách này
khớp với định nghĩa toán học của miền:

```text
D = {(x,y) | c <= y <= d and g(y) <= x <= h(y)}
```

So với sampling trực tiếp trên hình chữ nhật, phương pháp được chọn tránh sinh
nhiều điểm không hợp lệ nằm ngoài miền. Nó cũng giữ implementation đơn giản và
phù hợp với tính toán vector hóa bằng NumPy.

Nhìn chung, lời giải cân bằng giữa tính đúng toán học, sự đơn giản về mặt số
học, chất lượng trực quan hóa, và độ dễ đọc của code.
