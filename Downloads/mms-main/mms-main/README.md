# A* Micromouse Simulator

Mo phong robot tu tim duong trong me cung bang thuat toan **A\*** — bai tap ung dung mon **Lap trinh song song**.

---

## Muc luc

1. [Gioi thieu](#gioi-thieu)
2. [Thuat toan A*](#thuat-toan-a)
3. [Yeu cau cai dat](#yeu-cau-cai-dat)
4. [Cach chay](#cach-chay)
5. [Huong dan su dung](#huong-dan-su-dung)
6. [Cau truc du an](#cau-truc-du-an)

---

## Gioi thieu

**Micromouse** la cuoc thi robot tu hanh quoc te: mot robot nho duoc dat vao goc me cung va phai tu tim duong den trung tam ma **khong biet truoc ban do**.

Du an nay mo phong qua trinh do voi cac tinh nang:

- Me cung ngau nhien kich thuoc **a x b** (tuy chinh tu 1 den 100)
- Robot dung **Online A\*** — lap ke hoach lai moi buoc khi phat hien tuong moi
- Giao dien do hoa truc quan (Python + Tkinter, **khong can cai them thu vien**)
- Tuy chinh ban do hoan toan: ve hinh, xoa tuong, dat dich bat ky

---

## Thuat toan A*

### A* la gi?

A* (doc la "A-star") la thuat toan tim duong ngan nhat tren do thi. No ket hop:

- **Chi phi thuc te** tu diem xuat phat den o hien tai: `g(n)`
- **Uoc luong** khoang cach tu o hien tai den dich: `h(n)` (heuristic)

O co gia tri `f(n)` nho nhat se duoc mo rong tiep theo:

```
f(n) = g(n) + h(n)
         |         |
   Chi phi da di   Uoc luong con lai
   (chinh xac)     (Manhattan distance)
```

### Heuristic su dung

```
h(x, y) = |x - x_dich| + |y - y_dich|   <-- Khoang cach Manhattan
```

Heuristic nay **admissible** (khong uoc luong thua) vi robot chi di duoc 4 huong
(Bac / Nam / Dong / Tay), khong di cheo.

### Online A* (A* thoi gian thuc)

Robot **khong biet truoc** vi tri cac tuong. Moi buoc robot thuc hien:

```
1. Cam bien tuong xung quanh o hien tai
2. Cap nhat ban do da biet
3. Chay A* tu vi tri hien tai -> dich
   (tuong chua biet = coi nhu khong co, tuc la "lac quan")
4. Di chuyen 1 buoc theo duong A* vua tim
5. Lap lai tu buoc 1
```

Neu phat hien tuong chan duong da len ke hoach -> A* tu **replanning** ngay.

### Do phuc tap

| | Gia tri |
|---|---|
| Thoi gian | O(b^d) voi b = so nhanh, d = do sau |
| Khong gian | O(b^d) |
| Toi uu? | Co (neu heuristic admissible) |

---

## Yeu cau cai dat

| Yeu cau | Chi tiet |
|---------|---------|
| **Python** | 3.7 tro len |
| **Tkinter** | Co san trong Python (khong can cai them) |
| He dieu hanh | Windows / macOS / Linux |

Kiem tra Python:
```bash
python --version
```

---

## Cach chay

```bash
# Clone repo ve may
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>

# Chay simulator
python maze_astar.py
```

**Khong can cai bat ky thu vien nao them.** Tkinter co san trong Python.

---

## Huong dan su dung

### Giao dien chinh

```
[ Rong(a) ] [ Cao(b) ] [ Do mo(%) ] [ Hinh ]
[ Generate Maze ] [ Run A* ] [ Stop ] [ Ve: TAT ] [ Reset shape ] [ Xoa dich ] [ Toc do ]
Trang thai: ...
[ Legend mau sac ]
+------------------------------------------+
|                                          |
|          Ban do me cung                  |
|                                          |
+------------------------------------------+
```

### Cac buoc co ban

1. Nhap kich thuoc **Rong(a)** va **Cao(b)** — tu 1 den 100
2. Chon **Do mo** (0% = maze day tuong, 80% = nhieu vung thong thoang)
3. Nhan **Generate Maze** → me cung ngau nhien xuat hien
4. *(Tuy chon)* Click vao o bat ky de dat dich (cham do). Mac dinh = trung tam
5. Nhan **Run A\*** → robot (tron xanh) tu tim duong

### Bang mau

| Mau | Y nghia |
|-----|---------|
| Xanh nhat (cyan) | O robot da di qua |
| Vang | Duong A* dang len ke hoach |
| Xanh la nhat | O xuat phat |
| Cham do | O dich |
| Xanh la dam | Dich da den |
| Xam | Vung khong ton tai |

### Tuy chinh ban do

| Thao tac | Chuc nang |
|----------|-----------|
| Click trai vao **canh o** | Xoa / them lai tuong do |
| Click trai vao **giua o** | Dat dich tai o do |
| Click phai | Xoa dich (ve mac dinh trung tam) |
| Nut "Ve: BAT" + keo chuot trai | Them o vao ban do |
| Nut "Ve: BAT" + keo chuot phai | Xoa o khoi ban do |
| Dropdown "Hinh" | Chon hinh dang co san |
| Nut Reset shape | Ve hinh chu nhat day du |

### Hinh dang co san

| Ten | Mo ta |
|-----|-------|
| Chu nhat (day du) | Binh thuong |
| Bo goc tren-phai | Cat goc phan tu tren-phai |
| Bo 4 goc | Cat 4 goc |
| Hinh L | Hinh chu L |
| Hinh T | Hinh chu T |
| Hinh U | Hinh chu U |
| Hinh chu thap (+) | Hinh dau cong |

---

## Cau truc du an

```
repo/
 |
 +-- maze_astar.py        <-- FILE CHINH: chay cai nay de demo
 +-- README.md            <-- File nay
 |
 +-- astar/               <-- Thuat toan A* viet bang C++ (danh cho MMS goc)
 |    +-- main.cpp
 |    +-- Makefile
 |    +-- build.bat
 |
 +-- src/                 <-- MMS Simulator goc (Qt C++) -- khong can cho demo Python
      +-- Maze.cpp / Maze.h     (da them fromGenerated() sinh maze ngau nhien)
      +-- Window.cpp / Window.h (da them UI nhap kich thuoc + nut Generate)
      +-- ...
```

> **Chi can file `maze_astar.py` de chay demo.**
> Thu muc `src/` va `astar/` la phan mo rong cho MMS simulator goc (can cai Qt de build).

---

## Lien quan den Lap trinh song song

Du an nay la phan **mo phong don luong** (single-thread) de demo thuat toan A* trong
bai toan robot tu hanh. Trong nhom, cac thanh vien khac ap dung **multi-threading**
de song song hoa qua trinh tim kiem A* tren nhieu robot hoac nhieu huong tim kiem
dong thoi.

---

## Nguon tham khao

- [MMS - Micromouse Simulator (goc)](https://github.com/mackorone/mms)
- [A* Search Algorithm - Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths*
