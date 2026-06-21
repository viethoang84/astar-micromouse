"""
ui.py  –  Giao dien Python (Tkinter)
Khoi dong: python ui.py
Giao tiep voi thuat toan C++ qua stdin/stdout (giao thuc MMS).
"""
import tkinter as tk
from tkinter import ttk
import random, subprocess, threading, time, os

# ── Huong di ──────────────────────────────────────────────────────────────────
DIR_X = [0, 1, 0, -1]   # N E S W
DIR_Y = [1, 0, -1,  0]
OPP   = [2, 3, 0,   1]

# ── Mau giao dien ─────────────────────────────────────────────────────────────
C_INACTIVE = "#999999"
C_CELL     = "#ffffff"
C_VISITED  = "#88ccff"
C_PATH     = "#ffdd44"
C_START    = "#88ff88"
C_GOAL_BG  = "#ffaaaa"
C_DONE     = "#00bb44"
C_ROBOT    = "#0055ff"
C_WALL     = "#111111"

# Map ma mau MMS (C++ gui) sang hex Tkinter
MMS_COLORS = {
    'k': '#000000', 'b': '#4444ff', 'a': '#888888', 'c': '#88ccff',
    'g': '#88ff88', 'o': '#ff8800', 'r': '#ff4444', 'w': '#ffffff',
    'y': '#ffdd44', 'B': '#000088', 'C': '#008888', 'A': '#444444',
    'G': '#00bb44', 'R': '#880000', 'Y': '#888800',
}

PRESETS = {
    "Chu nhat (day du)": "full",
    "Bo goc tren-phai" : "cut_tr",
    "Bo 4 goc"         : "cut_4c",
    "Hinh L"           : "shape_l",
    "Hinh T"           : "shape_t",
    "Hinh U"           : "shape_u",
    "Hinh chu thap (+)": "shape_plus",
}

EXE_CANDIDATES = [
    "algorithm/astar.exe", "algorithm/astar",
    "astar/astar.exe",     "astar/astar",
]


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Micromouse  |  UI: Python  |  Algorithm: C++")
        self.root.resizable(True, True)

        # Kich thuoc ban do
        self.W, self.H = 16, 16
        self.aW, self.aH = 16, 16

        # Du lieu ban do
        self.walls  = None   # walls[x][y][d]
        self.active = None   # active[x][y]

        # Trang thai robot (Python theo doi de tra loi cam bien)
        self.rx, self.ry  = 0, 0
        self.rdir         = 0   # 0=N 1=E 2=S 3=W
        self.start_pos    = (0, 0)

        # Dich
        self.goal = None   # None = trung tam; (x,y) = tuy chinh

        # Hien thi
        self.cc = {}       # cell overlay color
        self.running  = False
        self.step_id  = None
        self.steps    = 0

        # Che do tuong tac (None | "draw" | "wall" | "goal")
        self.mode       = None
        self.draw_value = True

        # Subprocess C++
        self._proc = None

        self._build_ui()
        self.root.after(100, self._init_default)

    # ── Giao dien ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        def mkbtn(p, text, cmd, bg="#dddddd", fg="black"):
            tk.Button(p, text=text, command=cmd, bg=bg, fg=fg,
                      font=("Arial", 10), padx=5).pack(side=tk.LEFT, padx=2)

        r1 = tk.Frame(self.root, pady=3)
        r1.pack(side=tk.TOP, fill=tk.X, padx=6)
        tk.Label(r1, text="Rong(a):", font=("Arial", 10)).pack(side=tk.LEFT)
        self.w_var = tk.IntVar(value=16)
        tk.Spinbox(r1, from_=1, to=100, textvariable=self.w_var,
                   width=4, font=("Arial", 10)).pack(side=tk.LEFT, padx=(1, 6))
        tk.Label(r1, text="Cao(b):",  font=("Arial", 10)).pack(side=tk.LEFT)
        self.h_var = tk.IntVar(value=16)
        tk.Spinbox(r1, from_=1, to=100, textvariable=self.h_var,
                   width=4, font=("Arial", 10)).pack(side=tk.LEFT, padx=(1, 8))
        tk.Label(r1, text="Do mo(%):", font=("Arial", 10)).pack(side=tk.LEFT)
        self.open_var = tk.IntVar(value=20)
        tk.Scale(r1, from_=0, to=80, orient=tk.HORIZONTAL,
                 variable=self.open_var, length=110,
                 showvalue=True, font=("Arial", 9)).pack(side=tk.LEFT, padx=(1, 8))
        tk.Label(r1, text="Hinh:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.preset_var = tk.StringVar(value="Chu nhat (day du)")
        cb = ttk.Combobox(r1, textvariable=self.preset_var,
                          values=list(PRESETS.keys()), width=18,
                          font=("Arial", 10), state="readonly")
        cb.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", lambda _: self._apply_preset())

        r2 = tk.Frame(self.root, pady=3)
        r2.pack(side=tk.TOP, fill=tk.X, padx=6)
        mkbtn(r2, "Generate Maze", self.generate_maze, "#4caf50", "white")
        mkbtn(r2, "Run A*",        self.run_astar,     "#2196f3", "white")
        mkbtn(r2, "Stop",          self.stop,           "#f44336", "white")
        tk.Label(r2, text=" |", font=("Arial", 10), fg="#aaaaaa").pack(side=tk.LEFT)
        self.mode_btns = {}
        for mode_key, label in [("draw", "Ve map"), ("wall", "Them/Xoa tuong"), ("goal", "Chon dich")]:
            btn = tk.Button(r2, text=label, font=("Arial", 10),
                            bg="#aaaaaa", fg="white", padx=5,
                            command=lambda k=mode_key: self.toggle_mode(k))
            btn.pack(side=tk.LEFT, padx=2)
            self.mode_btns[mode_key] = btn
        tk.Label(r2, text=" |", font=("Arial", 10), fg="#aaaaaa").pack(side=tk.LEFT)
        mkbtn(r2, "Reset shape", self.reset_shape)
        mkbtn(r2, "Xoa dich",    self.clear_goal)
        tk.Label(r2, text="  Toc do:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=80)
        tk.Scale(r2, from_=1, to=200, orient=tk.HORIZONTAL,
                 variable=self.speed_var, length=120,
                 showvalue=False).pack(side=tk.LEFT)

        r3 = tk.Frame(self.root)
        r3.pack(side=tk.TOP, fill=tk.X, padx=6)
        self.sv = tk.StringVar(value="Nhan Generate Maze.")
        tk.Label(r3, textvariable=self.sv, font=("Arial", 10),
                 fg="#333333", anchor="w").pack(fill=tk.X)

        r4 = tk.Frame(self.root)
        r4.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(0, 2))
        for color, label in [
            (C_START, "Xuat phat"), (C_GOAL_BG, "Dich"),
            (C_VISITED, "Da di qua"), (C_PATH, "Duong A*"),
            (C_DONE, "Da den dich"), (C_INACTIVE, "Khong ton tai"),
        ]:
            tk.Label(r4, bg=color, width=2).pack(side=tk.LEFT, padx=(4, 1))
            tk.Label(r4, text=label, font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 6))

        self.canvas = tk.Canvas(self.root, bg="#aaaaaa", width=680, height=560)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        self.canvas.bind("<Button-1>",  self._lclick)
        self.canvas.bind("<B1-Motion>", self._ldrag)
        self.canvas.bind("<Button-3>",  self._rclick)
        self.canvas.bind("<B3-Motion>", self._rdrag)
        self.canvas.bind("<Configure>", lambda _: self._draw())

    # ── Khoi tao ──────────────────────────────────────────────────────────────

    def _init_default(self):
        self.W = self.aW = self.w_var.get()
        self.H = self.aH = self.h_var.get()
        self.active = [[True] * self.H for _ in range(self.W)]
        self.generate_maze()

    def _cs(self):
        cw = self.canvas.winfo_width()  or 680
        ch = self.canvas.winfo_height() or 560
        return max(4, min(cw // max(1, self.W), ch // max(1, self.H)))

    def _p2c(self, px, py):
        cs = self._cs()
        return px // cs, self.H - 1 - py // cs

    def _valid(self, x, y):
        return 0 <= x < self.W and 0 <= y < self.H

    # ── Chuot ─────────────────────────────────────────────────────────────────

    def _wall_hit(self, px, py):
        cs  = self._cs()
        lx, ly = px % cs, py % cs
        thr = max(3, cs // 4)
        dists = [ly, cs - lx, cs - ly, lx]
        md = min(dists)
        return dists.index(md) if md < thr else None

    def _toggle_wall(self, x, y, d):
        if self.walls is None: return
        nx, ny = x + DIR_X[d], y + DIR_Y[d]
        if not (self._valid(nx, ny) and self.active[x][y] and self.active[nx][ny]):
            return
        v = not self.walls[x][y][d]
        self.walls[x][y][d] = v
        self.walls[nx][ny][OPP[d]] = v
        self.sv.set(f"{'Them' if v else 'Xoa'} tuong ({x},{y}) huong {'NESW'[d]}")
        self._draw()

    def _lclick(self, e):
        x, y = self._p2c(e.x, e.y)
        if not self._valid(x, y): return
        if self.mode == "draw":
            self.draw_value = not self.active[x][y]
            self.active[x][y] = self.draw_value
            self._draw()
        elif self.mode == "wall":
            wd = self._wall_hit(e.x, e.y)
            if wd is not None:
                self._toggle_wall(x, y, wd)
        elif self.mode == "goal":
            if self.active[x][y]:
                self.goal = (x, y)
                self.sv.set(f"Dich: ({x},{y}). Nhan Run A*.")
                self._draw()

    def _ldrag(self, e):
        x, y = self._p2c(e.x, e.y)
        if self._valid(x, y) and self.mode == "draw":
            self.active[x][y] = self.draw_value
            self._draw()

    def _rclick(self, e):
        x, y = self._p2c(e.x, e.y)
        if not self._valid(x, y): return
        if self.mode == "draw":
            self.draw_value = False
            self.active[x][y] = False
            self._draw()
        elif self.mode == "goal":
            self.clear_goal()

    def _rdrag(self, e):
        x, y = self._p2c(e.x, e.y)
        if self._valid(x, y) and self.mode == "draw":
            self.active[x][y] = False
            self._draw()

    # ── Preset hinh dang ──────────────────────────────────────────────────────

    def _apply_preset(self):
        key  = PRESETS[self.preset_var.get()]
        W, H = self.w_var.get(), self.h_var.get()
        act  = [[True] * H for _ in range(W)]
        if key == "cut_tr":
            for x in range(W//2, W):
                for y in range(H//2, H): act[x][y] = False
        elif key == "cut_4c":
            qw, qh = max(1, W//4), max(1, H//4)
            for x in range(W):
                for y in range(H):
                    if (x < qw or x >= W-qw) and (y < qh or y >= H-qh):
                        act[x][y] = False
        elif key == "shape_l":
            for x in range(W):
                for y in range(H):
                    if x >= W//4 and y >= H//4: act[x][y] = False
        elif key == "shape_t":
            for x in range(W):
                for y in range(H):
                    if not (y >= H*3//4 or W//3 <= x < 2*W//3):
                        act[x][y] = False
        elif key == "shape_u":
            for x in range(W):
                for y in range(H):
                    if not (x < W//4 or x >= 3*W//4 or y < H//4):
                        act[x][y] = False
        elif key == "shape_plus":
            for x in range(W):
                for y in range(H):
                    if not (W//3 <= x < 2*W//3 or H//3 <= y < 2*H//3):
                        act[x][y] = False
        self.W = self.aW = W
        self.H = self.aH = H
        self.active = act
        self.goal = None
        self.generate_maze()

    def reset_shape(self):
        W, H = self.w_var.get(), self.h_var.get()
        self.W = self.aW = W
        self.H = self.aH = H
        self.active = [[True] * H for _ in range(W)]
        self.goal = None
        self.generate_maze()

    def toggle_mode(self, name):
        self.mode = None if self.mode == name else name
        hints = {
            "draw": "CHE DO VE MAP | Keo-TRAI=them o | Keo-PHAI=xoa o | Nhan Generate Maze sau khi ve.",
            "wall": "CHE DO TUONG | Click gan canh o de them/xoa tuong.",
            "goal": "CHE DO DICH | Click vao o bat ky de dat dich | Phai-click=xoa dich.",
        }
        self.sv.set(hints.get(self.mode, "Tat ca che do dang TAT. Chon 1 che do de thao tac."))
        for k, btn in self.mode_btns.items():
            btn.config(bg="#ff8800" if k == self.mode else "#aaaaaa")

    def clear_goal(self):
        self.goal = None
        self.sv.set("Da xoa dich. A* se tim den trung tam.")
        self._draw()

    # ── Sinh maze ─────────────────────────────────────────────────────────────

    def generate_maze(self):
        self.stop()
        W_new, H_new = self.w_var.get(), self.h_var.get()
        if self.active is None or self.aW != W_new or self.aH != H_new:
            self.aW, self.aH = W_new, H_new
            self.active = [[True] * H_new for _ in range(W_new)]
        self.W, self.H = W_new, H_new
        W, H = self.W, self.H

        self.walls = [[[True] * 4 for _ in range(H)] for _ in range(W)]

        visited = [[False] * H for _ in range(W)]
        start   = self._find_start()
        if start:
            stk = [start]
            visited[start[0]][start[1]] = True
            while stk:
                x, y = stk[-1]
                nbrs = [(d, x+DIR_X[d], y+DIR_Y[d]) for d in range(4)
                        if 0<=x+DIR_X[d]<W and 0<=y+DIR_Y[d]<H
                        and self.active[x+DIR_X[d]][y+DIR_Y[d]]
                        and not visited[x+DIR_X[d]][y+DIR_Y[d]]]
                if not nbrs:
                    stk.pop()
                else:
                    d, nx, ny = random.choice(nbrs)
                    self.walls[x][y][d] = False
                    self.walls[nx][ny][OPP[d]] = False
                    visited[nx][ny] = True
                    stk.append((nx, ny))

        op = self.open_var.get() / 100.0
        if op > 0:
            for x in range(W):
                for y in range(H):
                    if not self.active[x][y]: continue
                    for d in [0, 1]:
                        nx, ny = x+DIR_X[d], y+DIR_Y[d]
                        if (0<=nx<W and 0<=ny<H and self.active[nx][ny]
                                and self.walls[x][y][d]
                                and random.random() < op):
                            self.walls[x][y][d] = False
                            self.walls[nx][ny][OPP[d]] = False

        self.rx, self.ry = (start if start else (0, 0))
        self.rdir = 0
        self.cc = {}
        self.steps = 0
        self.sv.set(f"Map {W}x{H} da tao. Click o de dat dich, nhan Run A*.")
        self._draw()

    def _find_start(self):
        for y in range(self.H):
            for x in range(self.W):
                if self.active[x][y]:
                    return (x, y)
        return None

    # ── Muc tieu ──────────────────────────────────────────────────────────────

    def _gcells(self):
        if self.goal is not None:
            return {self.goal}
        W, H = self.W, self.H
        cells = {((W-1)//2, (H-1)//2)}
        if W%2==0: cells.add((W//2, (H-1)//2))
        if H%2==0: cells.add(((W-1)//2, H//2))
        if W%2==0 and H%2==0: cells.add((W//2, H//2))
        return cells

    def _primary_goal(self):
        """O dich chinh (1 o duy nhat) de gui cho C++."""
        if self.goal:
            return self.goal
        return ((self.W-1)//2, (self.H-1)//2)

    def _is_goal(self, x, y):
        return (x, y) in self._gcells()

    # ── Ve ────────────────────────────────────────────────────────────────────

    def _draw(self):
        if self.walls is None or self.active is None: return
        self.canvas.delete("all")
        W, H = self.W, self.H
        cs   = self._cs()
        lw   = max(1, cs // 8)
        goals = self._gcells()

        for x in range(W):
            for y in range(H):
                px = x * cs
                py = (H-1-y) * cs
                if not self.active[x][y]:
                    fill = C_INACTIVE
                elif (x, y) in self.cc:
                    fill = self.cc[(x, y)]
                elif (x, y) in goals and self.goal is None:
                    fill = C_GOAL_BG
                else:
                    fill = C_CELL
                self.canvas.create_rectangle(px, py, px+cs, py+cs,
                                             fill=fill, outline="")
                if not self.active[x][y]: continue
                if self.walls[x][y][0]:
                    self.canvas.create_line(px, py, px+cs, py,
                                            fill=C_WALL, width=lw)
                if self.walls[x][y][1]:
                    self.canvas.create_line(px+cs, py, px+cs, py+cs,
                                            fill=C_WALL, width=lw)
                if self.walls[x][y][2]:
                    self.canvas.create_line(px, py+cs, px+cs, py+cs,
                                            fill=C_WALL, width=lw)
                if self.walls[x][y][3]:
                    self.canvas.create_line(px, py, px, py+cs,
                                            fill=C_WALL, width=lw)

        for gx, gy in goals:
            if self._valid(gx, gy) and self.active[gx][gy]:
                gpx = gx*cs + cs//2
                gpy = (H-1-gy)*cs + cs//2
                r   = max(3, cs//3)
                self.canvas.create_oval(gpx-r, gpy-r, gpx+r, gpy+r,
                                        fill="red", outline="#880000",
                                        width=max(1, lw))

        rpx = self.rx*cs + cs//2
        rpy = (H-1-self.ry)*cs + cs//2
        r   = max(2, cs//3)
        self.canvas.create_oval(rpx-r, rpy-r, rpx+r, rpy+r,
                                fill=C_ROBOT, outline="#003399",
                                width=max(1, cs//8))
        self.canvas.update_idletasks()

    # ── Chay A* (giao tiep voi C++) ───────────────────────────────────────────

    def run_astar(self):
        if self.walls is None:
            self.sv.set("Hay nhan Generate Maze truoc!"); return
        if self.running: return

        exe = next((p for p in EXE_CANDIDATES if os.path.exists(p)), None)
        if exe is None:
            self.sv.set(
                "Khong tim thay file thuc thi C++! "
                "Vao thu muc 'algorithm/' va chay build.bat truoc."
            ); return

        start = self._find_start()
        if not start: return

        self.running   = True
        self.steps     = 0
        self.rx, self.ry = start
        self.rdir      = 0
        self.start_pos = start
        self.cc        = {}
        self.cc[start] = C_START
        for gx, gy in self._gcells():
            self.cc[(gx, gy)] = C_GOAL_BG
        self._draw()

        try:
            self._proc = subprocess.Popen(
                [exe],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True, bufsize=1
            )
        except Exception as ex:
            self.running = False
            self.sv.set(f"Loi khoi dong C++: {ex}"); return

        threading.Thread(target=self._protocol_loop, daemon=True).start()

    def _protocol_loop(self):
        """Thread phu: doc lenh tu C++ va tra loi."""
        try:
            for raw in self._proc.stdout:
                if not self.running: break
                resp = self._handle(raw.strip())
                if resp is not None:
                    self._proc.stdin.write(resp + "\n")
                    self._proc.stdin.flush()
        except Exception:
            pass
        finally:
            self.running = False
            self.root.after(0, self._draw)

    def _wall_in_dir(self, d):
        """Co tuong theo huong d khong? True neu: co tuong thuc su, hoac o ke inactive/ngoai ban do."""
        nx, ny = self.rx + DIR_X[d], self.ry + DIR_Y[d]
        if not self._valid(nx, ny) or not self.active[nx][ny]:
            return True
        return self.walls[self.rx][self.ry][d]

    def _handle(self, cmd: str):
        """Xu ly 1 dong lenh tu C++. Tra ve chuoi phan hoi hoac None."""
        if not cmd: return None
        p  = cmd.split()
        op = p[0]

        # --- Truy van thong tin ban do ---
        if op == "mazeWidth":  return str(self.W)
        if op == "mazeHeight": return str(self.H)
        if op == "goalX":      return str(self._primary_goal()[0])
        if op == "goalY":      return str(self._primary_goal()[1])
        if op == "wasReset":   return "false"

        # --- Cam bien tuong (dua tren huong robot hien tai) ---
        if op == "wallFront":
            return "true" if self._wall_in_dir(self.rdir) else "false"
        if op == "wallLeft":
            return "true" if self._wall_in_dir((self.rdir+3)%4) else "false"
        if op == "wallRight":
            return "true" if self._wall_in_dir((self.rdir+1)%4) else "false"
        if op == "wallBack":
            return "true" if self._wall_in_dir((self.rdir+2)%4) else "false"

        # --- Dieu khien chuyen dong ---
        if op == "moveForward":
            if self._wall_in_dir(self.rdir):
                return "crash"
            self.rx += DIR_X[self.rdir]
            self.ry += DIR_Y[self.rdir]
            self.steps += 1
            self.root.after(0, self._on_move)
            delay = max(0.005, (210 - self.speed_var.get()) / 1000.0)
            time.sleep(delay)
            return ""

        if op in ("turnLeft", "turnLeft90"):
            self.rdir = (self.rdir + 3) % 4; return ""
        if op in ("turnRight", "turnRight90"):
            self.rdir = (self.rdir + 1) % 4; return ""

        # --- Lenh hien thi (khong co phan hoi) ---
        if op == "setColor" and len(p) >= 4:
            try:
                x, y, c = int(p[1]), int(p[2]), p[3]
                col = MMS_COLORS.get(c)
                if col and self._valid(x, y):
                    self.cc[(x, y)] = col
            except Exception: pass
            return None

        if op == "clearAllColor":
            self.cc.clear(); return None

        # setWall, clearWall, setText, ... : Python tu quan ly, bo qua
        return None

    def _on_move(self):
        """Goi tren main thread sau moi buoc di chuyen."""
        if self._is_goal(self.rx, self.ry):
            self.cc[(self.rx, self.ry)] = C_DONE
            self.sv.set(f"HOAN THANH! Den dich sau {self.steps} buoc.")
            self.running = False
        else:
            self.sv.set(f"Buoc {self.steps} | Vi tri ({self.rx},{self.ry})")
        self._draw()

    def stop(self):
        self.running = False
        if self._proc:
            try: self._proc.terminate()
            except Exception: pass
            self._proc = None
        if self.step_id:
            self.root.after_cancel(self.step_id)
            self.step_id = None


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x780")
    MazeApp(root)
    root.mainloop()
