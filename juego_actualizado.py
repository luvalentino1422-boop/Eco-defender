import pygame
import math
import sys
import os
import random
from datetime import datetime
# Carpeta base (donde está el script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from informe import generar_matriz_informe
matriz = generar_matriz_informe()
print(matriz)

import os
from openai import OpenAI

# Inicializa el cliente con la API de Poe
client = OpenAI(
    api_key=os.getenv("POE_API_KEY"),
    base_url="https://poe.com/General_defenders",
)

def obtener_respuesta_poe(mensaje):
    """
    Envía un mensaje a Poe y devuelve la respuesta del modelo.
    """
    try:
        response = client.chat.completions.create(
            model="General_defenders",  # o el modelo que uses
            messages=[{"role": "user", "content": mensaje}],
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print("Error al comunicarse con Poe:", e)
        return "Hubo un error al contactar con la IA."


# ---------------------------
# Configuración para guardar impactos en archivo TXT
# ---------------------------
usuario_actual = None
LOG_FILE = os.path.join(BASE_DIR, "impactos_chispas.txt")

def registrar_chispa(x, y, frame, tipo="Desconocido"):
    global usuario_actual
    tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if usuario_actual:
        user_id, user_name = usuario_actual
    else:
        user_id, user_name = 0, "Desconocido"

    with open(LOG_FILE, mode="a", encoding="utf-8") as f:
        f.write(f"[{tiempo}] ID:{user_id} Usuario:{user_name} Frame:{frame} Pos({round(x,2)}, {round(y,2)}) Tipo:{tipo}\n")
# ---------------------------
# Captura de nombre de usuario
# ---------------------------
def pedir_usuario():
    global usuario_actual
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Ingrese su nombre")
    font = pygame.font.Font(None, 36)
    font_label = pygame.font.Font(None, 28)  # Fuente para el mensaje guía

    usuario = ""
    input_rect = pygame.Rect(300, 200, 200, 40)
    color_inactive = (100, 100, 100)
    color_active = (255, 255, 255)
    color = color_inactive
    active = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                    color = color_active
                else:
                    active = False
                    color = color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if usuario.strip():
                            jugador_id = guardar_usuario(usuario)
                            usuario_actual = (jugador_id, usuario)  # ID + nombre
                            return usuario
                    elif event.key == pygame.K_BACKSPACE:
                        usuario = usuario[:-1]
                    else:
                        usuario += event.unicode

        screen.fill((0, 0, 0))

        # Texto guía
        label = font_label.render("Ingrese un usuario:", True, BLANCO)
        screen.blit(label, (input_rect.x, input_rect.y - 30))  # 30 px arriba del input

        # Texto del usuario
        txt_surface = font.render(usuario, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_rect.w = width
        screen.blit(txt_surface, (input_rect.x + 5, input_rect.y + 5))
        pygame.draw.rect(screen, color, input_rect, 2)

        pygame.display.flip()

# ---------------------------
# Guardar usuario en archivo
# ---------------------------
def guardar_usuario(nombre):
    ruta = os.path.join(BASE_DIR, "usuarios.txt")

    # Leer último ID
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        ultimo_id = len(lineas)  # cada línea es un usuario
    else:
        ultimo_id = 0

    nuevo_id = ultimo_id + 1

    with open(ruta, "a", encoding="utf-8") as f:
        f.write(f"{nuevo_id};{nombre}\n")  # Guardar como ID;Nombre

    return nuevo_id

# ---------------------------
# Configuración base
# ---------------------------
ANCHO, ALTO = 1280, 720
FPS = 60
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
GRIS = (128, 128, 128)
AMARILLO = (255, 255, 0)
NARANJA = (255, 165, 0)
ARENA = (194, 178, 128)
MAR = (70, 130, 180)
BUNKER = (100, 100, 100)

# Posiciones de las cabras checas (también usadas para colisión)
CABRAS_POS = [
    (300, 150),
    (600, 400),
    (500, 680),
    (550, 50),
    (230, 700),
]

cabras_checas_rects = [
    pygame.Rect(x - 30, y - 30, 60, 60) for x, y in CABRAS_POS
]

# Posiciones y tamaños de las ventanas del bunker (x, y, ancho, alto)
VENTANAS_INFO = [
    (150, 0, 30, 100),
    (150, 200, 30, 100),
    (150, 400, 30, 100),
    (150, 600, 30, 100),
]

# Posiciones de enemigos (x, y)
ENEMIGOS_POS = [
    (1000, 150),
    (1100, 400),
    (1050, 650),
]

# ---------------------------
# Utilidad: cargar imagen con ruta segura
# ---------------------------
def cargar_sprite(nombre_archivo, tamaño):
    base, ext = os.path.splitext(nombre_archivo)
    posibles = []
    if ext:
        posibles.append(os.path.join(BASE_DIR, nombre_archivo))
        if ext.lower() in (".png", ".jpg", ".jpeg"):
            alt_ext = ".png" if ext.lower() in (".jpg", ".jpeg") else ".jpg"
            posibles.append(os.path.join(BASE_DIR, base + alt_ext))
    else:
        posibles.append(os.path.join(BASE_DIR, nombre_archivo + ".png"))
        posibles.append(os.path.join(BASE_DIR, nombre_archivo + ".jpg"))

    last_error = None
    for ruta in posibles:
        if not os.path.exists(ruta):
            continue
        try:
            img = pygame.image.load(ruta)
            try:
                img = img.convert_alpha()
            except Exception:
                img = img.convert()
            img = pygame.transform.smoothscale(img, tamaño)
            return img, None
        except Exception as e:
            last_error = e

    w, h = tamaño
    ph = pygame.Surface((w, h), pygame.SRCALPHA)
    ph.fill((30, 120, 220, 255))
    pygame.draw.line(ph, (255, 255, 255), (0, 0), (w, h), 3)
    pygame.draw.line(ph, (255, 255, 255), (w, 0), (0, h), 3)
    err_msg = f"No se pudo cargar ninguna de las rutas: {posibles}. Ultimo error: {last_error}"
    return ph, err_msg


# ---------------------------s
# Clase Jugador
# ---------------------------
class Jugador:
    def __init__(self):
        self.imagen, self.error = cargar_sprite("jugador.png", (60, 120))
        self.rect = self.imagen.get_rect(center=(100, 300))
        self.vel = 5
        self.vida = 10  # Vida del jugador

    def mover(self, teclas):
        if teclas[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.vel
        if teclas[pygame.K_s] and self.rect.bottom < ALTO:
            self.rect.y += self.vel

    def dibujar(self, win):
        win.blit(self.imagen, self.rect)

    def recibir_danio(self):
        self.vida -= 1
        print(f"Jugador recibió daño! Vida restante: {self.vida}")

    def esta_vivo(self):
        return self.vida > 0

# ---------------------------
# Clase Proyectil
# ---------------------------
class Proyectil:
    def __init__(self, x, y, destino, color=AMARILLO):
        self.x = float(x)
        self.y = float(y)
        self.vel = 12
        dx = destino[0] - self.x
        dy = destino[1] - self.y
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            distancia = 1.0
        self.dx = dx / distancia
        self.dy = dy / distancia
        self.radio = 4
        self.color = color

    def mover(self):
        self.x += self.dx * self.vel
        self.y += self.dy * self.vel

    def dibujar(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radio)

    def fuera_de_pantalla(self):
        return self.x < 0 or self.x > ANCHO or self.y < 0 or self.y > ALTO

    def get_rect(self):
        return pygame.Rect(int(self.x - self.radio), int(self.y - self.radio), self.radio * 2, self.radio * 2)

# ---------------------------
# Clase Chispa
# ---------------------------
class Chispa:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = random.uniform(0, 2 * math.pi)
        self.vel = random.uniform(2, 6)
        self.tiempo_vida = 20  # frames
        self.color = random.choice([(255, 255, 100), (255, 200, 50), (255, 255, 0)])

    def mover(self):
        self.x += math.cos(self.angulo) * self.vel
        self.y += math.sin(self.angulo) * self.vel
        self.tiempo_vida -= 1 

    def dibujar(self, surface):
        if self.tiempo_vida > 0:
            end_x = self.x + math.cos(self.angulo) * 5
            end_y = self.y + math.sin(self.angulo) * 5
            pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), 2)

    def esta_muerto(self):
        return self.tiempo_vida <= 0

# ---------------------------
# Clase Ventana (del bunker)
# ---------------------------
class Ventana:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.vida = 600
        self.visible = True

    def recibir_impacto(self):
        self.vida -= 1
        if self.vida <= 0:
            self.visible = False

    def dibujar(self, superficie):
        if self.visible:
            pygame.draw.rect(superficie, (180, 180, 180), self.rect)
            pygame.draw.rect(superficie, (100, 100, 100), self.rect, 2)

# ---------------------------
# Clase Enemigo
# ---------------------------
class Enemigo:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vel = 2  # Velocidad horizontal
        self.direccion = 1  # 1 = derecha, -1 = izquierda

        self.limite_izquierdo = x - 100  # Puedes ajustar
        self.limite_derecho = x + 100

        self.imagen, self.error = cargar_sprite("basura.jpg", (50, 50))
        self.rect = self.imagen.get_rect(center=(self.x, self.y))
        
        self.tiempo_disparo = 0
        self.intervalo_disparo = 120
        self.vida = 100    
        self.vivo = True
        
    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0:
            self.vivo = False
        
    def actualizar(self, jugador_pos, proyectiles_enemigos, frame):
        # Movimiento de patrulla izquierda-derecha
        self.x += self.vel * self.direccion

        if self.x >= self.limite_derecho:
            self.direccion = -1
        elif self.x <= self.limite_izquierdo:
            self.direccion = 1

        self.rect.center = (int(self.x), int(self.y))
        self.pos = self.rect.center

        # Disparo
        self.tiempo_disparo += 1
        if self.tiempo_disparo >= self.intervalo_disparo:
            self.tiempo_disparo = 0
            proyectiles_enemigos.append(
                Proyectil(self.rect.centerx, self.rect.centery, jugador_pos, color=ROJO)
            )

    def dibujar(self, superficie):
        superficie.blit(self.imagen, self.rect)
        # Dibujar barra de vida
        vida_max = 100
        ancho_barra = self.rect.width
        alto_barra = 5
        vida_actual = max(0, self.vida)
        ancho_vida = int((vida_actual / vida_max) * ancho_barra)
        barra_vida_rect = pygame.Rect(self.rect.left, self.rect.top - 10, ancho_barra, alto_barra)
        barra_actual_rect = pygame.Rect(self.rect.left, self.rect.top - 10, ancho_vida, alto_barra)
        pygame.draw.rect(superficie, (255, 0, 0), barra_vida_rect)
        pygame.draw.rect(superficie, (0, 255, 0), barra_actual_rect)

class EnemigoAleatorio:
    def __init__(self, x, y):  # ← Este es el constructor
        self.x = float(x)
        self.y = float(y)
        self.vel = 1.8
        self.direccion = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.imagen, self.error = cargar_sprite("basura.jpg", (50, 50))
        self.rect = self.imagen.get_rect(center=(self.x, self.y))

        self.tiempo_disparo = 0
        self.intervalo_disparo = 100
        self.vida = 75
        self.vivo = True

        self.tiempo_cambio = 0
        self.intervalo_cambio = random.randint(60, 180)

        print(f"EnemigoAleatorio creado en posición inicial: ({self.x}, {self.y})")

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0:
            self.vivo = False

    def actualizar(self, jugador_pos, proyectiles_enemigos, frame):
        # Movimiento aleatorio
        self.tiempo_cambio += 1
        if self.tiempo_cambio >= self.intervalo_cambio:
            self.tiempo_cambio = 0
            self.intervalo_cambio = random.randint(60, 180)
            self.direccion = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

        self.x += self.direccion.x * self.vel
        self.y += self.direccion.y * self.vel

        # Limitar dentro de la pantalla
        self.x = max(200, min(ANCHO - 60, self.x))  # Evita que se meta en el bunker o fuera
        self.y = max(10, min(ALTO - 60, self.y))

        self.rect.center = (int(self.x), int(self.y))

        # Disparo
        self.tiempo_disparo += 1
        if self.tiempo_disparo >= self.intervalo_disparo:
            self.tiempo_disparo = 0
            proyectiles_enemigos.append(
                Proyectil(self.rect.centerx, self.rect.centery, jugador_pos, color=NARANJA)
            )

    def dibujar(self, superficie):
        superficie.blit(self.imagen, self.rect)
        # Dibujar barra de vida
        vida_max = 75
        ancho_barra = self.rect.width
        alto_barra = 5
        vida_actual = max(0, self.vida)
        ancho_vida = int((vida_actual / vida_max) * ancho_barra)
        barra_vida_rect = pygame.Rect(self.rect.left, self.rect.top - 10, ancho_barra, alto_barra)
        barra_actual_rect = pygame.Rect(self.rect.left, self.rect.top - 10, ancho_vida, alto_barra)
        pygame.draw.rect(superficie, (255, 0, 0), barra_vida_rect)
        pygame.draw.rect(superficie, (255, 165, 0), barra_actual_rect)
        
# ---------------------------
# Dibujo de mira
# ---------------------------
def dibujar_mira(win):
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(win, BLANCO, (mx, my), 10, 1)
    pygame.draw.line(win, BLANCO, (mx - 12, my), (mx + 12, my), 1)
    pygame.draw.line(win, BLANCO, (mx, my - 12), (mx, my + 12), 1)

# ---------------------------
# Dibujo del fondo
# ---------------------------
def dibujar_fondo(win, frame):
    pygame.draw.rect(win, ARENA, (0, 0, ANCHO, ALTO))
    ancho_mar = ANCHO // 3
    for y in range(0, ALTO, 10):
        offset = int(7 * math.sin((y * 0.03) + frame * 0.05))
        pygame.draw.rect(win, MAR, (ANCHO - ancho_mar + offset, y, ancho_mar, 10))
    pygame.draw.rect(win, BUNKER, (0, 0, 180, 720))
    pygame.draw.rect(win, NEGRO, (1250, 0, 1280, 720))
    for x, y in CABRAS_POS:
        dibujar_cabra_checa(win, x, y)

def dibujar_cabra_checa(surface, centro_x, centro_y):
    color_viga = (90, 30, 30)
    largo = 100
    grosor = 20
    def dibujar_viga(x, y, angulo):
        viga = pygame.Surface((largo, grosor), pygame.SRCALPHA)
        pygame.draw.rect(viga, color_viga, (0, 0, largo, grosor))
        viga_rotada = pygame.transform.rotate(viga, angulo)
        rect_rotado = viga_rotada.get_rect(center=(x, y))
        surface.blit(viga_rotada, rect_rotado)
    dibujar_viga(centro_x, centro_y, 0)
    dibujar_viga(centro_x, centro_y, 60)
    dibujar_viga(centro_x, centro_y, -60)
    pygame.draw.circle(surface, (60, 60, 60), (centro_x, centro_y), 8)
    
def dibujar_boton(texto, x, y, ancho, alto, fuente, ventana, color_normal=GRIS, color_hover=(170, 170, 170)):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect_boton = pygame.Rect(x, y, ancho, alto)
    if rect_boton.collidepoint(mouse):
        pygame.draw.rect(ventana, color_hover, rect_boton)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(ventana, color_normal, rect_boton)
    texto_render = fuente.render(texto, True, BLANCO)
    text_rect = texto_render.get_rect(center=rect_boton.center)
    ventana.blit(texto_render, text_rect)
    return False

def mostrar_menu_inicio():
    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Menú Principal")
    clock = pygame.time.Clock()
    fuente_titulo = pygame.font.Font(None, 72)
    fuente_boton = pygame.font.Font(None, 36)
    titulo = fuente_titulo.render("Defender la posición", True, BLANCO)
    rect_titulo = titulo.get_rect(center=(ANCHO // 2, 150))
    print("avance")
    while True:
        clock.tick(FPS)
        ventana.fill((20, 20, 20))
        ventana.blit(titulo, rect_titulo)
        jugar = dibujar_boton("Jugar", ANCHO // 2 - 100, 300, 200, 50, fuente_boton, ventana)
        opciones = dibujar_boton("Opciones", ANCHO // 2 - 100, 380, 200, 50, fuente_boton, ventana)
        salir = dibujar_boton("Salir", ANCHO // 2 - 100, 460, 200, 50, fuente_boton, ventana)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if jugar:
            mostrar_menu_niveles()  # ← en vez de llamar a main() directamente
        elif salir:
            pygame.quit()
            sys.exit()
        elif opciones:
              mostrar_menu_opciones()
        
        pygame.display.flip()

def mostrar_menu_niveles():
    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Seleccionar Nivel")
    clock = pygame.time.Clock()
    bunker_rect = pygame.Rect(0, 0, 180, ALTO)

    fuente_titulo = pygame.font.Font(None, 60)
    fuente_boton = pygame.font.Font(None, 36)

    titulo = fuente_titulo.render("Selecciona un Nivel", True, BLANCO)
    rect_titulo = titulo.get_rect(center=(ANCHO // 2, 150))

    while True:
        clock.tick(FPS)
        ventana.fill((25, 25, 25))
        ventana.blit(titulo, rect_titulo)

        if dibujar_boton("Nivel 1", ANCHO//2 - 300, 300, 150, 50, fuente_boton, ventana):
            main(nivel=1)
            return
        if dibujar_boton("Nivel 2", ANCHO//2 - 75, 300, 150, 50, fuente_boton, ventana):
            main(nivel=2)
            return
        if dibujar_boton("Nivel 3", ANCHO//2 + 150, 300, 150, 50, fuente_boton, ventana):
            main(nivel=3)
            return
        if dibujar_boton("Volver", ANCHO//2 - 75, 450, 150, 50, fuente_boton, ventana):
            return

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

# ---------------------------
# Función principal
# ---------------------------
def main(nivel=1):
    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Defender la posición")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    jugador = Jugador()
    proyectiles_jugador = []
    proyectiles_enemigos = []
    chispas = []
    mensaje_error = jugador.error
    frame = 0

    ventanas = [Ventana(x, y, w, h) for x, y, w, h in VENTANAS_INFO]

    # Crear enemigos segun nivel, mezclando tipos
    if nivel == 1:
        enemigos = [
            Enemigo(1000, 150),
            EnemigoAleatorio(1100, 400),
        ]
    elif nivel == 2:
        enemigos = [
            EnemigoAleatorio(900, 150),
            Enemigo(950, 300),
            EnemigoAleatorio(1000, 500),
        ]
    elif nivel == 3:
        enemigos = [
            Enemigo(900, 100),
            EnemigoAleatorio(950, 250),
            Enemigo(1000, 400),
            EnemigoAleatorio(1050, 550),
        ]
    else:
        enemigos = [
            Enemigo(1000, 150),
            EnemigoAleatorio(1100, 400),
        ]

    # **RETIRAR esta línea** que sobrescribe enemigos:
    # enemigos = [Enemigo(x, y) for x, y in ENEMIGOS_POS]

    # Luego sigue el bucle
    corriendo = True
    while corriendo:
        clock.tick(FPS)
        frame += 1
        # … resto del código sin cambios significativos …
        # actualizas enemigos incluyendo EnemigoAleatorio
        for enemigo in enemigos:
            enemigo.actualizar(jugador.rect.center, proyectiles_enemigos, frame)
        enemigos = [e for e in enemigos if e.vivo]
        # dibujas enemigos
        for enemigo in enemigos:
            enemigo.dibujar(ventana)
        # …

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                corriendo = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                destino = pygame.mouse.get_pos()
                proyectiles_jugador.append(
                    Proyectil(jugador.rect.centerx, jugador.rect.centery, destino, color=AMARILLO)
                )

        teclas = pygame.key.get_pressed()
        jugador.mover(teclas)

        # Actualizar proyectiles jugador
        for p in proyectiles_jugador[:]:
            p.mover()
            impacto = False
            for rect in cabras_checas_rects:
                if p.get_rect().colliderect(rect):
                    proyectiles_jugador.remove(p)
                    impacto = True
                    for _ in range(10):
                        chispas.append(Chispa(p.x, p.y))
                    break
            if impacto:
                continue
            for enemigo in enemigos:
                if enemigo.rect.colliderect(p.get_rect()):
                    enemigo.recibir_dano(25)
                    proyectiles_jugador.remove(p)
                    for _ in range(10):
                        chispas.append(Chispa(p.x, p.y))
                        registrar_chispa(p.x, p.y, frame, tipo="Enemigo")
                    break
            if not impacto:
                for ventana_obj in ventanas:
                    if ventana_obj.visible and p.get_rect().colliderect(ventana_obj.rect):
                        ventana_obj.recibir_impacto()
                        proyectiles_jugador.remove(p)
                        impacto = True
                        for _ in range(10):
                            chispas.append(Chispa(p.x, p.y))
                        break
            if p in proyectiles_jugador and p.fuera_de_pantalla():
                proyectiles_jugador.remove(p)

        # Actualizar proyectiles enemigos
        for p in proyectiles_enemigos[:]:
            p.mover()
            rect_p = p.get_rect()

            if rect_p.colliderect(jugador.rect):
                proyectiles_enemigos.remove(p)
                jugador.recibir_danio()
                for _ in range(15): chispas.append(Chispa(p.x, p.y))
                continue
            # Colisión con ventanas
            for ventana_obj in ventanas:
                if ventana_obj.visible and rect_p.colliderect(ventana_obj.rect):
                    ventana_obj.recibir_impacto()
                    proyectiles_enemigos.remove(p)
                    for _ in range(10): 
                        chispas.append(Chispa(p.x, p.y))
                    break

            # Colisión con cabras checas
            choco_cabra = False
            for rect in cabras_checas_rects:
                if rect_p.colliderect(rect):
                    proyectiles_enemigos.remove(p)
                    choco_cabra = True
                    for _ in range(10): chispas.append(Chispa(p.x, p.y))
                    break
            if choco_cabra: continue

     

            if p.fuera_de_pantalla():
                proyectiles_enemigos.remove(p)

        # Actualizar enemigos
        for enemigo in enemigos:
            enemigo.actualizar(jugador.rect.center, proyectiles_enemigos, frame)
        enemigos = [e for e in enemigos if e.vivo]

        # Actualizar chispas
        for chispa in chispas[:]:
            chispa.mover()
            if chispa.esta_muerto():
                chispas.remove(chispa)

        # Dibujar todo
        dibujar_fondo(ventana, frame)
        for ventana_obj in ventanas:
            ventana_obj.dibujar(ventana)
        jugador.dibujar(ventana)
        for enemigo in enemigos:
            enemigo.dibujar(ventana)
        for p in proyectiles_jugador:
            p.dibujar(ventana)
        for p in proyectiles_enemigos:
            p.dibujar(ventana)
        for chispa in chispas:
            chispa.dibujar(ventana)
        dibujar_mira(ventana)

        if mensaje_error:
            aviso = font.render(mensaje_error, True, BLANCO)
            ventana.blit(aviso, (10, 10))

        # Mostrar vida jugador
        vida_texto = font.render(f"Vida: {jugador.vida}", True, ROJO)
        ventana.blit(vida_texto, (10, ALTO - 30))

        pygame.display.flip()

        #  La vida
        if not jugador.esta_vivo():
            mostrar_menu_final(ventana, "¡Has perdido!")
            corriendo = False
        elif not enemigos:
            mostrar_menu_final(ventana, "¡Has ganado!")
            corriendo = False

    pygame.quit()
    sys.exit()

def mostrar_menu_opciones():
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Informe de Usuario")

    matriz = generar_matriz_informe()  # usamos la función que ya te pasé antes

    # Fuente para mostrar texto
    font = pygame.font.Font(None, 28)

    clock = pygame.time.Clock()
    en_menu = True
    while en_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # salir con ESC
                    en_menu = False

        screen.fill((30, 30, 30))  # fondo gris oscuro

        # Mostrar título
        titulo = font.render("INFORME DE USUARIOS", True, (255, 255, 0))
        screen.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 20))

        # Dibujar la matriz como texto
        x = 50
        y = 80
        for fila in matriz:
            fila_texto = " | ".join(str(item) for item in fila)
            texto = font.render(fila_texto, True, (255, 255, 255))
            screen.blit(texto, (x, y))
            y += 30  # espacio entre filas

        pygame.display.flip()
        clock.tick(30)
# ---------------------------
# Menú final
# ---------------------------
def mostrar_menu_final(superficie, mensaje):
    fuente_grande = pygame.font.Font(None, 72)
    fuente_chica = pygame.font.Font(None, 36)
    texto = fuente_grande.render(mensaje, True, BLANCO)
    texto_rect = texto.get_rect(center=(ANCHO // 2, ALTO // 2 - 100))

    clock = pygame.time.Clock()

    while True:
        clock.tick(FPS)
        superficie.fill(NEGRO)
        superficie.blit(texto, texto_rect)

        if dibujar_boton("Volver al Menú", ANCHO // 2 - 250, ALTO // 2, 200, 50, fuente_chica, superficie):
            mostrar_menu_inicio()
            return
        if dibujar_boton("Reiniciar", ANCHO // 2 - 100, ALTO // 2 + 100, 200, 50, fuente_chica, superficie):
            main()  # Reinicia el juego en nivel por defecto
            return
        if dibujar_boton("Salir", ANCHO // 2 + 50, ALTO // 2, 200, 50, fuente_chica, superficie):
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

# ---------------------------
# Punto de entrada
# ---------------------------
if __name__ == "__main__":
    pedir_usuario()
    mostrar_menu_inicio()
