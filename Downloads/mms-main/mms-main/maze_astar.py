"""
A* Micromouse Simulator v2 - Python + Tkinter
Chay: python maze_astar.py
"""
import tkinter as tk
from tkinter import ttk
import random, heapq

DIR_X = [0, 1, 0, -1]
DIR_Y = [1, 0, -1,  0]
OPP   = [2, 3, 0,   1]

C_INACTIVE = "#999999"
C_CELL     = "#ffffff"
C_VISITED  = "#88ccff"
C_PATH     = "#ffdd44"
C_START    = "#88ff88"
C_GOAL_BG  = "#ffaaaa"
C_DONE     = "#00bb44"
C_ROBOT    = "#0055ff"
C_WALL     = "#111111"

PRESETS = {
    "Chu nhat (day du)": "full",
    "Bo goc tren-phai" : "cut_tr",
    "Bo 4 goc"         : "cut_4c",
    "Hinh L"           : "shape_l",
    "Hinh T"           : "shape_t",
    "Hinh U"           : "shape_u",
    "Hinh chu thap (+)": "shape_plus",
}


class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* Micromouse – Map tuy chinh v2")
        self.root.resizable(True, True)

        self.W, self.H   = 16, 16
        self.aW, self.aH = 16, 16   # dimensions of current active array

        self.walls      = None
        self.active     = None
        self.wall_known = None

        self.rx, self.ry  = 0, 0
        self.start_pos    = (0, 0)
        self.goal         = None   # None=center, (x,y)=custom

        self.cc       = {}         # cell overlay colors
        self.running  = False
        self.step_id  = None
        self.steps    = 0

        self.draw_mode  = False
        self.draw_value = True

        self._build_ui()
        self.root.after(100, self._init_default)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        def mkbtn(parent, text, cmd, bg="#dddddd", fg="black"):
            tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                      font=("Arial", 10), padx=5).pack(side=tk.LEFT, padx=2)

        # Row 1: dimensions + openness + preset shape
        r1 = tk.Frame(self.root, pady=3)
        r1.pack(side=tk.TOP, fill=tk.X, padx=6)

        tk.Label(r1, text="Rong(a):", font=("Arial", 10)).pack(side=tk.LEFT)
        self.w_var = tk.IntVar(value=16)
        tk.Spinbox(r1, from_=1, to=100, textvariable=self.w_var,
                   width=4, font=("Arial", 10)).pack(side=tk.LEFT, padx=(1, 6))

        tk.Label(r1, text="Cao(b):", font=("Arial", 10)).pack(side=tk.LEFT)
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
        cb.pack(side=tk.LEFT, padx=(1, 0))
        cb.bind("<<ComboboxSelected>>", lambda _: self._apply_preset())

        # Row 2: action buttons + speed
        r2 = tk.Frame(self.root, pady=3)
        r2.pack(side=tk.TOP, fill=tk.X, padx=6)

        mkbtn(r2, "Generate Maze", self.generate_maze, "#4caf50", "white")
        mkbtn(r2, "Run A*",        self.run_astar,     "#2196f3", "white")
        mkbtn(r2, "Stop",          self.stop,           "#f44336", "white")

        self.draw_btn = tk.Button(r2, text="Ve: TAT", font=("Arial", 10),
                                  bg="#aaaaaa", fg="white", padx=5,
                                  command=self.toggle_draw)
        self.draw_btn.pack(side=tk.LEFT, padx=2)

        mkbtn(r2, "Reset shape", self.reset_shape)
        mkbtn(r2, "Xoa dich",    self.clear_goal)

        tk.Label(r2, text="  Toc do:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=80)
        tk.Scale(r2, from_=1, to=200, orient=tk.HORIZONTAL,
                 variable=self.speed_var, length=120,
                 showvalue=False).pack(side=tk.LEFT)


        # Status bar
        r3 = tk.Frame(self.root)
        r3.pack(side=tk.TOP, fill=tk.X, padx=6)
        self.sv = tk.StringVar(value="Nhan Generate Maze de bat dau.")
        tk.Label(r3, textvariable=self.sv, font=("Arial", 10),
                 fg="#333333", anchor="w").pack(fill=tk.X)

        # Legend
        r4 = tk.Frame(self.root)
        r4.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(0, 2))
        for color, label in [
            (C_START, "Xuat phat"), (C_GOAL_BG, "Dich"),
            (C_VISITED, "Da di qua"), (C_PATH, "Duong A*"),
            (C_DONE, "Da den dich"), (C_INACTIVE, "Vung khong ton tai"),
        ]:
            tk.Label(r4, bg=color, width=2).pack(side=tk.LEFT, padx=(4, 1))
            tk.Label(r4, text=label, font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 6))

        # Canvas
        self.canvas = tk.Canvas(self.root, bg="#aaaaaa", width=680, height=560)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        self.canvas.bind("<Button-1>",  self._lclick)
        self.canvas.bind("<B1-Motion>", self._ldrag)
        self.canvas.bind("<Button-3>",  self._rclick)
        self.canvas.bind("<B3-Motion>", self._rdrag)
        self.canvas.bind("<Configure>", lambda _: self._draw())

    # ── Helpers ───────────────────────────────────────────────────────────────

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

    # ── Mouse events ──────────────────────────────────────────────────────────

    def _wall_hit(self, px, py):
        """Tra ve huong tuong (0=N,1=E,2=S,3=W) neu click gan tuong, nguoc lai None."""
        cs  = self._cs()
        lx  = px % cs          # vi tri ngang trong o (0=Tay, cs=Dong)
        ly  = py % cs          # vi tri doc trong o   (0=Bac, cs=Nam)
        thr = max(3, cs // 4)  # nguong phat hien (1/4 chieu rong o)
        # Khoang cach den 4 canh tuong: Bac, Dong, Nam, Tay
        dists = [ly, cs - lx, cs - ly, lx]
        min_d = min(dists)
        return dists.index(min_d) if min_d < thr else None

    def _toggle_wall(self, x, y, d):
        """Bat/tat tuong giua (x,y) va hang xom theo huong d (chi tuong noi that)."""
        if self.walls is None:
            return
        W, H = self.W, self.H
        nx, ny = x + DIR_X[d], y + DIR_Y[d]
        # Chi xoa tuong giua 2 o hoat dong (khong xoa bien gioi)
        if not (0 <= nx < W and 0 <= ny < H):
            return
        if not self.active[x][y] or not self.active[nx][ny]:
            return
        new_val = not self.walls[x][y][d]
        self.walls[x][y][d]        = new_val
        self.walls[nx][ny][OPP[d]] = new_val
        action = "Them" if new_val else "Xoa"
        self.sv.set(f"{action} tuong tai ({x},{y}) huong {'NESW'[d]}. Click vao o de dat dich.")
        self._draw()

    def _lclick(self, e):
        x, y = self._p2c(e.x, e.y)
        if not self._valid(x, y):
            return
        if self.draw_mode:
            self.draw_value = not self.active[x][y]
            self.active[x][y] = self.draw_value
            self._draw()
        else:
            # Neu click gan canh tuong -> bat/tat tuong do
            wall_dir = self._wall_hit(e.x, e.y)
            if wall_dir is not None:
                self._toggle_wall(x, y, wall_dir)
            elif self.active[x][y]:
                self.goal = (x, y)
                self.sv.set(f"Dich dat tai ({x},{y}). Nhan Run A*.")
                self._draw()

    def _ldrag(self, e):
        x, y = self._p2c(e.x, e.y)
        if self._valid(x, y) and self.draw_mode:
            self.active[x][y] = self.draw_value
            self._draw()

    def _rclick(self, e):
        x, y = self._p2c(e.x, e.y)
        if not self._valid(x, y):
            return
        if self.draw_mode:
            self.draw_value = False
            self.active[x][y] = False
            self._draw()
        else:
            self.clear_goal()

    def _rdrag(self, e):
        x, y = self._p2c(e.x, e.y)
        if self._valid(x, y) and self.draw_mode:
            self.active[x][y] = False
            self._draw()

    # ── Shape presets ─────────────────────────────────────────────────────────

    def _apply_preset(self):
        key  = PRESETS[self.preset_var.get()]
        W, H = self.w_var.get(), self.h_var.get()
        act  = [[True] * H for _ in range(W)]

        if key == "cut_tr":
            for x in range(W // 2, W):
                for y in range(H // 2, H):
                    act[x][y] = False

        elif key == "cut_4c":
            qw, qh = max(1, W // 4), max(1, H // 4)
            for x in range(W):
                for y in range(H):
                    if (x < qw or x >= W - qw) and (y < qh or y >= H - qh):
                        act[x][y] = False

        elif key == "shape_l":
            # L: cot trai + day duoi
            for x in range(W):
                for y in range(H):
                    if x >= W // 4 and y >= H // 4:
                        act[x][y] = False

        elif key == "shape_t":
            # T: thanh ngang tren + cot doc giua
            for x in range(W):
                for y in range(H):
                    in_bar  = y >= H * 3 // 4
                    in_stem = W // 3 <= x < 2 * W // 3
                    if not in_bar and not in_stem:
                        act[x][y] = False

        elif key == "shape_u":
            # U: 2 canh ben + day duoi
            for x in range(W):
                for y in range(H):
                    in_left   = x < W // 4
                    in_right  = x >= 3 * W // 4
                    in_bottom = y < H // 4
                    if not in_left and not in_right and not in_bottom:
                        act[x][y] = False

        elif key == "shape_plus":
            for x in range(W):
                for y in range(H):
                    in_h = W // 3 <= x < 2 * W // 3
                    in_v = H // 3 <= y < 2 * H // 3
                    if not in_h and not in_v:
                        act[x][y] = False

        self.W = self.aW = W
        self.H = self.aH = H
        self.active = act
        self.goal   = None
        self.generate_maze()

    def reset_shape(self):
        W, H = self.w_var.get(), self.h_var.get()
        self.W = self.aW = W
        self.H = self.aH = H
        self.active = [[True] * H for _ in range(W)]
        self.goal = None
        self.generate_maze()

    def toggle_draw(self):
        self.draw_mode = not self.draw_mode
        if self.draw_mode:
            self.draw_btn.config(text="Ve: BAT", bg="#ff8800")
            self.sv.set("CHE DO VE | Keo-TRAI = them o | Keo-PHAI = xoa o | Nhan Generate Maze sau khi ve.")
        else:
            self.draw_btn.config(text="Ve: TAT", bg="#aaaaaa")
            self.sv.set("Click trai = dat dich (cham do) | Click phai = xoa dich.")

    def clear_goal(self):
        self.goal = None
        self.sv.set("Da xoa dich. A* se tim den trung tam.")
        self._draw()

    # ── Maze generation ───────────────────────────────────────────────────────

    def generate_maze(self):
        self.stop()
        W_new, H_new = self.w_var.get(), self.h_var.get()

        if self.active is None or self.aW != W_new or self.aH != H_new:
            self.aW, self.aH = W_new, H_new
            self.active = [[True] * H_new for _ in range(W_new)]

        self.W, self.H = W_new, H_new
        W, H = self.W, self.H

        # All walls start as present
        self.walls = [[[True] * 4 for _ in range(H)] for _ in range(W)]

        # DFS only on active cells
        visited = [[False] * H for _ in range(W)]
        start   = self._find_start()

        if start:
            stk = [start]
            visited[start[0]][start[1]] = True
            while stk:
                x, y = stk[-1]
                nbrs = []
                for d in range(4):
                    nx, ny = x + DIR_X[d], y + DIR_Y[d]
                    if (0 <= nx < W and 0 <= ny < H
                            and self.active[nx][ny]
                            and not visited[nx][ny]):
                        nbrs.append((d, nx, ny))
                if not nbrs:
                    stk.pop()
                else:
                    d, nx, ny = random.choice(nbrs)
                    self.walls[x][y][d]        = False
                    self.walls[nx][ny][OPP[d]] = False
                    visited[nx][ny] = True
                    stk.append((nx, ny))

        # Open areas: remove extra interior walls to create loops / open plazas
        op = self.open_var.get() / 100.0
        if op > 0:
            for x in range(W):
                for y in range(H):
                    if not self.active[x][y]:
                        continue
                    for d in [0, 1]:   # North and East only (avoid double processing)
                        nx, ny = x + DIR_X[d], y + DIR_Y[d]
                        if (0 <= nx < W and 0 <= ny < H
                                and self.active[nx][ny]
                                and self.walls[x][y][d]
                                and random.random() < op):
                            self.walls[x][y][d]        = False
                            self.walls[nx][ny][OPP[d]] = False

        self.rx, self.ry = (start if start else (0, 0))
        self.cc = {}
        self._init_wk()
        self.steps = 0

        n_active = sum(self.active[x][y] for x in range(W) for y in range(H))
        self.sv.set(
            f"Map {W}×{H} | {n_active} o hoat dong | Do mo {self.open_var.get()}% "
            + ("| Click o bat ki de dat dich." if not self.draw_mode
               else "| Dang ve hinh."))
        self._draw()

    def _find_start(self):
        for y in range(self.H):
            for x in range(self.W):
                if self.active[x][y]:
                    return (x, y)
        return None

    def _init_wk(self):
        W, H = self.W, self.H
        self.wall_known = [[[False] * 4 for _ in range(H)] for _ in range(W)]
        for x in range(W):
            self.wall_known[x][0][2]   = True
            self.wall_known[x][H-1][0] = True
        for y in range(H):
            self.wall_known[0][y][3]   = True
            self.wall_known[W-1][y][1] = True
        # Walls adjacent to inactive cells are known from the start
        for x in range(W):
            for y in range(H):
                if not self.active[x][y]:
                    for d in range(4):
                        self.wall_known[x][y][d] = True
                        nx, ny = x + DIR_X[d], y + DIR_Y[d]
                        if 0 <= nx < W and 0 <= ny < H:
                            self.wall_known[nx][ny][OPP[d]] = True

    # ── Goal ──────────────────────────────────────────────────────────────────

    def _gcells(self):
        if self.goal is not None:
            return {self.goal}
        W, H = self.W, self.H
        cells = {((W-1)//2, (H-1)//2)}
        if W % 2 == 0: cells.add((W//2, (H-1)//2))
        if H % 2 == 0: cells.add(((W-1)//2, H//2))
        if W % 2 == 0 and H % 2 == 0: cells.add((W//2, H//2))
        return cells

    def _is_goal(self, x, y): return (x, y) in self._gcells()

    def _h(self, x, y):
        return min(abs(x-gx) + abs(y-gy) for gx, gy in self._gcells())

    # ── A* ────────────────────────────────────────────────────────────────────

    def _astar(self, sx, sy):
        W, H = self.W, self.H
        openh = [(self._h(sx, sy), 0, sx, sy)]
        gmap  = {(sx, sy): 0}
        came  = {}
        done  = set()

        while openh:
            f, g, x, y = heapq.heappop(openh)
            if (x, y) in done:
                continue
            done.add((x, y))

            if self._is_goal(x, y):
                path, p = [], (x, y)
                while p in came:
                    path.append(p); p = came[p]
                path.append((sx, sy)); path.reverse()
                return path

            for d in range(4):
                if self.wall_known[x][y][d] and self.walls[x][y][d]:
                    continue
                nx, ny = x + DIR_X[d], y + DIR_Y[d]
                if not (0 <= nx < W and 0 <= ny < H):
                    continue
                if not self.active[nx][ny]:
                    continue
                ng = g + 1
                if (nx, ny) not in gmap or ng < gmap[(nx, ny)]:
                    gmap[(nx, ny)] = ng
                    came[(nx, ny)] = (x, y)
                    heapq.heappush(openh, (ng + self._h(nx, ny), ng, nx, ny))
        return []

    def _sense(self):
        x, y, W, H = self.rx, self.ry, self.W, self.H
        for d in range(4):
            if not self.wall_known[x][y][d]:
                self.wall_known[x][y][d] = True
                nx, ny = x + DIR_X[d], y + DIR_Y[d]
                if 0 <= nx < W and 0 <= ny < H:
                    self.wall_known[nx][ny][OPP[d]] = True

    # ── Draw ──────────────────────────────────────────────────────────────────

    def _draw(self):
        if self.walls is None or self.active is None:
            return
        self.canvas.delete("all")
        W, H  = self.W, self.H
        cs    = self._cs()
        goals = self._gcells()
        lw    = max(1, cs // 8)

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

                self.canvas.create_rectangle(
                    px, py, px+cs, py+cs, fill=fill, outline="")

                if not self.active[x][y]:
                    continue

                if self.walls[x][y][0]:  # N
                    self.canvas.create_line(px, py, px+cs, py,
                                            fill=C_WALL, width=lw)
                if self.walls[x][y][1]:  # E
                    self.canvas.create_line(px+cs, py, px+cs, py+cs,
                                            fill=C_WALL, width=lw)
                if self.walls[x][y][2]:  # S
                    self.canvas.create_line(px, py+cs, px+cs, py+cs,
                                            fill=C_WALL, width=lw)
                if self.walls[x][y][3]:  # W
                    self.canvas.create_line(px, py, px, py+cs,
                                            fill=C_WALL, width=lw)

        # Goal markers — red dot
        for gx, gy in goals:
            if self._valid(gx, gy) and self.active[gx][gy]:
                gpx = gx * cs + cs // 2
                gpy = (H-1-gy) * cs + cs // 2
                r   = max(3, cs // 3)
                self.canvas.create_oval(gpx-r, gpy-r, gpx+r, gpy+r,
                                        fill="red", outline="#880000",
                                        width=max(1, lw))

        # Robot — blue circle
        rpx = self.rx * cs + cs // 2
        rpy = (H-1-self.ry) * cs + cs // 2
        r   = max(2, cs // 3)
        self.canvas.create_oval(rpx-r, rpy-r, rpx+r, rpy+r,
                                fill=C_ROBOT, outline="#003399",
                                width=max(1, cs // 8))

        self.canvas.update_idletasks()

    # ── Run ───────────────────────────────────────────────────────────────────

    def run_astar(self):
        if self.walls is None:
            self.sv.set("Hay nhan Generate Maze truoc!"); return
        if self.running:
            return
        start = self._find_start()
        if not start:
            self.sv.set("Khong co o hoat dong!"); return
        if self.goal is not None and (
                not self._valid(*self.goal) or not self.active[self.goal[0]][self.goal[1]]):
            self.sv.set("O dich khong hop le! Hay click chon lai."); return

        self.running   = True
        self.steps     = 0
        self.start_pos = start
        self.rx, self.ry = start
        self.cc = {}
        self._init_wk()

        self.cc[start] = C_START
        if self.goal is None:
            for gx, gy in self._gcells():
                self.cc[(gx, gy)] = C_GOAL_BG

        self._draw()
        self._step()

    def _step(self):
        if not self.running:
            return
        x, y = self.rx, self.ry
        self._sense()

        if (x, y) != self.start_pos and not self._is_goal(x, y):
            self.cc[(x, y)] = C_VISITED

        if self._is_goal(x, y):
            self.cc[(x, y)] = C_DONE
            self.running = False
            self.sv.set(f"HOAN THANH! Den ({x},{y}) sau {self.steps} buoc.")
            self._draw(); return

        path = self._astar(x, y)
        if len(path) < 2:
            self.running = False
            self.sv.set("Khong tim duoc duong den dich!"); self._draw(); return

        for px, py in path[1:]:
            if self.cc.get((px, py)) not in (C_VISITED, C_START, C_GOAL_BG, C_DONE):
                self.cc[(px, py)] = C_PATH

        nx, ny = path[1]
        self.rx, self.ry = nx, ny
        self.steps += 1
        self.sv.set(
            f"Buoc {self.steps} | Vi tri ({nx},{ny}) | Con lai ~{self._h(nx,ny)} buoc")

        self._draw()
        delay = max(1, 210 - self.speed_var.get())
        self.step_id = self.root.after(delay, self._step)

    def stop(self):
        self.running = False
        if self.step_id:
            self.root.after_cancel(self.step_id)
            self.step_id = None


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x780")
    MazeApp(root)
    root.mainloop()
