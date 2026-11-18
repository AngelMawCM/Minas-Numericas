import math
import random
from fractions import Fraction

SECCIONES = [
    ("Interpolación", "Común", (230, 230, 230)),
    ("Mínimos cuadrados", "Poco común", (90, 230, 90)),
    ("Ecuaciones lineales", "Raro", (80, 160, 255)),
    ("Integración", "Épico", (190, 90, 255)),
    ("Ecuaciones no lineales", "Legendario", (255, 170, 30)),
    ("Ecuaciones diferenciales (EDO)", "Mítico", (255, 70, 110)),
]
PROB_EJEMPLO = 0.2  # probabilidad de que salga el ejemplo exacto de los apuntes


def R(v, n=9):
    return round(v, n)


def fmt(v):
    s = f"{v:.9f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def P(etiqueta, valor, formula):
    return (etiqueta, R(float(valor)), formula)


def problema(enunciado, pasos, ejemplo=False):
    if ejemplo:
        enunciado = "(Ejemplo de tus apuntes)\n" + enunciado
    return {"enunciado": enunciado, "pasos": pasos}


def usar_ejemplo():
    return random.random() < PROB_EJEMPLO


def rnd(a, b, nd=1):
    return round(random.uniform(a, b), nd)


def resolver_sistema(A, b):
    n = len(A)
    M = [[Fraction(v) for v in A[i]] + [Fraction(b[i])] for i in range(n)]
    for i in range(n):
        p = next(r for r in range(i, n) if M[r][i] != 0)
        M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i and M[r][i] != 0:
                f = M[r][i] / M[i][i]
                M[r] = [M[r][c] - f * M[i][c] for c in range(n + 1)]
    return [float(M[i][n] / M[i][i]) for i in range(n)]


# ====================== INTERPOLACION ======================
FUNCS = [("ln(x)", math.log), ("sqrt(x)", math.sqrt), ("sin(x)", math.sin), ("exp(x/3)", lambda x: math.exp(x / 3))]


def tabla(xs, ys):
    return "\n".join(f"x{i+1} = {fmt(x)}    y{i+1} = {fmt(y)}" for i, (x, y) in enumerate(zip(xs, ys)))


def calc_lineal(a, b, x, ej=False):
    fa, fb, real = math.log(a), math.log(b), math.log(x)
    m = (fb - fa) / (b - a)
    g = m * (x - a) + fa
    enun = (f"Interpolación LINEAL de f(x) = Ln(x)\nUsa f(a) = Ln({a}) = {fmt(fa)}  y  f(b) = Ln({b}) = {fmt(fb)}\n"
            f"Estima Ln({x}).  Valor real: {fmt(real)}")
    return problema(enun, [
        P("Pendiente [f(b)-f(a)]/(b-a)", m, "[f(b) - f(a)] / (b - a)"),
        P("g(x) = pendiente·(x-a) + f(a)", g, "g(x) = [f(b)-f(a)]/(b-a)·(x - a) + f(a)"),
        P("Error Є = |f(x) - g(x)|", abs(real - g), "Є = |valor real - valor calculado|")], ej)


def g_lineal():
    if usar_ejemplo():
        return calc_lineal(*random.choice([(2, 5, 3), (2, 4, 3)]), ej=True)
    a = random.randint(1, 4)
    b = a + random.randint(2, 4)
    return calc_lineal(a, b, random.randint(a + 1, b - 1))


def calc_newton(xs, ys, xv, atras, ej=False):
    n = len(xs)
    h = abs(xs[1] - xs[0])
    d = [ys]
    for k in range(1, n):
        d.append([d[k - 1][i + 1] - d[k - 1][i] for i in range(n - k)])
    ref = xs[-1] if atras else xs[0]
    s = (xv - ref) / h
    g = ys[-1] if atras else ys[0]
    coef = 1
    sim = "∇" if atras else "Δ"
    nombre_ref = f"x{n}" if atras else "x1"
    pasos = [P("h = |x2 - x1|", h, "h = |x(i+1) - x(i)|"),
             P(f"s = (x - {nombre_ref}) / h", s, "s = (x - xi) / h   " + ("(negativo)" if atras else "(positivo)"))]
    for k in range(1, n):
        v = d[k][n - k - 1] if atras else d[k][0]
        coef *= (s + k - 1) / k if atras else (s - k + 1) / k
        g += v * coef
        pasos.append(P(f"{sim}{k} f", v, f"{sim}{k} f(xi): resta de dos diferencias de orden {k-1}"))
    pasos.append(P("g(x) final", g, "g(x) = yi + Δ'f·s + Δ²f·s(s-1)/2! + ...  (atrás: s(s+1))"))
    nom = "ATRÁS" if atras else "ADELANTE"
    return problema(f"Interpolación de NEWTON HACIA {nom}\n{tabla(xs, ys)}\nObtén g({fmt(xv)})", pasos, ej)


def _newton_azar(atras):
    n = random.choice([3, 4])
    h = random.choice([0.5, 1, 0.4, 0.2])
    x0 = rnd(1, 4)
    _, f = random.choice(FUNCS)
    xs = [round(x0 + i * h, 2) for i in range(n)]
    ys = [round(f(x), 2) for x in xs]
    fr = random.uniform(0.25, 0.75)
    xv = round(xs[-1] - h * fr if atras else xs[0] + h * fr, 2)
    return xs, ys, xv


def g_adelante():
    if usar_ejemplo():
        return calc_newton([1.7, 2.4, 3.1], [0.35, 0.87, 1.03], 3, False, True)
    return calc_newton(*_newton_azar(False), False)


def g_atras():
    if usar_ejemplo():
        return calc_newton([1.7, 2.4, 3.1], [0.35, 0.87, 1.03], 3, True, True)
    return calc_newton(*_newton_azar(True), True)


def _libres(n):
    _, f = random.choice(FUNCS)
    x = rnd(1, 3)
    xs, ys = [], []
    for _ in range(n):
        xs.append(x)
        ys.append(round(f(x), 2))
        x = round(x + random.uniform(0.3, 1.2), 1)
    i = random.randint(0, n - 2)
    return xs, ys, round(xs[i] + (xs[i + 1] - xs[i]) * random.uniform(0.25, 0.75), 2)


def calc_lagrange(xs, ys, xv, ej=False):
    n = len(xs)
    pasos, tot = [], 0
    for i in range(n):
        t = ys[i]
        for j in range(n):
            if j != i:
                t *= (xv - xs[j]) / (xs[i] - xs[j])
        tot += t
        pasos.append(P(f"Término {i+1}:  y{i+1}·Π(x-xj)/(xi-xj)", t, "yi · Π (x - xj) / (xi - xj),  j distinto de i"))
    pasos.append(P("g(x) = suma de términos", tot, "g(x) = Σ de los términos"))
    return problema(f"Interpolación de LAGRANGE\n{tabla(xs, ys)}\nObtén g({fmt(xv)})", pasos, ej)


def g_lagrange():
    if usar_ejemplo():
        return calc_lagrange([2.2, 2.5, 2.8, 3.1, 3.4], [2.54, 2.82, 3.21, 3.32, 3.41], 2.4, True)
    return calc_lagrange(*_libres(random.choice([3, 4])))


def calc_divididas(xs, ys, xv, ej=False):
    n = len(xs)
    t = [ys]
    for k in range(1, n):
        t.append([(t[k - 1][i + 1] - t[k - 1][i]) / (xs[i + k] - xs[i]) for i in range(n - k)])
    pasos, g, prod = [], 0, 1
    for k in range(n):
        if k:
            prod *= (xv - xs[k - 1])
        g += t[k][0] * prod
        pasos.append(P(f"D{k}", t[k][0], "D0 = y1;  Dk = (resta de dos diferencias k-1) / (resta de x no comunes)"))
    pasos.append(P("g(x) = D0 + D1(x-x1) + ...", g, "g(x) = D0 + D1(x-x1) + D2(x-x1)(x-x2) + ..."))
    return problema(f"NEWTON con DIFERENCIAS DIVIDIDAS\n{tabla(xs, ys)}\nObtén g({fmt(xv)})", pasos, ej)


def g_divididas():
    if usar_ejemplo():
        return calc_divididas([7.3, 6.5, 6.1], [-0.28, -1.35, -1.96], 7, True)
    return calc_divididas(*_libres(random.choice([3, 4])))


# ====================== MINIMOS CUADRADOS ======================
def _tabxy(xs, ys):
    return "\n".join(f"x = {fmt(x)}    y = {fmt(y)}" for x, y in zip(xs, ys))


def _normales(base, xs, ys):
    k = len(base)
    A = [[sum(base[i](x) * base[j](x) for x in xs) for j in range(k)] for i in range(k)]
    b = [sum(base[i](x) * y for x, y in zip(xs, ys)) for i in range(k)]
    return A, b, resolver_sistema(A, b)


def calc_recta(xs, ys, ej=False):
    base = [lambda x: 1, lambda x: x]
    A, b, sol = _normales(base, xs, ys)
    return problema(f"Ajuste de LÍNEA RECTA  g(x) = a0 + a1·x\n{_tabxy(xs, ys)}", [
        P("Σx", A[0][1], "Σx"), P("Σy", b[0], "Σy"), P("Σx²", A[1][1], "Σx²"), P("Σxy", b[1], "Σxy"),
        P("a0", sol[0], "Sistema: n·a0 + Σx·a1 = Σy ;  Σx·a0 + Σx²·a1 = Σxy"), P("a1", sol[1], "Resolver el sistema de 2x2")], ej)


def g_recta():
    if usar_ejemplo():
        return calc_recta([1.1, 1.9, 2.4, 4.8, 5.1, 10.5], [2.5, 2.7, 3.7, 5.2, 6.0, 8.3], True)
    xs = [1, 2, 3, 4, 5]
    a0, a1 = random.randint(-3, 5), random.choice([-2, -1, 1, 2, 3])
    return calc_recta(xs, [round(a0 + a1 * x + random.uniform(-0.8, 0.8), 1) for x in xs])


def g_cuadratica():
    xs = [0, 1, 2, 3, 4]
    c = (random.randint(-2, 4), random.randint(-3, 3), random.choice([-1, 1, 2]))
    ys = [round(c[0] + c[1] * x + c[2] * x * x + random.uniform(-0.8, 0.8), 1) for x in xs]
    base = [lambda x: 1, lambda x: x, lambda x: x * x]
    A, b, s = _normales(base, xs, ys)
    return problema(f"Ajuste CUADRÁTICO  g(x) = a0 + a1·x + a2·x²\n{_tabxy(xs, ys)}", [
        P("Σx²", A[1][1], "Σx²"), P("Σx³", A[1][2], "Σx³"), P("Σx⁴", A[2][2], "Σx⁴"), P("Σx²y", b[2], "Σx²y"),
        P("a0", s[0], "Resolver el sistema normal 3x3 (n, Σx, Σx²...)"), P("a1", s[1], "Resolver el sistema normal 3x3"),
        P("a2", s[2], "Resolver el sistema normal 3x3")])


def g_cubica():
    xs = [0, 1, 2, 3, 4, 5]
    c = [random.randint(-2, 3), random.randint(-3, 3), random.randint(-2, 2), random.choice([-0.5, 0.5, 1])]
    ys = [round(sum(c[i] * x ** i for i in range(4)) + random.uniform(-0.8, 0.8), 1) for x in xs]
    base = [lambda x: 1, lambda x: x, lambda x: x * x, lambda x: x ** 3]
    A, b, s = _normales(base, xs, ys)
    return problema(f"Ajuste CÚBICO  g(x) = a0 + a1·x + a2·x² + a3·x³\n{_tabxy(xs, ys)}", [
        P("Σx³", A[1][2], "Σx³"), P("Σx⁵", A[2][3], "Σx⁵"), P("Σx⁶", A[3][3], "Σx⁶"), P("Σx³y", b[3], "Σx³y")] +
        [P(f"a{i}", s[i], "Resolver el sistema normal 4x4") for i in range(4)])


FBASE = [("Ln(x)", math.log), ("sen(x)", math.sin), ("e^x", math.exp), ("cos(x)", math.cos)]


def g_funcion():
    nom, f = random.choice(FBASE)
    xs = [1, 2, 3, 4, 5, 6]
    c = [random.randint(-2, 3), random.randint(-2, 2) or 1, random.choice([-2, -1, 1, 2])]
    esc = 0.2 if nom == "e^x" else 1
    ys = [round(c[0] + c[1] * x + c[2] * esc * f(x) + random.uniform(-0.3, 0.3), 2) for x in xs]
    base = [lambda x: 1, lambda x: x, f]
    A, b, s = _normales(base, xs, ys)
    return problema(f"LINEAL CON FUNCIÓN  g(x) = a0 + a1·x + a2·{nom}\n{_tabxy(xs, ys)}", [
        P(f"Σ {nom}", A[0][2], "Σ f(x)"), P(f"Σ x·{nom}", A[1][2], "Σ x·f(x)"), P(f"Σ {nom}²", A[2][2], "Σ f(x)²"),
        P("a0", s[0], "Resolver el sistema 3x3 (n, Σx, Σf ...)"), P("a1", s[1], "Resolver el sistema 3x3"), P("a2", s[2], "Resolver el sistema 3x3")])


def g_cuad_funcion():
    nom, f = random.choice(FBASE)
    xs = [1, 2, 3, 4, 5, 6, 7]
    c = [random.randint(-2, 3), random.randint(-2, 2), random.choice([-1, 1]) * 0.2, random.choice([-2, -1, 1, 2])]
    esc = 0.2 if nom == "e^x" else 1
    ys = [round(c[0] + c[1] * x + c[2] * x * x + c[3] * esc * f(x) + random.uniform(-0.3, 0.3), 2) for x in xs]
    base = [lambda x: 1, lambda x: x, lambda x: x * x, f]
    A, b, s = _normales(base, xs, ys)
    return problema(f"CUADRÁTICA CON FUNCIÓN  g(x) = a0 + a1·x + a2·x² + a3·{nom}\n{_tabxy(xs, ys)}", [
        P(f"Σ {nom}", A[0][3], "Σ f(x)"), P(f"Σ x²·{nom}", A[2][3], "Σ x²·f(x)"), P(f"Σ {nom}²", A[3][3], "Σ f(x)²")] +
        [P(f"a{i}", s[i], "Resolver el sistema 4x4") for i in range(4)])


# ====================== ECUACIONES LINEALES ======================
def _sistema():
    xt = [random.randint(-3, 4) for _ in range(3)]
    A = [[random.randint(-3, 3) for _ in range(3)] for _ in range(3)]
    for i in range(3):
        A[i][i] = random.randint(8, 12)
    return A, [sum(A[i][j] * xt[j] for j in range(3)) for i in range(3)], xt


PDF_A = [[3, -0.1, -0.2], [0.1, 7, -0.3], [0.3, -0.2, 10]]
PDF_B = [7.85, -19.3, 71.4]


def _txt(A, b, v=("a", "b", "c")):
    return "\n".join(f"{fmt(A[i][0])}{v[0]} + ({fmt(A[i][1])}){v[1]} + ({fmt(A[i][2])}){v[2]} = {fmt(b[i])}" for i in range(3))


def _elim(A, b):
    M = [list(map(Fraction, A[i])) + [Fraction(b[i])] for i in range(3)]
    m21 = M[1][0] / M[0][0]; M[1] = [M[1][c] - m21 * M[0][c] for c in range(4)]
    m31 = M[2][0] / M[0][0]; M[2] = [M[2][c] - m31 * M[0][c] for c in range(4)]
    m32 = M[2][1] / M[1][1]; M[2] = [M[2][c] - m32 * M[1][c] for c in range(4)]
    x3 = M[2][3] / M[2][2]
    x2 = (M[1][3] - M[1][2] * x3) / M[1][1]
    x1 = (M[0][3] - M[0][1] * x2 - M[0][2] * x3) / M[0][0]
    return M, (m21, m31, m32), (x1, x2, x3)


def g_montante():
    A, b, _ = _sistema()
    M = [list(map(Fraction, A[i])) + [Fraction(b[i])] for i in range(3)]
    prev, pivs = Fraction(1), []
    for k in range(3):
        piv = M[k][k]
        pivs.append(piv)
        M = [M[i][:] if i == k else [(piv * M[i][j] - M[i][k] * M[k][j]) / prev for j in range(4)] for i in range(3)]
        prev = piv
    det = pivs[2]
    x = [M[i][3] / det for i in range(3)]
    return problema("MÉTODO MONTANTE (pivote anterior)\nnuevo aij = (pivote·aij - aik·akj) / pivote anterior\n" + _txt(A, b, ("x1", "x2", "x3")), [
        P("Pivote 2 (a22 tras la 1ª iteración)", pivs[1], "a22' = a11·a22 - a21·a12"),
        P("Pivote 3 = determinante de A", det, "El último pivote es det(A)"),
        P("x1 = b1*/det", x[0], "xi = bi* / det(A)"), P("x2", x[1], "xi = bi* / det(A)"), P("x3", x[2], "xi = bi* / det(A)")])


def g_gaussjordan():
    A, b, _ = _sistema()
    M, _, (x1, x2, x3) = _elim(A, b)
    return problema("GAUSS-JORDÁN (matriz identidad)\n" + _txt(A, b, ("x1", "x2", "x3")), [
        P("Pivote a22' (tras eliminar columna 1)", M[1][1], "a22' = a22 - (a21/a11)·a12"),
        P("Pivote a33'' (tras eliminar columna 2)", M[2][2], "a33'' = a33' - (a32'/a22')·a23'"),
        P("x1", x1, "Al llegar a la identidad: xi = bi*"), P("x2", x2, "xi = bi*"), P("x3", x3, "xi = bi*")])


def g_gauss():
    A, b, _ = _sistema()
    M, (m21, m31, m32), (x1, x2, x3) = _elim(A, b)
    return problema("ELIMINACIÓN GAUSSIANA (sin pivoteo)\n" + _txt(A, b, ("x1", "x2", "x3")), [
        P("m21 = a21/a11", m21, "m21 = a21 / a11"), P("m31 = a31/a11", m31, "m31 = a31 / a11"),
        P("m32 = a32'/a22'", m32, "m32 = a32' / a22'  (con la matriz ya reducida)"),
        P("x3 (sustitución hacia atrás)", x3, "x3 = b3'' / a33''"), P("x2", x2, "x2 = (b2' - a23'·x3) / a22'"),
        P("x1", x1, "x1 = (b1 - a12·x2 - a13·x3) / a11")])


def calc_iter(A, b, x0, seidel, ej=False):
    x = [float(v) for v in x0]
    pasos = []
    nom = "GAUSS-SEIDEL" if seidel else "JACOBI"
    v = ("a", "b", "c")
    for it in (1, 2):
        old = x[:]
        for i in range(3):
            src = x if seidel else old
            x[i] = (b[i] - sum(A[i][j] * src[j] for j in range(3) if j != i)) / A[i][i]
            pasos.append(P(f"{v[i]}{it}", x[i], f"{v[i]} = (término independiente - otros coeficientes por sus valores) / coef. de {v[i]}" +
                           ("  (usa los valores ya actualizados)" if seidel else "  (usa SOLO los valores de la iteración anterior)")))
    return problema(f"{nom}, valores iniciales a0 = {x0[0]}, b0 = {x0[1]}, c0 = {x0[2]}; haz 2 iteraciones\n" + _txt(A, b), pasos, ej)


def g_jacobi():
    if usar_ejemplo():
        return calc_iter(PDF_A, PDF_B, (1, 1, 1), False, True)
    A, b, _ = _sistema()
    return calc_iter(A, b, (1, 1, 1), False)


def g_seidel():
    if usar_ejemplo():
        return calc_iter(PDF_A, PDF_B, (0, 0, 0), True, True)
    A, b, _ = _sistema()
    return calc_iter(A, b, (0, 0, 0), True)


# ====================== ECUACIONES NO LINEALES ======================
# (texto, f, f', a, b, x0 para Newton)
FN = [("x^3 - 6.5x + 2", lambda x: x ** 3 - 6.5 * x + 2, lambda x: 3 * x * x - 6.5, 0, 1, 0.5),
      ("3x^3 - 2x - 3", lambda x: 3 * x ** 3 - 2 * x - 3, lambda x: 9 * x * x - 2, 1, 2, 1.5),
      ("x^3 + 2x^2 + 10x - 20", lambda x: x ** 3 + 2 * x * x + 10 * x - 20, lambda x: 3 * x * x + 4 * x + 10, 1, 2, 1),
      ("e^(-x) - x", lambda x: math.exp(-x) - x, lambda x: -math.exp(-x) - 1, 0, 1, 0),
      ("x^3 - x - 2", lambda x: x ** 3 - x - 2, lambda x: 3 * x * x - 1, 1, 2, 1.5),
      ("cos(x) - x", lambda x: math.cos(x) - x, lambda x: -math.sin(x) - 1, 0, 1, 0.5)]


def _fn():
    return random.choice(FN)


def g_grafico():
    nom, f, df, a, b, x0 = _fn()
    xs = [a + i * (b - a) / 4 for i in range(5)]
    v = [f(x) for x in xs]
    k = next((i for i in range(4) if v[i] * v[i + 1] <= 0), 0)
    pasos = [P(f"f({fmt(x)})", y, "sustituir x en f(x) (tabla de valores)") for x, y in zip(xs, v)]
    pasos.append(P("x izquierdo del subintervalo donde f cambia de signo", xs[k], "la raíz está donde la gráfica cruza el eje x"))
    return problema(f"MÉTODO GRÁFICO\nf(x) = {nom}\nHaz la tabla en x = {', '.join(fmt(x) for x in xs)}\nY da el x izquierdo del subintervalo con cambio de signo", pasos)


def g_biseccion():
    nom, f, df, a, b, x0 = _fn()
    a0, b0 = a, b
    cs = []
    for _ in range(3):
        c = (a + b) / 2
        cs.append(c)
        if f(a) * f(c) <= 0:
            b = c
        else:
            a = c
    pasos = [P(f"x{i+1} = (a+b)/2", cs[i], "x = (a + b) / 2   (descarta la mitad sin cambio de signo)") for i in range(3)]
    pasos.append(P("Є = |x3 - x2|", abs(cs[2] - cs[1]), "Є = |x(i+1) - x(i)|"))
    return problema(f"BISECTRIZ, 3 iteraciones\nf(x) = {nom}\nIntervalo inicial a = {fmt(a0)}, b = {fmt(b0)}", pasos)


def g_falsa():
    nom, f, df, a, b, x0 = _fn()
    a0 = a
    xs = []
    for _ in range(3):
        x = a - f(a) * (b - a) / (f(b) - f(a))
        xs.append(x)
        a = x
    pasos = [P(f"x{i+1}", xs[i], "x = a - f(a)(b-a) / (f(b) - f(a));  b se queda fijo y a = x anterior") for i in range(3)]
    pasos.append(P("Є = |x3 - x2|", abs(xs[2] - xs[1]), "Є = |x(i+1) - x(i)|"))
    return problema(f"FALSA POSICIÓN (b fijo), 3 iteraciones\nf(x) = {nom}\na = {fmt(a0)}, b = {fmt(b)}", pasos)


def g_newtonraphson():
    nom, f, df, a, b, x0 = _fn()
    x, xs = x0, []
    for _ in range(3):
        x = x - f(x) / df(x)
        xs.append(x)
    pasos = [P(f"x{i+1}", xs[i], "x(i+1) = xi - f(xi) / f'(xi)") for i in range(3)]
    pasos.append(P("Є = |x3 - x2|", abs(xs[2] - xs[1]), "Є = |x(i+1) - x(i)|"))
    return problema(f"NEWTON-RAPHSON, 3 iteraciones\nf(x) = {nom}   (deriva f'(x) tú)\nx0 = {fmt(x0)}", pasos)


GF = [("e^(-x)", lambda x: math.exp(-x), 0), ("cos(x)", math.cos, 0.5), ("sqrt(x + 2)", lambda x: math.sqrt(x + 2), 1),
      ("(x + 1)^(1/3)", lambda x: (x + 1) ** (1 / 3), 1)]


def g_puntofijo():
    nom, g, x = random.choice(GF)
    x0, xs = x, []
    for _ in range(3):
        x = g(x)
        xs.append(x)
    pasos = [P(f"x{i+1}", xs[i], "x(i+1) = g(xi)") for i in range(3)]
    pasos.append(P("Є = |x3 - x2|", abs(xs[2] - xs[1]), "Є = |x(i+1) - x(i)|"))
    return problema(f"PUNTO FIJO, 3 iteraciones\nx(i+1) = g(xi)  con  g(x) = {nom}\nx0 = {fmt(x0)}", pasos)


def g_secante():
    nom, f, df, a, b, x0 = _fn()
    p, q, xs = a, b, []
    for _ in range(3):
        n = q - f(q) * (q - p) / (f(q) - f(p))
        xs.append(n)
        p, q = q, n
    pasos = [P(f"x{i+2}", xs[i], "x(i+1) = xi - f(xi)(xi - x(i-1)) / (f(xi) - f(x(i-1)))") for i in range(3)]
    pasos.append(P("Є = |x4 - x3|", abs(xs[2] - xs[1]), "Є = |x(i+1) - x(i)|"))
    return problema(f"SECANTE, 3 iteraciones\nf(x) = {nom}\nx0 = {fmt(a)}   x1 = {fmt(b)}", pasos)


# ====================== INTEGRACION ======================
INT = [("1 - x^2", lambda x: 1 - x * x, 0, 1), ("e^x", math.exp, 0, 1), ("sin(x)", math.sin, 0, 2),
       ("1/x", lambda x: 1 / x, 1, 3), ("sqrt(x)", math.sqrt, 1, 4), ("1/(1+x^2)", lambda x: 1 / (1 + x * x), 0, 2)]
CERRADAS = {1: (Fraction(1, 2), [1, 1]), 2: (Fraction(1, 3), [1, 4, 1]), 3: (Fraction(3, 8), [1, 3, 3, 1]),
            4: (Fraction(2, 45), [7, 32, 12, 32, 7]), 5: (Fraction(5, 288), [19, 75, 50, 50, 75, 19]),
            6: (Fraction(1, 140), [41, 216, 27, 272, 27, 216, 41])}
ABIERTAS = {1: (Fraction(3, 2), [0, 1, 1, 0]), 2: (Fraction(4, 3), [0, 2, -1, 2, 0]),
            3: (Fraction(5, 24), [0, 11, 1, 1, 11, 0]), 4: (Fraction(6, 20), [0, 11, -14, 26, -14, 11, 0])}


def _integral(titulo, n, pesos, factor, etq, formula_i, h_den=None, f_int=None):
    nom, f, a, b = f_int if (f_int and usar_ejemplo()) else random.choice(INT)
    if f_int and nom == f_int[0]:
        pass
    h = (b - a) / (h_den or n)
    S = sum(w * f(a + i * h) for i, w in enumerate(pesos))
    return problema(f"{titulo}\n∫ de {nom} dx   desde a = {a} hasta b = {b},   n = {n}\n(x = a + i·h)", [
        P("h", h, "h = (b - a) / n" if not h_den else "h = (b - a) / (n + 2)"), P(etq, S, etq),
        P("Integral aproximada I", float(factor) * h * S, formula_i)])


def g_trapecio():
    return _integral("REGLA TRAPEZOIDAL", 4, [1, 2, 2, 2, 1], Fraction(1, 2), "S = f(a) + 2Σf(a+ih) + f(b)", "I = h/2 · S")


def g_simpson13():
    return _integral("REGLA DE 1/3 DE SIMPSON (n par)", 4, [1, 4, 2, 4, 1], Fraction(1, 3), "S = f(a) + 4Σ impares + 2Σ pares + f(b)", "I = h/3 · S")


def g_simpson38():
    return _integral("REGLA DE 3/8 DE SIMPSON", 3, [1, 3, 3, 1], Fraction(3, 8), "S = f(a) + 3Σf(a+ih) + f(b)", "I = 3h/8 · S")


def g_cotes_cerrada():
    n = random.choice([2, 4, 4, 5, 6])
    c, w = CERRADAS[n]
    return _integral(f"NEWTON-COTES CERRADA (n = {n})", n, w, c, "S = Σ wi·f(xi)  con pesos " + str(w), f"I = ({c})·h·S   (constante de la tabla)")


def g_cotes_abierta():
    n = random.choice([2, 3, 4, 4])
    c, w = ABIERTAS[n]
    return _integral(f"NEWTON-COTES ABIERTA (n = {n})", n, w, c, "S = Σ wi·f(xi)  con pesos " + str(w), f"I = ({c})·h·S   (constante de la tabla)", h_den=n + 2)


# ====================== EDO  (y' = f(y, t); k incluyen la h) ======================
EF = [("5yt - 1", lambda y, t: 5 * y * t - 1), ("y + t", lambda y, t: y + t), ("t - y", lambda y, t: t - y),
      ("2yt", lambda y, t: 2 * y * t), ("y - t", lambda y, t: y - t)]


def _edo():
    nom, f = random.choice(EF)
    return nom, f, random.choice([1, 2, 1.2]), random.choice([0, 0.2]), random.choice([0.1, 0.2])


def _en(titulo, nom, y0, t0, h, ej=False):
    return f"{titulo}\ny' = {nom}     y0 = {fmt(y0)}   t0 = {fmt(t0)}   h = {fmt(h)}\nCalcula un paso: y1"


def calc_euler_mod(nom, f, y0, t0, h):
    f0 = f(y0, t0)
    yp = y0 + h * f0
    f1 = f(yp, t0 + h)
    y1 = y0 + h / 2 * (f0 + f1)
    return problema(_en("EULER MODIFICADO (regla trapezoidal)", nom, y0, t0, h) + "\n(para y1 en f(y1,t1) usa primero Euler hacia adelante)", [
        P("f(y0,t0)", f0, "f(y0, t0)"), P("y1 provisional = y0 + h·f(y0,t0)", yp, "y1* = y0 + h·f(y0,t0)"),
        P("f(y1*, t1)", f1, "f(y1*, t0 + h)"), P("y1 = y0 + h/2·[f(y0,t0) + f(y1*,t1)]", y1, "y(n+1) = yn + h/2 [f(yn,tn) + f(y(n+1),t(n+1))]")])


def g_euler_mod():
    if usar_ejemplo():
        return calc_euler_mod("(5yt - 1)/3", lambda y, t: (5 * y * t - 1) / 3, 1.2, 0, 0.2)
    return calc_euler_mod(*_edo())


def calc_rk2(nom, f, y0, t0, h):
    k1 = h * f(y0, t0)
    k2 = h * f(y0 + k1, t0 + h)
    y1 = y0 + (k1 + k2) / 2
    return problema(_en("RUNGE-KUTTA DE 2º ORDEN", nom, y0, t0, h), [
        P("k1 = h·f(y0,t0)", k1, "k1 = h f(yn, tn)"), P("k2 = h·f(y0+k1, t0+h)", k2, "k2 = h f(yn + k1, tn + h)"),
        P("y1 = y0 + 1/2 (k1 + k2)", y1, "y(n+1) = yn + 1/2 (k1 + k2)")])


def g_rk2():
    if usar_ejemplo():
        return calc_rk2("5yt - 1", EF[0][1], 2, 0, 0.2)
    return calc_rk2(*_edo())


def calc_rk3(nom, f, y0, t0, h):
    k1 = h * f(y0, t0)
    k2 = h * f(y0 + k1 / 2, t0 + h / 2)
    k3 = h * f(y0 - k1 + 2 * k2, t0 + h)
    y1 = y0 + (k1 + 4 * k2 + k3) / 6
    return problema(_en("RUNGE-KUTTA DE 3er ORDEN", nom, y0, t0, h), [
        P("k1", k1, "k1 = h f(yn, tn)"), P("k2", k2, "k2 = h f(yn + k1/2, tn + h/2)"),
        P("k3", k3, "k3 = h f(yn - k1 + 2k2, tn + h)"), P("y1 = y0 + 1/6 (k1 + 4k2 + k3)", y1, "y(n+1) = yn + 1/6 (k1 + 4k2 + k3)")])


def g_rk3():
    if usar_ejemplo():
        return calc_rk3("5yt - 1", EF[0][1], 2, 0, 0.2)
    return calc_rk3(*_edo())


def calc_rk4_13(nom, f, y0, t0, h):
    k1 = h * f(y0, t0)
    k2 = h * f(y0 + k1 / 2, t0 + h / 2)
    k3 = h * f(y0 + k2 / 2, t0 + h / 2)
    k4 = h * f(y0 + k3, t0 + h)
    y1 = y0 + (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return problema(_en("RUNGE-KUTTA 4º ORDEN (1/3 de Simpson)", nom, y0, t0, h), [
        P("k1", k1, "k1 = h f(yn, tn)"), P("k2", k2, "k2 = h f(yn + k1/2, tn + h/2)"), P("k3", k3, "k3 = h f(yn + k2/2, tn + h/2)"),
        P("k4", k4, "k4 = h f(yn + k3, tn + h)"), P("y1 = y0 + 1/6 (k1 + 2k2 + 2k3 + k4)", y1, "y(n+1) = yn + 1/6 (k1 + 2k2 + 2k3 + k4)")])


def g_rk4_13():
    if usar_ejemplo():
        return calc_rk4_13("5yt - 1", EF[0][1], 2, 0, 0.2)
    return calc_rk4_13(*_edo())


def calc_rk4_38(nom, f, y0, t0, h):
    k1 = h * f(y0, t0)
    k2 = h * f(y0 + k1 / 3, t0 + h / 3)
    k3 = h * f(y0 + k1 / 3 + k2 / 3, t0 + 2 * h / 3)
    k4 = h * f(y0 + k1 - k2 + k3, t0 + h)
    y1 = y0 + (k1 + 3 * k2 + 3 * k3 + k4) / 8
    return problema(_en("RUNGE-KUTTA 4º ORDEN (3/8 de Simpson)", nom, y0, t0, h), [
        P("k1", k1, "k1 = h f(yn, tn)"), P("k2", k2, "k2 = h f(yn + k1/3, tn + h/3)"),
        P("k3", k3, "k3 = h f(yn + k1/3 + k2/3, tn + 2h/3)"), P("k4", k4, "k4 = h f(yn + k1 - k2 + k3, tn + h)"),
        P("y1 = y0 + 1/8 (k1 + 3k2 + 3k3 + k4)", y1, "y(n+1) = yn + 1/8 (k1 + 3k2 + 3k3 + k4)")])


def g_rk4_38():
    if usar_ejemplo():
        return calc_rk4_38("5yt - 1", EF[0][1], 2, 0, 0.2)
    return calc_rk4_38(*_edo())


def calc_rk_superior(a, b, U, V, q, h, ej=False):
    sa = "+" if a > 0 else "-"
    sb = "+" if b > 0 else "-"
    k1 = h * V
    m1 = h * (a * V * q + b * U)
    k2 = h * (V + m1)
    m2 = h * (a * (V + m1) * (q + h) + b * (U + k1))
    y1 = U + (k1 + k2) / 2
    v1 = V + (m1 + m2) / 2
    return problema(f"RUNGE-KUTTA DE ORDEN SUPERIOR\ny'' = {sa}y'·t {sb} y     y0 = {fmt(U)}   y'0 = {fmt(V)}   t0 = {fmt(q)}   h = {fmt(h)}\n"
                    "(Vn = y',  Un = y,  qn = t)", [
        P("k1 = h·Vn", k1, "k1 = h Vn"), P("m1 = h[a·Vn·qn + b·Un]", m1, "m1 = h [± a Vn qn ± b Un]"),
        P("k2 = h(Vn + m1)", k2, "k2 = h (Vn + m1)"), P("m2 = h[a(Vn+m1)(qn+h) + b(Un+k1)]", m2, "m2 = h [± a (Vn + m1)(qn + h) ± b (Un + k1)]"),
        P("y1 = y0 + 1/2(k1 + k2)", y1, "y(n+1) = yn + 1/2 (k1 + k2)"), P("y'1 = y'0 + 1/2(m1 + m2)", v1, "y'(n+1) = y'n + 1/2 (m1 + m2)")], ej)


def g_rk_superior():
    if usar_ejemplo():
        return calc_rk_superior(1, 1, 1, 2, 0, 0.5, True)
    return calc_rk_superior(random.choice([1, -1]), random.choice([1, -1]), random.randint(1, 2), random.randint(0, 2), random.choice([0, 0.2]), random.choice([0.1, 0.2, 0.5]))


# ====================== CATALOGO (32) ======================
_defs = [
    (0, "Interpolación lineal", g_lineal), (0, "Newton hacia adelante", g_adelante), (0, "Newton hacia atrás", g_atras),
    (0, "Diferencias divididas", g_divididas), (0, "Lagrange", g_lagrange),
    (1, "Línea recta", g_recta), (1, "Cuadrática", g_cuadratica), (1, "Cúbica", g_cubica),
    (1, "Lineal con función", g_funcion), (1, "Cuadrática con función", g_cuad_funcion),
    (2, "Montante", g_montante), (2, "Gauss-Jordán", g_gaussjordan), (2, "Eliminación gaussiana", g_gauss),
    (2, "Gauss-Seidel", g_seidel), (2, "Jacobi", g_jacobi),
    (3, "Regla trapezoidal", g_trapecio), (3, "1/3 de Simpson", g_simpson13), (3, "3/8 de Simpson", g_simpson38),
    (3, "Newton-Cotes cerradas", g_cotes_cerrada), (3, "Newton-Cotes abiertas", g_cotes_abierta),
    (4, "Método gráfico", g_grafico), (4, "Bisectriz", g_biseccion), (4, "Punto fijo", g_puntofijo),
    (4, "Newton-Raphson", g_newtonraphson), (4, "Falsa posición", g_falsa), (4, "Secante", g_secante),
    (5, "Euler modificado", g_euler_mod), (5, "Runge-Kutta 2º orden", g_rk2), (5, "Runge-Kutta 3er orden", g_rk3),
    (5, "Runge-Kutta 4º (1/3)", g_rk4_13), (5, "Runge-Kutta 4º (3/8)", g_rk4_38), (5, "Runge-Kutta orden superior", g_rk_superior),
]
METODOS = [{"id": i, "seccion": s, "nombre": n, "gen": g} for i, (s, n, g) in enumerate(_defs)]
assert len(METODOS) == 32
