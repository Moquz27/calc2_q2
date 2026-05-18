# Surface Plotter

## 1. Tổng quan

Project này là một chương trình Python dùng để vẽ một mặt 3D có dạng:

```text
z = f(x,y)
```

Mặt được vẽ phía trên miền nằm giữa hai đường biên
`x = g(y)` và `x = h(y)` nằm trong mặt phẳn `xOy` :

```text
D = {(x,y) | c <= y <= d and min(g(y), h(y)) <= x <= max(g(y), h(y))}
```

User sẽ nhập hàm `f(x,y)`, 2 đường giới hạn `g(y)` và `h(y)`,
và 2 hẳng số `c` và `d`.

## 2. Cấu trúc Repository 

```text
calc2_q2/
├── README.md
├── requirements.txt
├── surface_plot.py
├── VI.md
└── outputs/          # thư mục này sẽ được tạo tại máy người dùng sau khi chạy thành công lần đầu
```

- `README.md`: giải thích project và hướng dẫn sử dụng, cài đặt.
- `requirements.txt`: các package Python cần thiết.
- `surface_plot.py`: source code chính.
- `design_n_algorithm/`: giải thích chi tiết về thiết kế và thuật toán.
- `outputs/`: lưu ảnh biểu đồ được tạo và file lưu input.

## 3. Yêu cầu

- Python 3.10++
- numpy
- matplotlib
- sympy

## 4. Quá trình cài đặt

Nếu như máy bạn không có git hoặc không biết dùng git, 
hãy tải repo xuống dưới dạng zip và unzip.

Nếu không:
Đầu tiên, clone repository và cd vào thư mục project:

```bash
git clone https://github.com/Moquz27/calc2_q2.git
cd calc2_q2
```

Nếu repository đã được tải sẵn, chỉ cần mở terminal trong thư mục
calc2_q2/: Chuột phải vào thư mục và chọn open cmd/terminal 

hoặc dùng: 
```cd calc2_q2/``` / 
```cd calc2_q2_zip/ ``` 

Tuỳ thuộc vào tên folder


Tiếp theo, cần cài các package cần thiết:
### Windows:

```bat
python -m pip install -r requirements.txt
```

### macOS/Linux:

Nên sử dụng virtual environment (venv) trên macOS/Linux để tránh các vấn đề 
về quyền của Python hệ thống hoặc Homebrew Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## 5. How to Run

Đảm bảo đã cd đến thư mục chứa file .py

### Windows
Double click vào file src pyhton

Hoặc

Chạy CMD trong `calc2_q2/` và chạy:

```bat
python surface_plot.py
```

### macOS/Linux

Kích hoạt venv trước:

```bash
source .venv/bin/activate
```

Và chạy:

```bash
python3 surface_plot.py
```

## 6. Input Rules

- Sử dụng cú pháp toán học của Python.
- Dùng `x**2` thay vì `x^2`.
- `f(x,y)` được phép dùng các biến `x` và `y`.
- `g(y)` và `h(y)` chỉ được dùng biến `y`.
- `c` và `d` phải là số hữu hạn hoặc biểu thức số như `pi`,
  `2*pi`, hoặc `sqrt(2)`.
- `c < d`.


Example input:

```text
f(x,y): x**2 + y**2
g(y): y
h(y): y + 2
c: 0
d: 2
```

Các hàm và biến hỗ trợ:
`sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `Abs`, `pi`, `E`.

## 7. Output

Sau khi nhập input hợp lệ, chương trình sẽ:

- mở cửa sổ biểu đồ 3D bằng Matplotlib,
- tự động tạo thư mục `outputs/`,
- lưu biểu đồ dưới dạng file `.png`,
- lưu các giá trị input đã nhập dưới dạng file `.txt` tương ứng.

Thư mục `outputs/` chỉ được tạo tự động sau khi chương trình chạy thành công
và lưu output.

Tên file output sẽ chứa timestamp, ví dụ:

```text
surface_20260511_153020.png
surface_20260511_153020.txt
