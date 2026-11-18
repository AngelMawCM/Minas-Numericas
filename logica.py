"""Reglas del juego (sin graficos): ejercicios, fusibles, desbloqueos y guardado en 5 ranuras."""
import json
import os
import random
import shutil
import time

from metodos import METODOS, SECCIONES

AQUI = os.path.dirname(os.path.abspath(__file__))


def carpeta_datos():
    """Carpeta de datos de CADA usuario: en Windows %APPDATA%\\MinasNumericas.
    Asi cada persona tiene sus propias partidas y no se pierden al usar el .exe."""
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, "MinasNumericas")


CARPETA = os.path.join(carpeta_datos(), "partidas")  # aqui viven las ranuras partida_1.json ... partida_5.json
CARPETA_VIEJA = os.path.join(AQUI, "partidas")  # donde se guardaba antes (junto al codigo)
ARCHIVO_VIEJO = os.path.join(AQUI, "partida.json")  # version anterior (una sola partida)
RANURAS = 5
FUSIBLES = 3
BASE_PESOS = [40, 28, 18, 9, 4, 1]  # que tan comun es sacar cada seccion


def leer_numero(t):
    t = t.strip()
    try:
        if t and t[0] in "-0123456789." and not t.lower().startswith(("0x", "inf", "nan")):
            return float(t)
    except ValueError:
        pass
    return None


class Ejercicio:
    def __init__(self, metodo):
        self.metodo = metodo
        p = metodo["gen"]()
        self.enunciado, self.pasos = p["enunciado"], p["pasos"]
        self.i, self.fusibles, self.fin, self.gano = 0, FUSIBLES, False, False

    @property
    def paso(self):
        return self.pasos[self.i]

    def responder(self, texto):
        """Devuelve 'invalido', 'ok', 'mal', 'gano' o 'perdio'."""
        v = leer_numero(texto)
        if v is None or self.fin:
            return "invalido"
        esperado = self.paso[1]
        # notas: "El margen de error permitido es de 2 diez milesimas" (0.0002);
        # en sumas muy grandes (minimos cuadrados) se permite 0.01 % del valor
        if abs(v - esperado) <= max(0.0002, abs(esperado) * 0.0001):
            self.i += 1
            if self.i >= len(self.pasos):
                self.fin = self.gano = True
                return "gano"
            return "ok"
        self.fusibles -= 1
        if self.fusibles <= 0:
            self.fin = True
            return "perdio"
        return "mal"


class Progreso:
    def __init__(self, rng=None):
        self.rng = rng or random
        self.desbloqueados = [m["id"] for m in METODOS if m["seccion"] == 0]  # empiezas con Interpolacion
        self.hechos = {}  # id -> veces completado
        self.orden = []  # ids conseguidos en orden (sin los iniciales)
        self.slot = None  # ranura donde se guarda esta partida (None = sin guardar)
        self.fecha = ""  # cuando se guardo por ultima vez (solo informativo)

    def esta(self, mid):
        return mid in self.desbloqueados

    def prob_desbloqueo(self, seccion):
        return min(0.9, 0.30 + 0.07 * seccion)  # mas dificil -> mas chance de premio

    def pesos(self, seccion):
        # exponente < 1 aplana la tabla: al completar secciones dificiles, lo raro es menos raro
        exp = 1 - 0.12 * seccion
        return [b ** exp for b in BASE_PESOS]

    def completar(self, mid):
        """Registra el metodo completado y tira el dado. Devuelve el id desbloqueado o None."""
        self.hechos[mid] = self.hechos.get(mid, 0) + 1
        sec = METODOS[mid]["seccion"]
        if self.rng.random() > self.prob_desbloqueo(sec):
            return None
        candidatos = [m for m in METODOS if m["id"] not in self.desbloqueados]
        if not candidatos:
            return None
        pesos = self.pesos(sec)
        elegido = self.rng.choices(candidatos, weights=[pesos[m["seccion"]] for m in candidatos])[0]
        self.desbloqueados.append(elegido["id"])
        self.orden.append(elegido["id"])
        return elegido["id"]


class Almacen:
    """Maneja las 5 ranuras de guardado (archivos JSON dentro de la carpeta 'partidas')."""

    def __init__(self, carpeta=CARPETA, viejo=ARCHIVO_VIEJO):
        self.carpeta = carpeta
        self.viejo = viejo
        self._migrar()

    def ruta(self, n):
        return os.path.join(self.carpeta, f"partida_{n}.json")

    def _ruta_activa(self):
        return os.path.join(self.carpeta, "activa.txt")

    def _migrar(self):
        """Pasa las partidas de versiones anteriores a la carpeta del usuario."""
        try:  # partidas que estaban junto al codigo -> carpeta del usuario (solo si aun no hay ninguna)
            if (self.carpeta == CARPETA and os.path.isdir(CARPETA_VIEJA) and not os.path.isdir(self.carpeta)):
                shutil.copytree(CARPETA_VIEJA, self.carpeta)
        except OSError:
            pass
        try:  # partida.json de la primera version -> ranura 1
            if not self.viejo or not os.path.exists(self.viejo) or os.path.exists(self.ruta(1)):
                return
            with open(self.viejo, encoding="utf-8") as f:
                d = json.load(f)
            p = self._armar(d)
            if p is not None and self.guardar(1, p):
                os.replace(self.viejo, os.path.join(os.path.dirname(self.viejo), "partida_vieja.json"))
        except (OSError, ValueError):
            pass

    @staticmethod
    def _armar(d):
        """Valida un diccionario leido del disco y construye un Progreso (o None si esta danado)."""
        try:
            n = len(METODOS)
            des = [int(i) for i in d["desbloqueados"]]
            hechos = {int(k): int(v) for k, v in d["hechos"].items()}
            orden = [int(i) for i in d.get("orden", [])]
        except (KeyError, TypeError, ValueError, AttributeError):
            return None
        if any(not 0 <= i < n for i in des + list(hechos) + orden) or any(v < 0 for v in hechos.values()):
            return None
        p = Progreso()
        vistos = list(p.desbloqueados)  # Interpolacion siempre esta desbloqueada
        for i in des:
            if i not in vistos:
                vistos.append(i)
        p.desbloqueados = vistos
        p.hechos = {k: v for k, v in hechos.items() if v}
        p.orden = [i for i in dict.fromkeys(orden) if i in vistos]
        return p

    def cargar(self, n):
        """Devuelve el Progreso de la ranura n, o None si esta vacia o danada."""
        try:
            with open(self.ruta(n), encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            return None
        p = self._armar(d) if isinstance(d, dict) else None
        if p is not None:
            p.slot = n
            f = d.get("guardado", "")
            p.fecha = f if isinstance(f, str) else ""
        return p

    def resumen(self, n):
        p = self.cargar(n)
        if p is None:
            return None
        return {"desbloqueados": len(p.desbloqueados), "completados": len(p.hechos), "fecha": p.fecha}

    def guardar(self, n, progreso):
        """Escribe el progreso en la ranura n y la marca como activa. True si se pudo."""
        if not 1 <= n <= RANURAS:
            return False
        datos = {"version": 2, "desbloqueados": progreso.desbloqueados, "hechos": progreso.hechos,
                 "orden": progreso.orden, "guardado": time.strftime("%d/%m/%Y %H:%M")}
        try:
            os.makedirs(self.carpeta, exist_ok=True)
            tmp = self.ruta(n) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(datos, f)
            os.replace(tmp, self.ruta(n))  # reemplazo atomico: nunca queda un archivo a medias
        except OSError:
            return False
        progreso.slot = n
        self.poner_activa(n)
        return True

    def borrar(self, n):
        try:
            os.remove(self.ruta(n))
        except OSError:
            return False
        if self.activa() is None:
            try:
                os.remove(self._ruta_activa())
            except OSError:
                pass
        return True

    def primer_libre(self):
        for n in range(1, RANURAS + 1):
            if not os.path.exists(self.ruta(n)):
                return n
        return None

    def poner_activa(self, n):
        try:
            os.makedirs(self.carpeta, exist_ok=True)
            with open(self._ruta_activa(), "w", encoding="utf-8") as f:
                f.write(str(n))
        except OSError:
            pass

    def activa(self):
        """Ranura de la ultima partida usada (solo si todavia existe y es valida)."""
        try:
            with open(self._ruta_activa(), encoding="utf-8") as f:
                n = int(f.read().strip())
        except (OSError, ValueError):
            return None
        return n if 1 <= n <= RANURAS and self.cargar(n) is not None else None
