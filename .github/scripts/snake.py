"""Cobrinha animada que come comida aleatória (não depende das contribuições).

Gera dist/github-snake-dark.svg e dist/github-snake.svg.
Roda no GitHub Actions; cada execução sorteia um campo novo.
"""
import os
import random
import time

COLS, ROWS, CELL, DOT = 53, 7, 16, 12
STEP = 0.11            # segundos por casa
SNAKE_LEN = 5
FOOD = 46              # quantidade de comida no campo

THEMES = {
    "dark": {
        "empty": "#161b22",
        "food": ["#3a3a3a", "#6e6e6e", "#a8a8a8", "#ffffff"],
        "snake": ["#ffffff", "#e6e6e6", "#c4c4c4", "#9a9a9a", "#6e6e6e"],
    },
    "light": {
        "empty": "#ebedf0",
        "food": ["#c6c6c6", "#9a9a9a", "#5c5c5c", "#1a1a1a"],
        "snake": ["#000000", "#1f1f1f", "#3d3d3d", "#5c5c5c", "#7a7a7a"],
    },
}


def manhattan_path(a, b, rnd):
    """Caminho casa a casa de a até b, alternando eixos para parecer orgânico."""
    (x, y), (tx, ty) = a, b
    out = []
    while (x, y) != (tx, ty):
        moves = []
        if x != tx:
            moves.append((1 if tx > x else -1, 0))
        if y != ty:
            moves.append((0, 1 if ty > y else -1))
        dx, dy = rnd.choice(moves)
        x, y = x + dx, y + dy
        out.append((x, y))
    return out


def build(rnd):
    cells = [(x, y) for x in range(COLS) for y in range(ROWS)]
    food = rnd.sample(cells, FOOD)
    start = (0, rnd.randrange(ROWS))
    path, cur, remaining = [start], start, food[:]
    eaten_at = {}
    while remaining:
        nxt = min(remaining, key=lambda c: abs(c[0] - cur[0]) + abs(c[1] - cur[1]) + rnd.random())
        remaining.remove(nxt)
        path += manhattan_path(cur, nxt, rnd)
        eaten_at[nxt] = len(path) - 1
        cur = nxt
    # volta ao começo para o loop ficar contínuo
    path += manhattan_path(cur, start, rnd)[:-1] if cur != start else []
    if path[-1] == start and len(path) > 1:
        path = path[:-1]
    return path, food, eaten_at


def svg(theme, path, food, eaten_at, rnd_levels):
    t = THEMES[theme]
    n = len(path)
    total = n * STEP
    w, h = COLS * CELL, ROWS * CELL
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-16 -16 {w + 32} {h + 32}" '
           f'width="{w + 32}" height="{h + 32}">',
           "<desc>Cobrinha aleatória · github.com/paulomeier</desc>"]
    pos = lambda c: (c[0] * CELL + (CELL - DOT) / 2, c[1] * CELL + (CELL - DOT) / 2)
    food_set = set(food)
    for c in [(x, y) for x in range(COLS) for y in range(ROWS)]:
        x, y = pos(c)
        if c in food_set:
            lvl = t["food"][rnd_levels[c]]
            te = eaten_at[c] / n
            back = min(0.999, te + rnd_levels[c] * 0.07 + 0.18)  # renasce depois
            out.append(
                f'<rect x="{x:.0f}" y="{y:.0f}" width="{DOT}" height="{DOT}" rx="3" fill="{lvl}">'
                f'<animate attributeName="fill" values="{lvl};{t["empty"]};{lvl}" '
                f'keyTimes="0;{te:.4f};{back:.4f}" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite"/>'
                f"</rect>")
        else:
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{DOT}" height="{DOT}" rx="3" fill="{t["empty"]}"/>')
    # cobrinha: cada gomo segue o mesmo caminho, alguns passos atrás
    for k in range(SNAKE_LEN - 1, -1, -1):
        size = DOT + 2 - k * 1.2
        off = (CELL - size) / 2
        vals = []
        for s in range(n + 1):
            c = path[(s - k) % n]
            vals.append(f"{c[0] * CELL + off:.1f} {c[1] * CELL + off:.1f}")
        out.append(
            f'<rect width="{size:.1f}" height="{size:.1f}" rx="{size / 3:.1f}" fill="{t["snake"][k]}">'
            f'<animateTransform attributeName="transform" type="translate" values="{";".join(vals)}" '
            f'dur="{total:.2f}s" repeatCount="indefinite"/></rect>')
    out.append("</svg>")
    return "".join(out)


def main():
    seed = int(os.environ.get("SNAKE_SEED", time.time() // 3600))
    rnd = random.Random(seed)
    path, food, eaten_at = build(rnd)
    levels = {c: rnd.randrange(4) for c in food}
    os.makedirs("dist", exist_ok=True)
    open("dist/github-snake-dark.svg", "w").write(svg("dark", path, food, eaten_at, levels))
    open("dist/github-snake.svg", "w").write(svg("light", path, food, eaten_at, levels))
    print(f"seed={seed} passos={len(path)}")


if __name__ == "__main__":
    main()
