"""Gera as partes dinâmicas do perfil (roda a cada hora no GitHub Actions).

- dist/github-snake-dark.svg / github-snake.svg: cobrinha comendo comida aleatória
- dist/robux.svg: frase aleatória sobre Robux
- dist/ascii.svg: gatinho em arte ASCII com chuva estilo Matrix
- dist/galeria.svg: imagem sorteada de assets/galeria/
"""
import base64
import glob
import os
import random
import time
from xml.sax.saxutils import escape

MONO = "'Fira Code','Cascadia Code',Consolas,'Courier New',monospace"

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



FRASES = [
    "Aceito Robux. Pix também, mas prefiro Robux.",
    "Faço sites por 400 Robux.",
    "Robux: a única moeda que eu entendo.",
    "Se você tem Robux, a gente é amigo.",
    "Cotação de hoje: 1 abraço = 0 Robux.",
    "Achou um bug? Paga em Robux.",
    "Investindo tudo em Robux desde 2011.",
    "Meu cofrinho de Robux está vazio :(",
    "Robux grátis? Só no meu coração.",
    "Troco café por Robux.",
    "1 commit = 1 Robux. Estou rico? Não.",
    "Me manda Robux que eu te mando um bom dia.",
    "Saldo atual: 0 Robux (por enquanto).",
    "Aceito Robux em até 12x sem juros.",
    "Patrocinado por ninguém. Aceito Robux.",
    "Código limpo, carteira de Robux vazia.",
    "Testo seu sistema por apenas 800 Robux.",
    "Encontrei uma vulnerabilidade: falta Robux.",
    "Robux na conta, sorriso no rosto.",
    "Oi, você tem Robux? Pergunto por um amigo.",
    "Meu GLPI abriu um chamado: falta de Robux.",
    "IA local treinada só para pedir Robux.",
]

CAT = [
    '               .-:                        .=***-',
    '             :%@@@@%+:                  =#@@@@@@#',
    '            :@@@@@@@@@%+.            .+@@@@@@@@@@+',
    '            *@@@@@@@@@@@@*-=*##%%%#**@@@@@@@@@@@@%',
    '            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',
    '            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*',
    '            -@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-',
    '             #@@@@@@@@@@@@@@@@@@@@@@@@@*=-=+%@@@@%.',
    '            .%@@@@@@@@@#-::::+@@@@@@@*.=###+.%@@@@+:=+###:',
    '            #@@@@@@@@@*.*@@@%=*@@@##%%#@@@@@@@@@@@@#+=--:',
    '           :@@@=::::-+@@@@@@@@@@@*. *@@@@@@@@@@@@@@++++=-.',
    '           :@@@@@@@%#%@@@@@@@@-:*+.:-+:-@@@@@@@@@@%--==**:',
    '            %@@%=..-+#@@@@@@@@@*+*%@%*%@@@@@@@@@@@@%*+-.',
    '      .-=+=..%@@#%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@* :=*#-',
    '    -#@@@@@@*.+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%=',
    '  .#@@@@@@@@@- .=%@@@@@@@@@@@@@@@@@@@@@@@@@@@%+.',
    ' .%@@@@@@@@@#  :#@@@@@@@@@@@@@@@@@@@@@@@@@@@@:',
    ' #@@@@@@@@#: .*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-',
    ':@@@@@@@@=  :%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:',
    ':@@@@@@@+  .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#',
    '.@@@@@@@:  *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:',
    ' =@@@@@@#. @@@@@@@@@@@@:@@@@@@@@@@@@@@@@@+@@@@@@=',
    '  =@@@@@@%=%@@@@@@@@@@* @@@@@@@@%#@@@@@@@:+@@@@@:',
    '   .#@@@@@@@@@@@@@@@@@* #@@@@@@@+:@@@@@@@:=@@@@%',
    '     :*@@@@@@@@@@@@@@@% *@@@@@@@=:@@@@@@@.=@@@%.',
    '       .-+#%@@@@@@@@@@@+:%@@@@@@:.@@@@@@+.%@@*.',
    '             ...:=+***+- .=*##+:  :*##*- .-:.',
]


def card(w, h, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>'
            f'{inner}</svg>')


def robux(rnd):
    frase = escape(rnd.choice(FRASES))
    qtd = rnd.randint(0, 3)
    inner = (f'<g font-family="{MONO}" text-anchor="middle">'
             f'<text x="440" y="44" font-size="20" font-weight="600" fill="#ffffff">{frase}'
             f'<tspan fill="#ffffff"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.55;1" dur="1s" repeatCount="indefinite"/>_</tspan></text>'
             f'<text x="440" y="68" font-size="11" fill="#6e7681">Robux recebidos nesta hora: {qtd}</text></g>')
    return card(880, 88, inner)


def ascii_art(rnd):
    w, lh, cw = 880, 13, 7.0
    h = len(CAT) * lh + 40
    chars = "01$R#ROBUX+*:"
    rain = []
    for i in range(44):
        x = 10 + i * 20
        n = rnd.randint(8, 16)
        dur = rnd.uniform(4, 9)
        beg = -rnd.uniform(0, dur)
        spans = []
        for k in range(n):
            op = 0.9 if k == n - 1 else 0.12 + 0.5 * k / n
            col = "#ffffff" if k == n - 1 else "#6e7681"
            spans.append(f'<tspan x="{x}" dy="15" fill="{col}" fill-opacity="{op:.2f}">{escape(rnd.choice(chars))}</tspan>')
        rain.append(f'<text y="0" font-family="{MONO}" font-size="12">{"".join(spans)}'
                    f'<animateTransform attributeName="transform" type="translate" values="0 {-n * 15};0 {h}" '
                    f'dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/></text>')
    x0 = (w - 58 * cw) / 2
    lines = []
    for j, l in enumerate(CAT):
        if l.strip():
            lines.append(f'<text x="{x0:.0f}" y="{28 + j * lh}" textLength="{len(l) * cw:.0f}" '
                         f'lengthAdjust="spacing" xml:space="preserve">{escape(l)}</text>')
    inner = (f'<clipPath id="c"><rect width="{w}" height="{h}" rx="10"/></clipPath>'
             f'<g clip-path="url(#c)">{"".join(rain)}</g>'
             f'<rect x="{x0 - 14:.0f}" y="10" width="{58 * cw + 28:.0f}" height="{h - 20}" rx="8" fill="#0d1117" fill-opacity=".72"/>'
             f'<g font-family="{MONO}" font-size="12" fill="#e6edf3">{"".join(lines)}'
             f'<animate attributeName="opacity" values="1;1;.55;1;1;.8;1" keyTimes="0;.9;.91;.92;.95;.96;1" dur="6s" repeatCount="indefinite"/></g>')
    return card(w, h, inner)


def galeria(rnd):
    tipos = {".avif": "image/avif", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}
    fotos = [f for f in glob.glob("assets/galeria/*") if os.path.splitext(f)[1].lower() in tipos]
    fotos = fotos or ["assets/swag-for-life.avif"]
    f = rnd.choice(sorted(fotos))
    dado = base64.b64encode(open(f, "rb").read()).decode()
    mime = tipos[os.path.splitext(f)[1].lower()]
    w, h = 880, 495
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<clipPath id="c"><rect width="{w}" height="{h}" rx="10"/></clipPath>'
            f'<image href="data:{mime};base64,{dado}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#c)"/>'
            f'</svg>')


def main():
    hora = int(time.time() // 3600)
    rnd = random.Random(hora)
    path, food, eaten_at = build(rnd)
    levels = {c: rnd.randrange(4) for c in food}
    os.makedirs("dist", exist_ok=True)
    saidas = {
        "github-snake-dark.svg": svg("dark", path, food, eaten_at, levels),
        "github-snake.svg": svg("light", path, food, eaten_at, levels),
        "robux.svg": robux(rnd),
        "ascii.svg": ascii_art(rnd),
        "galeria.svg": galeria(rnd),
    }
    for nome, conteudo in saidas.items():
        open(os.path.join("dist", nome), "w").write(conteudo)
    print("hora", hora, "arquivos:", ", ".join(saidas))


if __name__ == "__main__":
    main()
