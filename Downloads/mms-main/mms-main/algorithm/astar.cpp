// algorithm/astar.cpp
// Thuat toan A* cho robot Micromouse.
// Giao tiep voi giao dien Python (ui.py) qua stdin/stdout.
//
// Build:  Windows: build.bat   Linux/Mac: make
// Chay:   Duoc goi dong tu ui.py, khong can chay tay.
//
// Giao thuc (stdin/stdout):
//   C++ gui lenh, Python tra loi:
//     mazeWidth     -> <so>
//     mazeHeight    -> <so>
//     goalX         -> <so>
//     goalY         -> <so>
//     wallFront/Left/Right/Back -> "true" | "false"
//     moveForward   -> "" (thanh cong) | "crash"
//     turnLeft/Right -> ""
//   C++ gui lenh hien thi (khong co phan hoi):
//     setColor <x> <y> <char>
//     clearAllColor

#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
#include <queue>

using namespace std;

// ── Huong di ──────────────────────────────────────────────────────────────────
const int DIR_X[4]   = { 0,  1,  0, -1 };   // N E S W (delta x)
const int DIR_Y[4]   = { 1,  0, -1,  0 };   // N E S W (delta y)
const char DIR_CH[4] = {'n','e','s','w'};

// ── Du lieu toan cuc ──────────────────────────────────────────────────────────
int W = 0, H = 0;      // kich thuoc ban do
int goalX = 0, goalY = 0; // o dich (nhan tu Python)

// walls[x][y][d]     = true → co tuong
// wallKnown[x][y][d] = true → da cam bien
vector<vector<array<bool,4>>> walls;
vector<vector<array<bool,4>>> wallKnown;

int robotX = 0, robotY = 0;
int robotDir = 0;   // ban dau huong Bac

// ── Giao thuc stdin/stdout ────────────────────────────────────────────────────

// Gui lenh va doc phan hoi
static string query(const string &cmd) {
    cout << cmd << "\n";
    cout.flush();
    string resp;
    getline(cin, resp);
    return resp;
}

// Gui lenh hien thi (khong can phan hoi)
static void display(const string &cmd) {
    cout << cmd << "\n";
    cout.flush();
}

static void apiSetColor(int x, int y, char c) {
    display("setColor " + to_string(x) + " " + to_string(y) + " " + c);
}
static void apiSetWall(int x, int y, char d) {
    display("setWall " + to_string(x) + " " + to_string(y) + " " + d);
}

// ── Cam bien tuong ────────────────────────────────────────────────────────────

static void markWall(int x, int y, int dir, bool present) {
    if (wallKnown[x][y][dir]) return;
    walls[x][y][dir]     = present;
    wallKnown[x][y][dir] = true;

    int nx = x + DIR_X[dir], ny = y + DIR_Y[dir];
    if (nx >= 0 && nx < W && ny >= 0 && ny < H) {
        int opp = (dir + 2) % 4;
        walls[nx][ny][opp]     = present;
        wallKnown[nx][ny][opp] = true;
    }
    if (present) apiSetWall(x, y, DIR_CH[dir]);
}

// Cam bien 3 tuong xung quanh o hien tai
static void senseWalls() {
    bool front = query("wallFront") == "true";
    bool right  = query("wallRight") == "true";
    bool left   = query("wallLeft")  == "true";
    markWall(robotX, robotY, robotDir,           front);
    markWall(robotX, robotY, (robotDir + 1) % 4, right);
    markWall(robotX, robotY, (robotDir + 3) % 4, left);
}

// ── Di chuyen ─────────────────────────────────────────────────────────────────

static void turnRight() { query("turnRight"); robotDir = (robotDir + 1) % 4; }
static void turnLeft()  { query("turnLeft");  robotDir = (robotDir + 3) % 4; }

static void turnToFace(int target) {
    int diff = (target - robotDir + 4) % 4;
    if      (diff == 1) turnRight();
    else if (diff == 3) turnLeft();
    else if (diff == 2) { turnRight(); turnRight(); }
}

static void stepForward() {
    query("moveForward");
    robotX += DIR_X[robotDir];
    robotY += DIR_Y[robotDir];
}

// ── Heuristic (Manhattan den o dich) ─────────────────────────────────────────

static float heuristic(int x, int y) {
    return (float)(abs(x - goalX) + abs(y - goalY));
}

// ── A* Online ─────────────────────────────────────────────────────────────────

struct Node {
    float f;
    int x, y;
    bool operator>(const Node &o) const { return f > o.f; }
};

// Tim duong tu (sx,sy) den (goalX,goalY).
// Tuong chua biet = coi la thong (lac quan).
static vector<pair<int,int>> astar(int sx, int sy) {
    auto idx = [&](int x, int y) { return x * H + y; };

    vector<float> g(W * H, 1e9f);
    vector<int>   parent(W * H, -1);
    vector<bool>  closed(W * H, false);
    priority_queue<Node, vector<Node>, greater<Node>> open;

    g[idx(sx, sy)] = 0.0f;
    open.push({ heuristic(sx, sy), sx, sy });

    while (!open.empty()) {
        Node cur = open.top(); open.pop();
        int x = cur.x, y = cur.y;

        if (closed[idx(x, y)]) continue;
        closed[idx(x, y)] = true;

        if (x == goalX && y == goalY) {
            // Trich xuat duong di
            vector<pair<int,int>> path;
            int p = idx(x, y);
            while (p != -1) {
                path.push_back({ p / H, p % H });
                p = parent[p];
            }
            reverse(path.begin(), path.end());
            return path;
        }

        for (int d = 0; d < 4; d++) {
            // Bo qua huong co tuong da biet
            if (wallKnown[x][y][d] && walls[x][y][d]) continue;

            int nx = x + DIR_X[d], ny = y + DIR_Y[d];
            if (nx < 0 || nx >= W || ny < 0 || ny >= H) continue;

            float ng = g[idx(x, y)] + 1.0f;
            if (ng < g[idx(nx, ny)]) {
                g[idx(nx, ny)] = ng;
                parent[idx(nx, ny)] = idx(x, y);
                open.push({ ng + heuristic(nx, ny), nx, ny });
            }
        }
    }

    return {};  // Khong tim thay duong
}

// ── Ham chinh ─────────────────────────────────────────────────────────────────

int main() {
    ios::sync_with_stdio(false);

    // Lay thong tin ban do tu Python
    W     = stoi(query("mazeWidth"));
    H     = stoi(query("mazeHeight"));
    goalX = stoi(query("goalX"));
    goalY = stoi(query("goalY"));

    // Khoi tao bang tuong
    walls.assign(W,     vector<array<bool,4>>(H, {false,false,false,false}));
    wallKnown.assign(W, vector<array<bool,4>>(H, {false,false,false,false}));

    // Danh dau tuong bien (luon ton tai)
    for (int x = 0; x < W; x++) {
        markWall(x, 0,   2, true);   // bien Nam
        markWall(x, H-1, 0, true);   // bien Bac
    }
    for (int y = 0; y < H; y++) {
        markWall(0,   y, 3, true);   // bien Tay
        markWall(W-1, y, 1, true);   // bien Dong
    }

    // To mau khoi dau
    apiSetColor(0, 0, 'g');              // xuat phat = xanh la
    apiSetColor(goalX, goalY, 'R');      // dich = do dam

    // ── Vong lap A* truc tuyen ────────────────────────────────────────────────
    while (true) {
        senseWalls();
        apiSetColor(robotX, robotY, 'c');  // o da di qua = cyan

        // Kiem tra da den dich chua
        if (robotX == goalX && robotY == goalY) {
            apiSetColor(robotX, robotY, 'G');  // dich = xanh la dam
            break;
        }

        // Lap ke hoach voi kien thuc hien tai
        vector<pair<int,int>> path = astar(robotX, robotY);
        if (path.size() < 2) break;  // khong co duong

        // To duong ke hoach mau vang
        for (size_t i = 1; i < path.size(); i++)
            apiSetColor(path[i].first, path[i].second, 'y');

        // Xac dinh huong can di
        int nx = path[1].first, ny = path[1].second;
        int moveDir = -1;
        for (int d = 0; d < 4; d++) {
            if (robotX + DIR_X[d] == nx && robotY + DIR_Y[d] == ny) {
                moveDir = d; break;
            }
        }
        if (moveDir < 0) break;

        // Quay dung huong va tien
        turnToFace(moveDir);
        stepForward();
    }

    return 0;
}
