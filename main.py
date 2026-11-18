"""Minas Numéricas: juego de 32 métodos numéricos. Ejecuta:  python main.py"""
import glob
import math
import os
import random
import sys

import pygame

from logica import RANURAS, Almacen, Ejercicio, Progreso
from metodos import METODOS, SECCIONES

ANCHO, ALTO = 1180, 720
NEGRO = (0, 0, 0)
BLANCO = (240, 240, 240)
GRIS = (90, 90, 100)
RAINBOW = [(255, 80, 80), (255, 160, 40), (255, 230, 60), (90, 230, 90), (70, 200, 255), (170, 110, 255), (255, 100, 200)]
LIMPIAR = {"Σ": "Suma ", "Δ": "Delta", "∇": "Nabla", "²": "^2", "³": "^3", "⁴": "^4", "⁶": "^6", "·": "*", "✔": "OK",
           "■": "#", "□": "-", "≤": "<=", "→": "->", "¡": "!", "¿": "?"}
AQUI = os.path.dirname(os.path.abspath(__file__))


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Minas Numéricas")
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        self.ruta_fuente = None
        for patron in ("*.ttf", "*.otf"):
            hallados = sorted(glob.glob(os.path.join(AQUI, "fuentes", patron)))
            if hallados:
                self.ruta_fuente = hallados[0]
                break
        self.cache = {}
        self.almacen = Almacen()
        activa = self.almacen.activa()
        self.progreso = (activa and self.almacen.cargar(activa)) or Progreso()
        self.resumenes = []  # resumen de cada ranura (se refresca al abrir PARTIDAS)
        self.pendiente = None  # accion de ranura que espera segunda pulsacion (confirmar)
        self.mensaje = ("", BLANCO)
        self.estado = "menu"
        self.ej = None
        self.entrada = ""
        self.aviso = ""
        self.aviso_color = BLANCO
        self.formula = ""
        self.resultado = None  # dict con mensaje final
        self.t = 0.0
        self.estrellas = [[random.randint(0, ANCHO), random.randint(0, ALTO), random.choice(RAINBOW), random.random() * 6] for _ in range(70)]
        self.botones = []  # (rect, accion)

    # ---------- utilidades de dibujo ----------
    def fuente(self, tam):
        if tam not in self.cache:
            if self.ruta_fuente:
                self.cache[tam] = pygame.font.Font(self.ruta_fuente, tam)
            else:
                self.cache[tam] = pygame.font.SysFont("consolas,couriernew,monospace", tam, bold=True)
        return self.cache[tam]

    def texto(self, s, x, y, color=BLANCO, tam=22, centro=False):
        for a, b in LIMPIAR.items():
            s = s.replace(a, b)
        img = self.fuente(tam).render(s, False, color)
        if centro:
            x = x - img.get_width() // 2
        self.pantalla.blit(img, (x, y))
        return img.get_height()

    def envolver(self, s, tam, ancho):
        f = self.fuente(tam)
        salida = []
        for linea in s.split("\n"):
            actual = ""
            for palabra in linea.split(" "):
                prueba = (actual + " " + palabra) if actual else palabra
                if f.size(prueba)[0] <= ancho or not actual:
                    actual = prueba
                else:
                    salida.append(actual)
                    actual = palabra
            salida.append(actual)
        return salida

    def lineas(self, s, x, y, color=BLANCO, tam=22, ancho=ANCHO - 80):
        for linea in self.envolver(s, tam, ancho):
            y += self.texto(linea, x, y, color, tam) + 4
        return y

    def boton(self, rect, etiqueta, accion, color=(70, 120, 220), activo=True):
        raton = pygame.mouse.get_pos()
        r = pygame.Rect(rect)
        encima = r.collidepoint(raton) and activo
        col = tuple(min(255, c + 40) for c in color) if encima else color
        if not activo:
            col = (40, 40, 48)
        pygame.draw.rect(self.pantalla, col, r)
        pygame.draw.rect(self.pantalla, BLANCO if activo else GRIS, r, 3)
        self.texto(etiqueta, r.centerx, r.centery - 11, BLANCO if activo else GRIS, 20, centro=True)
        if activo:
            self.botones.append((r, accion))

    def fondo(self):
        self.pantalla.fill(NEGRO)
        for e in self.estrellas:
            brillo = 0.5 + 0.5 * math.sin(self.t * 2 + e[3])
            c = tuple(int(v * (0.3 + 0.7 * brillo)) for v in e[2])
            pygame.draw.rect(self.pantalla, c, (e[0], e[1], 6, 6))

    def titulo_arcoiris(self, s, y, tam=56):
        ancho = sum(self.fuente(tam).size(ch)[0] for ch in s)
        x = ANCHO // 2 - ancho // 2
        for i, ch in enumerate(s):
            c = RAINBOW[(i + int(self.t * 3)) % len(RAINBOW)]
            img = self.fuente(tam).render(ch, False, c)
            self.pantalla.blit(img, (x, y + int(6 * math.sin(self.t * 3 + i))))
            x += img.get_width()

    # ---------- pantallas ----------
    def dibujar_menu(self):
        self.titulo_arcoiris("MINAS NUMÉRICAS", 110)
        self.texto("32 métodos numéricos por descubrir", ANCHO // 2, 190, (170, 170, 190), 22, True)
        n_des, n_hechos = len(self.progreso.desbloqueados), len([k for k, v in self.progreso.hechos.items() if v])
        self.texto(f"Desbloqueados {n_des}/32     Completados {n_hechos}/32", ANCHO // 2, 235, (255, 230, 60), 20, True)
        self.boton((ANCHO // 2 - 150, 300, 300, 56), "JUGAR", "elegir", (60, 170, 80))
        self.boton((ANCHO // 2 - 150, 375, 300, 56), "COLECCIÓN", "coleccion", (150, 90, 220))
        self.boton((ANCHO // 2 - 150, 450, 300, 56), "PARTIDAS", "partidas", (70, 120, 220))
        self.boton((ANCHO // 2 - 150, 525, 300, 56), "SALIR", "salir", (170, 60, 60))
        slot = self.progreso.slot
        self.texto(f"Partida actual: ranura {slot}" if slot else "Partida actual: sin guardar", ANCHO // 2, 268, (170, 170, 190), 16, True)

    def dibujar_grid(self, jugable):
        self.texto("ELIGE UN MÉTODO" if jugable else "COLECCIÓN", ANCHO // 2, 22, (255, 230, 60), 34, True)
        n_des = len(self.progreso.desbloqueados)
        n_hechos = len([k for k, v in self.progreso.hechos.items() if v])
        self.texto(f"Desbloqueados {n_des}/32     Completados {n_hechos}/32", ANCHO // 2, 58, (255, 230, 60), 16, True)
        ancho_col = (ANCHO - 40) // 6
        for s, (nombre, rareza, color) in enumerate(SECCIONES):
            x = 20 + s * ancho_col
            self.texto(rareza, x + ancho_col // 2 - 6, 80, color, 18, True)
            self.texto(nombre.split("(")[0].strip()[:20], x + ancho_col // 2 - 6, 102, GRIS, 12, True)
            for j, m in enumerate([m for m in METODOS if m["seccion"] == s]):
                r = (x, 135 + j * 78, ancho_col - 12, 68)
                abierto = self.progreso.esta(m["id"])
                hecho = self.progreso.hechos.get(m["id"], 0)
                if abierto:
                    pygame.draw.rect(self.pantalla, tuple(c // 5 for c in color), r)
                    pygame.draw.rect(self.pantalla, color, r, 3 if hecho else 1)
                    yy = r[1] + 6
                    for ln in self.envolver(m["corto"], 14, r[2] - 12)[:2]:
                        yy += self.texto(ln, r[0] + 6, yy, color, 14) + 1
                    self.texto(f"✔ x{hecho}" if hecho else "sin completar", r[0] + 6, r[1] + 46, (255, 230, 60) if hecho else GRIS, 13)
                    if jugable:
                        self.botones.append((pygame.Rect(r), ("jugar", m["id"])))
                else:
                    pygame.draw.rect(self.pantalla, (20, 20, 26), r)
                    pygame.draw.rect(self.pantalla, (50, 50, 60), r, 1)
                    self.texto("???", r[0] + 6, r[1] + 22, (70, 70, 80), 20)
        self.boton((ANCHO // 2 - 90, ALTO - 66, 180, 46), "VOLVER", "menu", (170, 60, 60))

    def dibujar_partidas(self):
        self.texto("PARTIDAS", ANCHO // 2, 22, (255, 230, 60), 34, True)
        self.texto(f"Hasta {RANURAS} partidas guardadas. Tu avance se guarda solo al ganar un método.", ANCHO // 2, 64, GRIS, 16, True)
        for i in range(RANURAS):
            n = i + 1
            res = self.resumenes[i] if i < len(self.resumenes) else None
            y = 100 + i * 98
            activa = self.progreso.slot == n
            borde = (255, 230, 60) if activa else ((90, 90, 110) if res else (50, 50, 60))
            pygame.draw.rect(self.pantalla, (20, 20, 30), (40, y, ANCHO - 80, 84))
            pygame.draw.rect(self.pantalla, borde, (40, y, ANCHO - 80, 84), 3 if activa else 1)
            self.texto(f"RANURA {n}", 60, y + 12, BLANCO if res else GRIS, 24)
            if activa:
                self.texto("(ACTIVA)", 230, y + 14, (255, 230, 60), 20)
            if res:
                self.texto(f"Desbloqueados {res['desbloqueados']}/32   Completados {res['completados']}/32", 60, y + 48, (170, 170, 190), 18)
                if res["fecha"]:
                    self.texto(res["fecha"], 470, y + 14, GRIS, 18)
            else:
                self.texto("- vacía -", 60, y + 48, GRIS, 18)
            botones = [("CARGAR", "cargar", (60, 170, 80)), ("GUARDAR", "guardar", (70, 120, 220)), ("BORRAR", "borrar", (170, 60, 60))]
            if not res:
                botones[0] = ("NUEVA", "nueva", (60, 170, 80))
            for k, (etiqueta, tipo, color) in enumerate(botones):
                esperando = self.pendiente == (tipo, n)
                self.boton((720 + k * 140, y + 17, 130, 50), "CONFIRMA" if esperando else etiqueta, (tipo, n),
                           (220, 140, 30) if esperando else color, activo=not (tipo == "borrar" and not res))
        self.texto(self.mensaje[0], ANCHO // 2, ALTO - 115, self.mensaje[1], 20, True)
        self.boton((ANCHO // 2 - 90, ALTO - 66, 180, 46), "VOLVER", "menu", (170, 60, 60))

    def dibujar_problema(self):
        e = self.ej
        sec = SECCIONES[e.metodo["seccion"]]
        self.texto(f"{e.metodo['nombre']}  [{sec[1]}]", 40, 24, sec[2], 30)
        tam = 22
        if len(self.envolver(e.enunciado, 22, ANCHO - 80)) > 10:
            tam = 17
        y = 80
        for linea in self.envolver(e.enunciado, tam, ANCHO - 80):
            col = (255, 230, 60) if linea.startswith("(Ejemplo") else BLANCO
            y += self.texto(linea, 40, y, col, tam) + 4
        self.texto("Fusibles: " + "■ " * e.fusibles + "□ " * (3 - e.fusibles), 40, ALTO - 300, (255, 80, 80), 24)
        self.texto(f"Paso {e.i + 1} / {len(e.pasos)}:  {e.paso[0]}", 40, ALTO - 260, (255, 230, 60), 24)
        caja = pygame.Rect(40, ALTO - 215, 700, 50)
        pygame.draw.rect(self.pantalla, (25, 25, 35), caja)
        pygame.draw.rect(self.pantalla, (70, 200, 255), caja, 3)
        cursor = "_" if int(self.t * 2) % 2 == 0 else " "
        self.texto(self.entrada + cursor, caja.x + 12, caja.y + 10, BLANCO, 26)
        self.texto(self.aviso, 40, ALTO - 150, self.aviso_color, 22)
        if self.formula:
            self.lineas("Fórmula: " + self.formula, 40, ALTO - 118, (170, 110, 255), 18, ANCHO - 80)
        self.boton((760, ALTO - 215, 140, 50), "ENVIAR", "enviar", (70, 120, 220))
        self.boton((910, ALTO - 215, 120, 50), "FÓRMULA", "formula", (130, 90, 200))
        self.boton((1040, ALTO - 215, 110, 50), "SALIR", "menu", (170, 60, 60))
        self.texto("Enter = enviar   F1 = fórmula   Esc = salir", 40, ALTO - 50, GRIS, 16)

    def dibujar_resultado(self):
        r = self.resultado
        self.titulo_arcoiris(r["titulo"], 120, 44)
        y = 220
        for linea, color in r["lineas"]:
            self.texto(linea, ANCHO // 2, y, color, 26, True)
            y += 44
        self.boton((ANCHO // 2 - 130, ALTO - 150, 260, 56), "CONTINUAR", "elegir", (60, 170, 80))

    # ---------- eventos ----------
    def iniciar(self, mid):
        self.ej = Ejercicio(METODOS[mid])
        self.entrada, self.aviso, self.formula = "", "", ""
        self.estado = "problema"

    def enviar(self):
        e = self.ej
        paso_actual = e.paso
        r = e.responder(self.entrada)
        if r == "invalido":
            self.aviso, self.aviso_color = "Escribe un número válido (con punto decimal).", (255, 160, 40)
        elif r == "ok":
            self.aviso, self.aviso_color = "¡Correcto!", (90, 230, 90)
            self.entrada, self.formula = "", ""
        elif r == "mal":
            self.aviso, self.aviso_color = f"Incorrecto. Te quedan {e.fusibles} fusibles.", (255, 80, 80)
        elif r == "gano":
            nuevo = self.progreso.completar(e.metodo["id"])
            ranura = self.autoguardar()
            lineas = [(f"¡Completaste {e.metodo['nombre']}!", (90, 230, 90))]
            if nuevo is not None:
                m = METODOS[nuevo]
                rar = SECCIONES[m["seccion"]]
                lineas += [("¡NUEVO MÉTODO DESBLOQUEADO!", (255, 230, 60)), (m["nombre"], rar[2]), (f"Rareza: {rar[1]}  ({rar[0]})", rar[2])]
            else:
                lineas.append(("Esta vez no hubo desbloqueo. ¡Sigue intentando!", (170, 170, 190)))
            if ranura:
                lineas.append((f"Partida guardada en la ranura {ranura}", (120, 120, 140)))
            else:
                lineas.append(("No hay ranuras libres: borra una en PARTIDAS para guardar.", (255, 160, 40)))
            self.resultado = {"titulo": "¡VICTORIA!", "lineas": lineas}
            self.estado = "resultado"
        elif r == "perdio":
            self.resultado = {"titulo": "SIN FUSIBLES", "lineas": [
                ("Se acabaron los fusibles.", (255, 80, 80)), (f"Respuesta del paso: {paso_actual[1]}", (255, 230, 60)),
                ("Inténtalo de nuevo (el problema cambia).", (170, 170, 190))]}
            self.estado = "resultado"

    def autoguardar(self):
        """Guarda en la ranura actual (o en la primera libre). Devuelve el numero de ranura o None."""
        n = self.progreso.slot or self.almacen.primer_libre()
        if n is None:
            return None
        return n if self.almacen.guardar(n, self.progreso) else None

    def refrescar(self):
        self.resumenes = [self.almacen.resumen(n) for n in range(1, RANURAS + 1)]

    def accion_ranura(self, tipo, n):
        alm, res = self.almacen, self.almacen.resumen(n)
        if tipo == "borrar":
            confirmar = res is not None
        elif tipo == "guardar":
            confirmar = res is not None and self.progreso.slot != n  # sobrescribir otra partida
        elif tipo in ("cargar", "nueva"):
            confirmar = self.progreso.slot is None and bool(self.progreso.hechos)  # perderias avance sin guardar
        else:
            confirmar = False
        if confirmar and self.pendiente != (tipo, n):
            self.pendiente = (tipo, n)
            aviso = {"borrar": f"Se borrará la ranura {n}. Pulsa CONFIRMA para continuar.",
                     "guardar": f"Se reemplazará la partida de la ranura {n}. Pulsa CONFIRMA.",
                     "cargar": "Tu avance actual no está guardado y se perderá. Pulsa CONFIRMA.",
                     "nueva": "Tu avance actual no está guardado y se perderá. Pulsa CONFIRMA."}[tipo]
            self.mensaje = (aviso, (255, 160, 40))
            return
        self.pendiente = None
        ok = (90, 230, 90)
        if tipo == "cargar":
            p = alm.cargar(n)
            if p is None:
                self.mensaje = (f"La ranura {n} está vacía o dañada.", (255, 80, 80))
            else:
                self.progreso = p
                alm.poner_activa(n)
                self.mensaje = (f"Partida {n} cargada.", ok)
        elif tipo == "nueva":
            self.progreso = Progreso()
            self.mensaje = (f"Partida nueva en la ranura {n}.", ok) if alm.guardar(n, self.progreso) else ("No se pudo guardar.", (255, 80, 80))
        elif tipo == "guardar":
            self.mensaje = (f"Partida guardada en la ranura {n}.", ok) if alm.guardar(n, self.progreso) else ("No se pudo guardar.", (255, 80, 80))
        elif tipo == "borrar":
            era_actual = self.progreso.slot == n
            if alm.borrar(n):
                if era_actual:
                    self.progreso.slot = None
                self.mensaje = (f"Ranura {n} borrada." + (" Tu avance sigue en pantalla sin guardar." if era_actual else ""), ok)
            else:
                self.mensaje = ("No se pudo borrar.", (255, 80, 80))
        self.refrescar()

    def accion(self, a):
        if not (isinstance(a, tuple) and a[0] in ("cargar", "nueva", "guardar", "borrar")):
            self.pendiente = None
        if isinstance(a, tuple) and a[0] in ("cargar", "nueva", "guardar", "borrar"):
            self.accion_ranura(a[0], a[1])
        elif isinstance(a, tuple) and a[0] == "jugar":
            self.iniciar(a[1])
        elif a == "partidas":
            self.mensaje = ("", BLANCO)
            self.refrescar()
            self.estado = "partidas"
        elif a == "elegir":
            self.estado = "elegir"
        elif a == "coleccion":
            self.estado = "coleccion"
        elif a == "menu":
            self.estado = "menu"
        elif a == "enviar":
            self.enviar()
        elif a == "formula":
            self.formula = self.ej.paso[2]
        elif a == "salir":
            pygame.quit()
            sys.exit()

    def evento(self, ev):
        if ev.type == pygame.QUIT:
            self.accion("salir")
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for rect, a in list(self.botones):
                if rect.collidepoint(ev.pos):
                    self.accion(a)
                    break
        elif ev.type == pygame.KEYDOWN:
            if self.estado == "problema":
                if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.enviar()
                elif ev.key == pygame.K_BACKSPACE:
                    self.entrada = self.entrada[:-1]
                elif ev.key == pygame.K_F1:
                    self.formula = self.ej.paso[2]
                elif ev.key == pygame.K_ESCAPE:
                    self.estado = "elegir"
                elif ev.unicode and ev.unicode in "0123456789.-" and len(self.entrada) < 20:
                    self.entrada += ev.unicode
            elif ev.key == pygame.K_ESCAPE:
                self.estado = "menu" if self.estado != "resultado" else "elegir"
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.estado == "resultado":
                self.estado = "elegir"

    def correr(self):
        while True:
            self.t += self.reloj.tick(60) / 1000
            for ev in pygame.event.get():
                self.evento(ev)
            self.botones = []
            self.fondo()
            if self.estado == "menu":
                self.dibujar_menu()
            elif self.estado == "elegir":
                self.dibujar_grid(True)
            elif self.estado == "coleccion":
                self.dibujar_grid(False)
            elif self.estado == "partidas":
                self.dibujar_partidas()
            elif self.estado == "problema":
                self.dibujar_problema()
            elif self.estado == "resultado":
                self.dibujar_resultado()
            pygame.display.flip()


if __name__ == "__main__":
    App().correr()
