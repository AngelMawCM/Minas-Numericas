# Minas Numéricas

32 métodos numéricos (según tus apuntes en PDF)

## Cómo ejecutar (Windows)

1. Python 3.9 o superior (python.org, marca "Add Python to PATH").
2. En una terminal dentro de esta carpeta:

```
python -m pip install pygame-ce
python main.py
```

(o `pygame`, si te instala bien). Si pip no se reconoce: `python -m pip install pygame`

## Crear la app (.exe) con acceso directo en el escritorio (Windows)

1. Ten instalado Python 3.9+ (marca "Add Python to PATH").
2. Doble clic en **`construir_app.bat`**. Tarda 1-2 minutos y hace todo:
   - crea `MinasNumericas.exe` (no necesita Python para abrirse),
   - lo instala en `%LOCALAPPDATA%\Programs\MinasNumericas`,
   - crea el acceso directo **Minas Numericas** en el escritorio y en el menú Inicio,
   - deja una copia para compartir en la carpeta **`Entregable`**.
3. Para compañeros o maestros: manda solo `Entregable\MinasNumericas.exe`. Se abre con doble clic.
   Como el .exe no está firmado, Windows puede mostrar "Windows protegió tu PC": clic en **Más información → Ejecutar de todas formas**.

Cada persona tiene sus propias partidas en `%APPDATA%\MinasNumericas\partidas` (en su usuario de Windows).

## Cómo se juega

- Empiezas con los 5 métodos de Interpolación (rareza Común).
- Elige un método y resuelve cada paso (3 fusibles). Enter = enviar, F1 = fórmula, Esc = salir.
- Margen de error permitido: 2 diez milésimas (0.0002), como en las notas; en valores muy grandes se acepta 0.01 % del valor. Usa al menos 4 decimales.
- Al completar un método puede desbloquearse otro cualquiera. Mientras más difícil la sección completada, más probabilidad de premio y más chance de rarezas altas.
- Rarezas: Interpolación = Común, Mínimos cuadrados = Poco común, Lineales = Raro, Integración = Épico, No lineales = Legendario, EDO = Mítico.
- Botón **COLECCIÓN**: todo lo desbloqueado y cuántas veces completaste cada método.
- Botón **PARTIDAS** (menú principal): hasta 5 ranuras de guardado.
  - CARGAR / NUEVA (ranura vacía) / GUARDAR (copia tu avance actual ahí) / BORRAR.
  - Sobrescribir o borrar pide una segunda pulsación (CONFIRMA).
- Autoguardado: al ganar un método se guarda en tu ranura actual (o en la primera libre). Al abrir el juego se carga la última ranura usada.
- Las partidas viven en `%APPDATA%\MinasNumericas\partidas` (`partida_1.json` ... `partida_5.json`). Para reiniciar todo, borra esa carpeta. Las partidas de versiones anteriores (carpeta `partidas` junto al código o `partida.json`) se pasan solas.

## Archivos

- `main.py` (ventana)
- `logica.py` (reglas)
- `metodos.py` (los 32 métodos)
- `construir_app.bat` (crea el .exe y los accesos directos)
- `icono.ico` / `icono.png` (ícono de la app)
