// A* Micromouse Algorithm for MMS Simulator
// Communicates via stdin/stdout per the MMS protocol.
// Directions: 0=North, 1=East, 2=South, 3=West

#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <iostream>
#include <map>
#include <queue>
#include <string>
#include <vector>

using namespace std;

// ── Constants ─────────────────────────────────────────────────────────────────

const int DIR_X[4]    = { 0,  1,  0, -1 };   // N  E  S  W  (delta x)
const int DIR_Y[4]    = { 1,  0, -1,  0 };   // N  E  S  W  (delta y)
const char DIR_CH[4]  = {'n','e','s','w'};

// ── Global state ──────────────────────────────────────────────────────────────

int W = 0, H = 0;   // maze dimensions

// walls[x][y][d]     = true → wall present
// wallKnown[x][y][d] = true → already sensed
vector<vector<array<bool, 4>>> walls;
vector<vector<array<bool, 4>>> wallKnown;

int robotX = 0, robotY = 0;
int robotDir = 0;   // facing North initially

// ── MMS API helpers ───────────────────────────────────────────────────────────

// Commands that return a response
static string query(const string &cmd) {
    cout << cmd << "\n";
    cout.flush();
    string resp;
    getline(cin, resp);
    return resp;
}

// Commands that have no response (display-only)
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
static void apiClearAllColor() { display("clearAllColor"); }

// ── Wall sensing & propagation ────────────────────────────────────────────────

static void markWall(int x, int y, int dir, bool present) {
    if (wallKnown[x][y][dir]) return;   // already known
    walls[x][y][dir]     = present;
    wallKnown[x][y][dir] = true;

    // Mirror onto the neighbouring cell
    int nx = x + DIR_X[dir], ny = y + DIR_Y[dir];
    if (nx >= 0 && nx < W && ny >= 0 && ny < H) {
        int opp = (dir + 2) % 4;
        walls[nx][ny][opp]     = present;
        wallKnown[nx][ny][opp] = true;
    }

    if (present) apiSetWall(x, y, DIR_CH[dir]);
}

// Sense the three observable walls at the robot's current cell
static void senseWalls() {
    bool front = query("wallFront") == "true";
    bool right  = query("wallRight") == "true";
    bool left   = query("wallLeft")  == "true";
    markWall(robotX, robotY, robotDir,           front);
    markWall(robotX, robotY, (robotDir + 1) % 4, right);
    markWall(robotX, robotY, (robotDir + 3) % 4, left);
}

// ── Movement ──────────────────────────────────────────────────────────────────

static void turnRight() { query("turnRight"); robotDir = (robotDir + 1) % 4; }
static void turnLeft()  { query("turnLeft");  robotDir = (robotDir + 3) % 4; }

static void turnToFace(int target) {
    int diff = (target - robotDir + 4) % 4;
    if      (diff == 1) turnRight();
    else if (diff == 3) turnLeft();
    else if (diff == 2) { turnRight(); turnRight(); }
    // diff == 0 → already facing the right direction
}

static void stepForward() {
    query("moveForward");
    robotX += DIR_X[robotDir];
    robotY += DIR_Y[robotDir];
}

// ── Center cells ──────────────────────────────────────────────────────────────

static vector<pair<int,int>> centerCells() {
    // Matches the logic in Maze::getCenterPositions
    int ax = (W-1)/2, ay = (H-1)/2;
    int bx =  W/2,    by = (H-1)/2;
    int cx = (W-1)/2, cy =  H/2;
    int dx2 = W/2,    dy2 = H/2;

    vector<pair<int,int>> v;
    v.push_back({ax, ay});
    if      (W%2==0 && H%2==0) { v.push_back({bx,by}); v.push_back({cx,cy}); v.push_back({dx2,dy2}); }
    else if (W%2==0)             v.push_back({bx,by});
    else if (H%2==0)             v.push_back({cx,cy});
    return v;
}

static bool isCenter(int x, int y) {
    for (auto &c : centerCells())
        if (c.first == x && c.second == y) return true;
    return false;
}

// Manhattan distance to nearest center cell (admissible heuristic)
static float heuristic(int x, int y) {
    float best = 1e9f;
    for (auto &c : centerCells()) {
        float d = (float)(abs(x - c.first) + abs(y - c.second));
        if (d < best) best = d;
    }
    return best;
}

// ── A* ────────────────────────────────────────────────────────────────────────

struct Node {
    float f;
    int x, y;
    bool operator>(const Node &o) const { return f > o.f; }
};

// Returns path from (sx,sy) to the nearest center cell.
// Unknown walls are treated as open (optimistic / online replanning).
static vector<pair<int,int>> astar(int sx, int sy) {
    auto idx = [&](int x, int y) { return x * H + y; };
    int N = W * H;

    vector<float> g(N, 1e9f);
    vector<int>   parent(N, -1);
    vector<bool>  closed(N, false);
    priority_queue<Node, vector<Node>, greater<Node>> open;

    g[idx(sx, sy)] = 0.0f;
    open.push({ heuristic(sx, sy), sx, sy });

    while (!open.empty()) {
        Node cur = open.top(); open.pop();
        int x = cur.x, y = cur.y;

        if (closed[idx(x, y)]) continue;
        closed[idx(x, y)] = true;

        if (isCenter(x, y)) {
            // Reconstruct path from goal back to start
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
            // Skip if we KNOW there is a wall
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

    return {};   // No path found
}

// ── Main ──────────────────────────────────────────────────────────────────────

int main() {
    // Get maze dimensions from simulator
    W = stoi(query("mazeWidth"));
    H = stoi(query("mazeHeight"));

    // Initialise wall maps
    walls.assign(W,     vector<array<bool,4>>(H, {false,false,false,false}));
    wallKnown.assign(W, vector<array<bool,4>>(H, {false,false,false,false}));

    // Mark border walls (always present)
    for (int x = 0; x < W; x++) {
        markWall(x, 0,   2, true);    // South border
        markWall(x, H-1, 0, true);    // North border
    }
    for (int y = 0; y < H; y++) {
        markWall(0,   y, 3, true);    // West border
        markWall(W-1, y, 1, true);    // East border
    }

    // Initial colours
    apiSetColor(0, 0, 'g');                                      // start = green
    for (auto &c : centerCells()) apiSetColor(c.first, c.second, 'R');  // goals = dark red

    // ── Online A* navigation loop ─────────────────────────────────────────────
    while (true) {
        senseWalls();
        apiSetColor(robotX, robotY, 'c');   // mark as visited (cyan)

        if (isCenter(robotX, robotY)) {
            apiSetColor(robotX, robotY, 'G');   // arrived (dark green)
            break;
        }

        // Plan optimal path with current knowledge
        vector<pair<int,int>> path = astar(robotX, robotY);
        if (path.size() < 2) break;   // no path (shouldn't happen in a valid maze)

        // Highlight the planned path in yellow
        for (size_t i = 1; i < path.size(); i++)
            apiSetColor(path[i].first, path[i].second, 'y');

        // Determine next cell and the direction to move
        int nx = path[1].first, ny = path[1].second;
        int moveDir = -1;
        for (int d = 0; d < 4; d++) {
            if (robotX + DIR_X[d] == nx && robotY + DIR_Y[d] == ny) {
                moveDir = d; break;
            }
        }
        if (moveDir < 0) break;

        // Face the target direction and step forward
        turnToFace(moveDir);
        stepForward();
    }

    return 0;
}
