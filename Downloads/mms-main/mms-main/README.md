# A* Micromouse – Mo phong robot tim duong

> **Mon hoc:** Lap trinh song song  
> **Chuc nang:** Mo phong robot tu tim duong trong me cung bang thuat toan **A\***  
> **Ngon ngu:** Python (giao dien) + C++ (thuat toan)

---

## Muc luc

1. [Tong quan du an](#1-tong-quan-du-an)
2. [Kien truc tach biet](#2-kien-truc-tach-biet)
3. [Cai dat va chay](#3-cai-dat-va-chay)
4. [Cau truc thu muc](#4-cau-truc-thu-muc)
5. [Giao thuc giao tiep C++↔Python](#5-giao-thuc-giao-tiep-cpython)
6. [Thuat toan A*](#6-thuat-toan-a)
7. [Huong dan su dung giao dien](#7-huong-dan-su-dung-giao-dien)
8. [Huong dan sua code](#8-huong-dan-sua-code)
9. [Lien quan Lap trinh song song](#9-lien-quan-lap-trinh-song-song)

---

## 1. Tong quan du an

**Micromouse** la cuoc thi robot tu hanh: robot duoc dat vao goc me cung, tu tim duong
den trung tam **ma khong biet truoc vi tri cac tuong**.

Du an nay mo phong bai toan do voi:
- Me cung ngau nhien kich thuoc **a x b** (tuy chinh 1–100)
- Robot dung **Online A\*** — hieu biet tuong qua cam bien, lap lai ke hoach moi buoc
- Giao dien do hoa Python (Tkinter, chay ngay, khong can cai them thu vien)
- Thuat toan viet bang C++ (bien dich mot lan, chay nhanh)
- Tuy chinh ban do: ve hinh tu do, xoa/them tuong, dat dich bat ky

---

## 2. Kien truc tach biet

```
┌─────────────────────────┐        stdin / stdout        ┌──────────────────────┐
│   ui.py  (Python)       │◄────────────────────────────►│  algorithm/astar.exe │
│                         │                              │      (C++)           │
│  • Sinh me cung (DFS)   │  Python tra loi tung lenh:  │                      │
│  • Ve giao dien Tkinter │  wallFront → "true"/"false"  │  • Chay thuat toan   │
│  • Tra loi cam bien     │  moveForward → ""            │    A* Online         │
│  • Cap nhat hoa si      │  goalX/goalY → toa do dich  │  • Gui lenh cam bien │
└─────────────────────────┘                              │  • Gui lenh di chuyen│
                                                         └──────────────────────┘
```

**Quy tac don gian:** Python biet toan bo ban do (da sinh ra me cung); C++ khong biet,
phai hoi tung buoc. Khi C++ hoi `wallFront`, Python tra loi that hay khong, C++ dua
vao do de quyet dinh huong di.

**Loi ich khi tach:**
- Thanh vien thuat toan: chi sua `algorithm/astar.cpp`, khong can biet Tkinter
- Thanh vien giao dien: chi sua `ui.py`, khong can biet A*
- Co the thay the thuat toan khac (BFS, Dijkstra, ...) ma khong doi giao dien

---

## 3. Cai dat va chay

### Yeu cau

| Cong cu | Kiem tra | Cai dat neu chua co |
|---------|---------|---------------------|
| Python 3.7+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| g++ (GCC) | `g++ --version` | Windows: [MinGW-w64](https://www.mingw-w64.org/) hoac [MSYS2](https://www.msys2.org/) |

> **Tkinter** co san trong Python, khong can cai them.

### Buoc chay (lan dau)

```bash
# 1. Clone repo
git clone https://github.com/viethoang84/astar-micromouse.git
cd astar-micromouse

# 2. Build C++ algorithm (chi can lam 1 lan, hoac moi khi sua astar.cpp)
cd algorithm
.\build.bat          # Windows
# hoac: make         # Linux / Mac
cd ..

# 3. Chay giao dien
python ui.py
```

### Buoc chay (lan sau, neu khong sua astar.cpp)

```bash
python ui.py
```

### Neu khong co g++ (chay thu nhanh)

```bash
python maze_astar.py    # Ban Python thuan tuy, khong can C++
```

---

## 4. Cau truc thu muc

```
astar-micromouse/
│
├── ui.py                  ← GIAO DIEN (Python/Tkinter)
│                            Sua file nay neu muon them tinh nang UI
│
├── algorithm/
│   ├── astar.cpp          ← THUAT TOAN (C++)
│   │                        Sua file nay neu muon toi uu A* hoac doi thuat toan
│   ├── build.bat          ← Build tren Windows: chay .\build.bat
│   └── Makefile           ← Build tren Linux/Mac: chay make
│
├── maze_astar.py          ← Ban du phong (Python thuan tuy, khong can C++)
│
└── README.md              ← File nay
```

---

## 5. Giao thuc giao tiep C++↔Python

Khi nhan **Run A\***, Python spawn C++ lam tien trinh con (`subprocess`). Hai ben
giao tiep qua **stdin/stdout** (moi lenh = 1 dong van ban).

### C++ gui lenh, Python tra loi (query)

| C++ gui | Python tra loi | Y nghia |
|---------|---------------|---------|
| `mazeWidth` | `16` | Chieu rong ban do |
| `mazeHeight` | `16` | Chieu cao ban do |
| `goalX` | `7` | Toa do X o dich |
| `goalY` | `7` | Toa do Y o dich |
| `wallFront` | `true` / `false` | Co tuong phia truoc khong? |
| `wallLeft` | `true` / `false` | Co tuong ben trai khong? |
| `wallRight` | `true` / `false` | Co tuong ben phai khong? |
| `moveForward` | `` (rong) | Tien 1 o, Python cap nhat vi tri robot |
| `turnLeft` | `` (rong) | Quay trai 90°, Python cap nhat huong |
| `turnRight` | `` (rong) | Quay phai 90°, Python cap nhat huong |

### C++ gui lenh hien thi (display – khong can phan hoi)

| C++ gui | Y nghia |
|---------|---------|
| `setColor 3 4 y` | To o (3,4) mau vang (y=yellow) |
| `setColor 0 0 g` | To o (0,0) mau xanh la (g=green) |
| `clearAllColor` | Xoa tat ca mau |

**Ma mau:** `k`=den, `b`=xanh duong, `c`=cyan, `g`=xanh la, `o`=cam,
`r`=do, `w`=trang, `y`=vang, `G`=xanh dam, `R`=do dam

### He toa do

```
Y
^
|  (0,H-1)  ...  (W-1,H-1)
|    ...              ...
|  (0,0)    ...  (W-1,0)
+──────────────────────► X
```

Robot xuat phat tai `(0,0)`, mat huong Bac (Y tang). Dich mac dinh = trung tam.

---

## 6. Thuat toan A*

### Y tuong chinh

```
f(n) = g(n)  +  h(n)
        |           |
  Chi phi da di   Uoc luong con lai
  (so buoc thuc)  (Manhattan distance)
```

O co `f` nho nhat duoc xet truoc → A* tim duong toi uu.

### Online A* (A* thoi gian thuc)

Robot **khong biet truoc ban do**. Moi buoc:

```
1. Cam bien 3 tuong xung quanh (trai, phai, truoc)
2. Cap nhat ban do da biet
3. Chay A* tu vi tri hien tai → dich
   (tuong chua biet = coi la thong → "lac quan")
4. Di chuyen 1 buoc theo duong A* vua tim
5. Lap lai tu buoc 1
```

Neu phat hien tuong chan duong da ke hoach → **tu replanning** ngay lap tuc.

### Heuristic

```cpp
// Manhattan distance den o dich (admissible vi robot khong di cheo)
float heuristic(int x, int y) {
    return abs(x - goalX) + abs(y - goalY);
}
```

---

## 7. Huong dan su dung giao dien

```
[ Rong(a) ] [ Cao(b) ] [ Do mo(%) ] [ Hinh ]
[ Generate Maze ] [ Run A* ] [ Stop ] [ Ve:TAT ] [ Reset ] [ Xoa dich ] [ Toc do ]
[ Legend mau sac ]
+───────────────────────────────────+
│           Ban do me cung          │
+───────────────────────────────────+
```

### Cac buoc co ban

| Buoc | Thao tac |
|------|---------|
| 1 | Nhap **Rong** va **Cao** (1–100) |
| 2 | Chon **Do mo** (0% = day tuong, 80% = nhieu vung thong) |
| 3 | Chon **Hinh** (chu nhat, hinh L, hinh T, ...) |
| 4 | Nhan **Generate Maze** → sinh me cung ngau nhien |
| 5 | *(Tuy chon)* Click vao o de dat dich (mac dinh = trung tam) |
| 6 | Nhan **Run A\*** → robot tu tim duong |

### Bang mau sac

| Mau | Y nghia |
|-----|---------|
| Xanh nhat | O robot da di qua |
| Vang | Duong A* dang ke hoach |
| Xanh la nhat | O xuat phat |
| Nen do nhat | O dich |
| Xanh la dam | Robot da den dich |
| Xam | Vung khong ton tai (inactive) |

### Chinh sua ban do thu cong

| Thao tac | Ket qua |
|----------|---------|
| Click **canh o** (gan tuong) | Xoa / them lai tuong do |
| Click **giua o** | Dat dich tai o do |
| Click phai | Xoa dich |
| Bat **Ve: BAT** + keo trai | Them o (mo rong ban do) |
| Bat **Ve: BAT** + keo phai | Xoa o (thu hep ban do) |

---

## 8. Huong dan sua code

### Sua thuat toan (algorithm/astar.cpp)

File C++ co cau truc ro rang, moi phan co chu thich:

```
main()
 ├─ Query mazeWidth / mazeHeight / goalX / goalY tu Python
 ├─ markWall(): danh dau tuong bien
 └─ Vong lap chinh:
     ├─ senseWalls(): hoi Python 3 tuong, cap nhat wallKnown[][]
     ├─ astar(): tim duong voi kien thuc hien tai
     ├─ turnToFace() / stepForward(): gui lenh den Python
     └─ Lap lai
```

**Vi du: doi heuristic Chebyshev** (cho phep di cheo — chi demo, robot nay khong di cheo):
```cpp
// Trong algorithm/astar.cpp, thay ham heuristic():
float heuristic(int x, int y) {
    return max(abs(x - goalX), abs(y - goalY));  // Chebyshev
}
```

Sau khi sua xong, build lai:
```bash
cd algorithm && .\build.bat
```

### Sua giao dien (ui.py)

Cac hang so mau o dau file, de sua:
```python
C_VISITED  = "#88ccff"   # mau o da di qua
C_PATH     = "#ffdd44"   # mau duong ke hoach
C_ROBOT    = "#0055ff"   # mau robot
```

Ham quan trong:
- `generate_maze()` — sinh me cung DFS
- `_draw()` — ve toan bo ban do len canvas
- `_handle()` — xu ly lenh tu C++, day la "cau noi" giua Python va C++
- `_on_move()` — cap nhat hien thi sau moi buoc di

---

## 9. Lien quan Lap trinh song song

Du an nay la **phan mo phong don luong** (1 robot, 1 luong) de demo thuat toan.
Trong nhom, cac thanh vien khac co the ap dung **da luong (multi-threading)** de:

- Chay nhieu robot cung luc (moi robot 1 thread)
- Song song hoa ban than vong lap A* (parallel A*)
- Phan cong explore ban do theo vung (multi-agent exploration)

---

## Tham khao

- [MMS – Micromouse Simulator goc](https://github.com/mackorone/mms)
- [A\* Search Algorithm – Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- Hart, P.E., Nilsson, N.J., Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*
