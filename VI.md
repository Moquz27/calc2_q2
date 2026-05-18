# Surface Plotter – Design and Algorithm Report

## 1. Introduction

Mục tiêu của code là tạo ra một surface trong không gian 3D, có dạng:

```text
z = f(x,y)
```

Mặt này được vẽ trên miền nằm giữa hai đường biên `x = g(y)` và `x = h(y)`
trong mặt phẳng `xOy`:

```text
D = {(x,y) | c <= y <= d and min(g(y), h(y)) <= x <= max(g(y), h(y))}
```

Đề bài yêu cầu người dùng nhập:

- `f(x,y)`: hàm độ cao của mặt,
- `g(y)`: một đường biên theo biến `x`,
- `h(y)`: đường biên còn lại theo biến `x`,
- `c`: cận dưới của `y`,
- `d`: cận trên của `y`.

File `surface_plot.py` đọc các giá trị này từ terminal/cmd, sinh lưới các điểm trên miền
`D` (sử dụng script build_surface_mesh() ) sau đó tính `z = f(x,y)`, vẽ mặt bằng Matplotlib, và tự động lưu kết quả.

## 2. Phân tích vấn đề cần giải quyết
Thứ nhất, miều D, không nhất thiết là hình chữ nhật cố định trong mặt phẳng `xOy`. Vì, với
mỗi giá trị `y` cố định, khoảng hợp lệ của `x` là khoảng nằm giữa hai giá trị
biên:

```text
min(g(y), h(y)) <= x <= max(g(y), h(y))
```

Vì hai biên đều phụ thuộc vào `y`, cạnh trái và cạnh phải của miền có thể là
đường cong. Nếu tạo lưới chữ nhật trực tiếp theo một khoảng `x` toàn cục và một
khoảng `y`, nhiều điểm sinh ra có thể nằm ngoài miền `D`. 

ví dụ, với input sau:
```text
g(y)=y
h(y)=y+2
c=0
d=2
```
với y=0, khoảng x sẽ là 0-2
với y=1, khoảng x sẽ là từ 1-3
...
tiếp tục như vậy. Như hình:
<img width="1280/2" height="1209/2" alt="telegram-cloud-photo-size-5-6075381573097295960-y" src="https://github.com/user-attachments/assets/d8822de2-af2f-4b53-8d87-8face439ad1e" />

Khi đó cần thêm bước lọc hoặc mask các điểm không hợp lệ. 
nói cách khác, Code sẽ tạo toàn bộ các điểm theo miền, tức từ khoảng x theo y bé nhất tới khoảng x theo y lớn nhất. 
sau đó sẽ sử dụng boolean để giải quyết các điểm sai nằm ngoài miền D.
Ví dụ: ```valid = (x >= min(g(y), h(y))) & (x <= max(g(y), h(y)))```

kết quả thu được:
``` text
Điểm	valid
(0,2)	False
(1,2)	False
(3,2)	True
```

Khó khăn nằm ở chỗ khoảng hợp lệ của `x` thay đổi theo `y`. 

Nếu sử dụng phương pháp mask, tập hợp các điểm dùng để dựng surface (còn gọi là mesh) sinh ra sẽ ở dạng lưới theo hình chữ nhật,
rồi bị lọc dần đi. Tuy nhiên điều này dẫn đến việc khi plot bề mặt, output ra sẽ bị răng cưa ở viền. 
Ngoài ra còn lãng phí việc tính toán. Đôi lúc số điểm hợp lệ chỉ chiếm 20-30% tổng số điểm sinh ra.

Điều này dẫn tới ý tưởng biến đổi một miền tham số chữ nhật đơn giản thành miền cong
`D`. Code tính cả hai biên trước, sau đó dùng giá trị nhỏ hơn làm biên trái và
giá trị lớn hơn làm biên phải cho từng giá trị `y` được lấy mẫu.

Nói 1 cách dễ hiểu
Code sử dụng `t` như một tham số nội bộ, chạy từ 0 tới 1, với 0 là biên trái
`min(g(y), h(y))` và 1 là biên phải `max(g(y), h(y))`.
Với mỗi 1 giá trị x, sẽ được sinh với công thức
```
left_boundary = min(g(y), h(y))
right_boundary = max(g(y), h(y))
x = left_boundary + t(right_boundary - left_boundary)
```
Với mỗi y cố định, t chạy từ 0 đến 1. Khi t=0 thì x là biên trái, khi t=1 thì
x là biên phải, còn khi 0<t<1 thì x nằm giữa hai biên.
Ví dụ
y = 0
t chạy từ 0 - 1
x với y=0 sẽ được sinh từ biên nhỏ hơn tới biên lớn hơn, tương đương t từ 0 tới 1



## 3. Design Goals
KISS :> keep it simple, stupid

## 4. Phương pháp được chọn để sử dụng

Parameterization

Hướng được chọn là tham số hóa các giá trị `x` hợp lệ bằng công thức:

```text
left_boundary = min(g(y), h(y))
right_boundary = max(g(y), h(y))
x = left_boundary + t(right_boundary-left_boundary)
```

trong đó:

```text
c <= y <= d
0 <= t <= 1
```

Cách cài đặt hiện tại tính:

```text
left_boundary = min(g(y), h(y))
right_boundary = max(g(y), h(y))
```

rồi dùng công thức tham số hóa từ `left_boundary` tới `right_boundary`. Vì vậy
chương trình xử lý được cả trường hợp hai đường biên đổi vị trí trái/phải.




## 5. Định nghĩa toán học

### 5.1 Projection Region - Miền chiếu

```text
D = {(x,y) | c <= y <= d and min(g(y), h(y)) <= x <= max(g(y), h(y))}
```

Điều này có nghĩa là `y` chạy từ `c` đến `d`. 
Với mỗi `y` cố định, giá trị `x` chạy từ giá trị nhỏ hơn trong hai biên
`g(y)`, `h(y)` đến giá trị lớn hơn.

### 5.2 Parameterization Formula

Code sử dụng tham số `t`:

```text
0 <= t <= 1
```

Sau đó định nghĩa:

```text
left_boundary = min(g(y), h(y))
right_boundary = max(g(y), h(y))
x = left_boundary + t(right_boundary-left_boundary)
```

Miền tham số là hình chữ nhật:

```text
(y,t) in [c,d] x [0,1]
```

### 5.3 giải thích phần thông tin trước

Khi `t = 0`:

```text
x = left_boundary
```

Khi `t = 1`:

```text
x = right_boundary
```

Khi `0 < t < 1`, giá trị `x` nằm giữa hai đường biên. Vì `left_boundary` và
`right_boundary` được tính bằng `min()` và `max()` theo từng giá trị `y`, mọi
điểm được sinh ra đều thỏa:

```text
min(g(y), h(y)) <= x <= max(g(y), h(y))
```

Miền tham số chữ nhật `[c,d] x [0,1]` được ánh xạ sang miền chiếu cong `D` với công thức trên


## 6. Numerical Algorithm

### Step 1 — Đọc input

Chương trình đọc năm chuỗi từ terminal:

- `f(x, y)`,
- `g(y)`,
- `h(y)`,
- `c`,
- `d`.

Các giá trị này được lưu trong dictionary `input_values` để có thể ghi lại vào
file .txt sau khi vẽ

### Step 2 — Parse Mathematical Expressions

Các chuỗi `f`, `g`, và `h` được parse bằng SymPy `parse_expr()`. 
sau đó kiểm tra biểu thức chỉ dùng các biến được phép. Tiếp theo trong
`build_surface_mesh()`, các biểu thức symbolic được chuyển thành hàm số bằng
`sp.lambdify()`, nhằm tăng tốc độ xử lý khi cần tính toán hàg loạt điểm để tạo 
mesh

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

### Step 4 — Dựng mesh

Các hàm biên được tính trên các giá trị `y` đã lấy mẫu. Chương trình lưu giá
trị thô vào `g_values` và `h_values`, sau đó tính:

```python
left_boundary = np.minimum(g_values, h_values)
right_boundary = np.maximum(g_values, h_values)
```

Vì vậy, giá trị nhỏ hơn luôn là biên trái và giá trị lớn hơn luôn là biên phải
cho từng `y`.

Sau đó tạo:

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

```
Z = f(X,Y)
```
Với code là: 

```
z_grid = np.asarray(f(x_grid, y_grid), dtype=float)
```

### Step 6 — Visualize the Surface

Hàm `plot_surface()` tạo một figure 3D bằng Matplotlib và vẽ mặt bằng:

```python
ax.plot_surface(x_grid, y_grid, z_grid, cmap="viridis", edgecolor="none")
```

Biểu đồ cũng có nhãn trục, tiêu đề, colorbar, và hai đường biên. Mesh dùng
`left_boundary` và `right_boundary` động, nhưng hai đường biên được hiển thị
vẫn là hai curve gốc do người dùng nhập: `x = g(y)` và `x = h(y)`.


## 7. Expression Parsing and Safety

Code dùng parse expr để phân tích các biểu thức toán học được nhập vào:

```python
parse_expr(...)
```

với `local_dict` được sử dụng kiểm soát biến được dùng, nhằm giới hạn biến đúng:

```python
local_dict = {"x": x_symbol, "y": y_symbol}
```

Code cũng định nghĩa `SAFE_GLOBAL_DICT`, giới hạn các cấu trúc hàm
toán học được phép sử dụng và các hằng số được sử dụng. 

Các hàm và hằng số được hỗ trợ gồm:

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
- Biểu thức sử dụng đúng syntax/ đúng các biểu thức, hàm được hỗ trợ.

Nếu biểu thức chứa biến không hợp lệ, chương trình báo `ValueError`.

## 8. Numerical Grid Construction

`GRID_SIZE` điều khiển số mẫu theo mỗi hướng tham số. 

```python
GRID_SIZE = 80
```

Nếu `GRID_SIZE = n`, chương trình tạo `n` mẫu cho `y` và `n` mẫu cho `t`. Mesh
cuối cùng có `n²` điểm.

Các mảng chính là:

- `x_grid`: tất cả tọa độ `x` được lấy mẫu trong miền,
- `y_grid`: tất cả tọa độ `y` được lấy mẫu,
- `z_grid`: các độ cao của mặt sau khi tính `f(x,y)`.

#### Case đặc biệt
Đối với case g(y) và h(y) là 1 hằng số

Nếu không chia thành 1 trường hơp riêng biệt, khi xử lý để tạo ra đường biên, 
thay vì trả về một mảng biên có cùng số phần tử với y_values, 
biểu thức chỉ trả về một giá trị hằng số duy nhất.

Để xử lý trường hợp `g(y)` hoặc `h(y)` là biểu thức hằng. Nếu một biên
trả về scalar, nó được mở rộng bằng `np.full_like()` để có cùng shape với
`y_values`.

#### Case đặc biệt 2
Chương trình kiểm tra các mảng biên và `z_grid` chỉ chứa giá trị hữu hạn. Điều
này tránh các biểu đồ không hợp lệ do `nan` hoặc `inf`

##### ví dụ:
user nhập:
```
f(x,y) = 1 / (x - y)
```
Khi x = y, sẽ sinh ra điểm vô cực `z = 1 / 0`

Nếu phát hiện dữ liệu không hữu hạn, code sẽ báo lỗi thay vì cố vẽ một surface sai.

## 9. Input Validation

Chương trình xác thực input ở nhiều bước:

- `c` và `d` phải là số hữu hạn hoặc biểu thức số hợp lệ như `pi`, `2*pi`,
  hoặc `sqrt(2)`.
- `c < d`.
- `f` chỉ được dùng biến `x` và `y`.
- `g` và `h` chỉ được dùng biến `y`.
- `g(y)` và `h(y)` phải sinh giá trị hữu hạn trên các điểm `y` đã lấy mẫu.
- các giá trị biên phải hữu hạn.
- các giá trị `Z` phải hữu hạn.

Nếu validation thất bại, chương trình dừng plotting và in thông báo lỗi rõ ràng
ra terminal.

Chương trình không còn báo lỗi chỉ vì `g(y) > h(y)` tại một số điểm sample.
Thay vào đó, nó dùng giá trị nhỏ hơn làm biên trái và giá trị lớn hơn làm biên
phải. Việc chọn biên này là kiểm tra số học trên sampled grid, không phải là
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

- curve gốc `x = g(y)`,
- curve gốc `x = h(y)`.

Các cột đầu/cuối của mesh vẫn là biên trái/phải động được tạo bằng
`min(g(y), h(y))` và `max(g(y), h(y))`. Tuy nhiên, khi visualization, code tính
z cho chính `g_values` và `h_values` rồi vẽ hai curve gốc. Vì vậy nếu hai đường
giao nhau, chúng sẽ giao nhau tự nhiên thay vì bị đổi identity.

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

Với mỗi giá trị `y`, chương trình chỉ hỗ trợ một đoạn `x` liên tục. Chương
trình không hỗ trợ miền có lỗ hoặc nhiều đoạn `x` rời nhau cho cùng một `y`.

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
D = {(x,y) | c <= y <= d and min(g(y), h(y)) <= x <= max(g(y), h(y))}
```

So với sampling trực tiếp trên hình chữ nhật, phương pháp được chọn tránh sinh
nhiều điểm không hợp lệ nằm ngoài miền. Nó cũng giữ implementation đơn giản và
phù hợp với tính toán vector hóa bằng NumPy.

Nhìn chung, lời giải cân bằng giữa tính đúng toán học, sự đơn giản về mặt số
học, chất lượng trực quan hóa, và độ dễ đọc của code.
