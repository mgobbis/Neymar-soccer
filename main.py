import pygame
import random
import sys
import time
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
TELA = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo de Pênalti")
clock = pygame.time.Clock()

BRANCO = (255, 255, 255)
VERDE = (0, 200, 0)
AZUL = (0, 100, 255)
VERMELHO = (200, 0, 0)
PRETO = (0, 0, 0)

font = pygame.font.SysFont(None, 48)
font_pontos = pygame.font.SysFont(None, 64, bold=True)

TELA_INICIO = True
TELA_FIM = False
resultado_final = None
dificuldade = "facil"
pontos = 0
tentativas = 0
tempo_inicial = None
tempo_total = 30

bola_inicio_pos = None
bola_destino_pos = None
bola_parabola_altura = 0
bola_altura_max = 150
bola_bateu_goleiro = False
bola_t = 0
bola_chutada = False

# Jogador sprite
try:
    jogador_img = pygame.image.load(os.path.join("assets", "jogador.png")).convert_alpha()
    jogador_img = pygame.transform.scale(jogador_img, (80, 160))
except:
    jogador_img = None

jogador = pygame.Rect(WIDTH // 2 - 40, HEIGHT - 160, 80, 160)

# Bola
bola = pygame.Rect(WIDTH // 2 - 40, HEIGHT - 140, 80, 80)

try:
    bola_img_original = pygame.image.load(os.path.join("assets", "bola.png")).convert_alpha()
except:
    bola_img_original = None

bola_vel = 0.02

# Trave
TRAVE_LARGURA = 600
TRAVE_ALTURA = 240
TRAVE_X = WIDTH // 2 - TRAVE_LARGURA // 2
TRAVE_Y = 200

class Trave(pygame.sprite.Sprite):
    def __init__(self, caminho_imagem, largura, altura, x, y):
        super().__init__()
        self.image = pygame.image.load(caminho_imagem).convert_alpha()
        self.image = pygame.transform.scale(self.image, (largura, altura))
        self.rect = self.image.get_rect(topleft=(x, y))

try:
    trave = Trave(os.path.join("assets", "trave.png"), TRAVE_LARGURA, TRAVE_ALTURA, TRAVE_X, TRAVE_Y)
except:
    trave = None

# Goleiro
GOLEIRO_LARGURA = 140
GOLEIRO_ALTURA = 210
GOLEIRO_X = WIDTH // 2 - GOLEIRO_LARGURA // 2
GOLEIRO_Y = TRAVE_Y + TRAVE_ALTURA - GOLEIRO_ALTURA + 20

try:
    goleiro_img = pygame.image.load(os.path.join("assets", "goleiro.png")).convert_alpha()
    goleiro_img = pygame.transform.scale(goleiro_img, (GOLEIRO_LARGURA, GOLEIRO_ALTURA))
except:
    goleiro_img = None

goleiro = pygame.Rect(GOLEIRO_X, GOLEIRO_Y, GOLEIRO_LARGURA, GOLEIRO_ALTURA)
goleiro_direcao = None
goleiro_animando = False
goleiro_vel = 0.08
goleiro_alvo_x = goleiro.x
goleiro_frame = 0
goleiro_frames = [VERMELHO, (255, 100, 100), (200, 50, 50)]

animacoes_pontos = []

def carregar_img(nome, w, h):
    try:
        img = pygame.image.load(os.path.join("assets", nome)).convert()
        return pygame.transform.scale(img, (w, h))
    except:
        return None

fundo_cenario = carregar_img("cenario.png", WIDTH, HEIGHT)
fundo_inicio = carregar_img("fundo_inicio.png", WIDTH, HEIGHT)
fundo_vitoria = carregar_img("vitoria.png", WIDTH, HEIGHT)
fundo_derrota = carregar_img("derrota.png", WIDTH, HEIGHT)

def desenhar_caixa_texto(texto_str, pos_y):
    padding_x = 20
    padding_y = 10
    caixa_cor = (255, 255, 0)
    borda_cor = (200, 0, 0)

    texto = font.render(texto_str, True, PRETO)
    caixa_largura = texto.get_width() + padding_x * 2
    caixa_altura = texto.get_height() + padding_y * 2

    caixa_rect = pygame.Rect(WIDTH // 2 - caixa_largura // 2, pos_y, caixa_largura, caixa_altura)
    pygame.draw.rect(TELA, caixa_cor, caixa_rect, border_radius=10)
    pygame.draw.rect(TELA, borda_cor, caixa_rect, width=3, border_radius=10)
    TELA.blit(texto, (caixa_rect.x + padding_x, caixa_rect.y + padding_y))

def desenhar_campo():
    if fundo_cenario:
        TELA.blit(fundo_cenario, (0, 0))
    else:
        TELA.fill(VERDE)

    if trave:
        TELA.blit(trave.image, trave.rect)

    if bola_img_original:
        altura_max = 100
        altura_min = 30
        proporcao = (bola.y - TRAVE_Y) / (HEIGHT - TRAVE_Y)
        proporcao = max(0, min(proporcao, 1))
        escala = altura_min + (altura_max - altura_min) * proporcao
        bola_img = pygame.transform.scale(bola_img_original, (int(escala), int(escala)))
        TELA.blit(bola_img, (bola.x, bola.y))
    else:
        pygame.draw.ellipse(TELA, PRETO, bola)

    if goleiro_img:
        TELA.blit(goleiro_img, (goleiro.x, goleiro.y))
    else:
        pygame.draw.rect(TELA, goleiro_frames[goleiro_frame], goleiro)

    if jogador_img:
        TELA.blit(jogador_img, (jogador.x, jogador.y))
    else:
        pygame.draw.rect(TELA, AZUL, jogador)

    texto = font.render(f"Gols: {pontos}", True, BRANCO)
    TELA.blit(texto, (10, 10))

    if tempo_inicial:
        tempo_passado = int(time.time() - tempo_inicial)
        restante = max(0, tempo_total - tempo_passado)
        timer_txt = font.render(f"Tempo: {restante}s", True, BRANCO)
        TELA.blit(timer_txt, (WIDTH - 200, 10))

    for anim in animacoes_pontos:
        cor = (255, 255, 0)
        texto_anim = font_pontos.render("+1", True, cor)
        TELA.blit(texto_anim, (anim["x"], anim["y"]))

def chutar():
    global bola_chutada, tentativas, goleiro_direcao, goleiro_animando
    global bola_inicio_pos, bola_destino_pos, bola_t, bola_parabola_altura, bola_bateu_goleiro
    if not bola_chutada:
        bola_chutada = True
        tentativas += 1
        bola_inicio_pos = (bola.x, bola.y)
        bola_destino_pos = (bola.x, TRAVE_Y + TRAVE_ALTURA - 10)  # ainda menor para facilitar
        bola_t = 0
        bola_parabola_altura = bola_inicio_pos[1] - bola_destino_pos[1] + bola_altura_max
        bola_bateu_goleiro = False
        escolha_goleiro()

def mover_bola():
    global bola_chutada, pontos, animacoes_pontos, bola_t, bola_bateu_goleiro
    global bola_inicio_pos, bola_destino_pos

    if bola_chutada and bola_inicio_pos and bola_destino_pos:
        bola_t += bola_vel
        if bola_t > 1:
            bola_t = 1
        bola.x = bola_inicio_pos[0] + (bola_destino_pos[0] - bola_inicio_pos[0]) * bola_t
        bola.y = bola_inicio_pos[1] + (bola_destino_pos[1] - bola_inicio_pos[1]) * bola_t - bola_parabola_altura * 4 * (bola_t * (1 - bola_t))

        if bola.colliderect(goleiro) and not bola_bateu_goleiro:
            bola_bateu_goleiro = True
            bola_chutada = False

        if bola_t >= 1 or bola_bateu_goleiro:
            bola_chutada = False
            if not bola_bateu_goleiro and trave and bola.colliderect(trave.rect):
                pontos += 1
                animacoes_pontos.append({"x": WIDTH // 2 - 20, "y": TRAVE_Y + 50, "timer": 60})
            resetar()

def mover_goleiro():
    global goleiro_animando, goleiro_frame
    if goleiro_animando:
        goleiro_frame = (goleiro_frame + 1) % len(goleiro_frames)
        goleiro.x += (goleiro_alvo_x - goleiro.x) * goleiro_vel
        if abs(goleiro.x - goleiro_alvo_x) < 1:
            goleiro_animando = False

def escolha_goleiro():
    global goleiro_direcao, goleiro_animando, goleiro_alvo_x
    bola_lado = "centro"
    if bola.centerx < WIDTH // 2 - 50:
        bola_lado = "esquerda"
    elif bola.centerx > WIDTH // 2 + 50:
        bola_lado = "direita"

    chance = random.random()
    if dificuldade == "facil":
        if chance < 0.9:  # goleiro erra mais
            goleiro_direcao = random.choice(["esquerda", "direita", "centro"])
        else:
            goleiro_direcao = bola_lado
    elif dificuldade == "medio":
        if chance < 0.7:
            goleiro_direcao = bola_lado
        else:
            goleiro_direcao = random.choice(["esquerda", "direita", "centro"])
    elif dificuldade == "dificil":
        if chance < 0.6:
            goleiro_direcao = bola_lado
        else:
            goleiro_direcao = random.choice(["esquerda", "direita", "centro"])

    if goleiro_direcao == "esquerda":
        goleiro_alvo_x = WIDTH // 2 - 160
    elif goleiro_direcao == "direita":
        goleiro_alvo_x = WIDTH // 2 + 40
    else:
        goleiro_alvo_x = WIDTH // 2 - GOLEIRO_LARGURA // 2
    goleiro_animando = True

def resetar():
    global bola, jogador, goleiro, goleiro_frame, bola_inicio_pos, bola_destino_pos, bola_t
    bola.x, bola.y = WIDTH // 2 - 40, HEIGHT - 140
    jogador.x = WIDTH // 2 - 40
    goleiro.x, goleiro.y = WIDTH // 2 - GOLEIRO_LARGURA // 2, GOLEIRO_Y
    goleiro_frame = 0
    bola_inicio_pos = None
    bola_destino_pos = None
    bola_t = 0

def atualizar_animacoes():
    global animacoes_pontos
    novas = []
    for anim in animacoes_pontos:
        anim["y"] -= 1
        anim["timer"] -= 1
        if anim["timer"] > 0:
            novas.append(anim)
    animacoes_pontos = novas

def tela_inicio():
    global TELA_INICIO, dificuldade, pontos, tentativas, tempo_inicial
    selecionando = True
    opcoes = ["facil", "medio", "dificil"]
    indice = 0
    while selecionando:
        if fundo_inicio:
            TELA.blit(fundo_inicio, (0, 0))
        else:
            TELA.fill(PRETO)
        desenhar_caixa_texto("Use ← → para escolher dificuldade", 250)
        desenhar_caixa_texto(f"Dificuldade: {opcoes[indice]}", 350)
        desenhar_caixa_texto("Pressione ENTER para começar", 450)
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    indice = (indice - 1) % len(opcoes)
                elif evento.key == pygame.K_RIGHT:
                    indice = (indice + 1) % len(opcoes)
                elif evento.key == pygame.K_RETURN:
                    dificuldade = opcoes[indice]
                    pontos = 0; tentativas = 0
                    tempo_inicial = time.time()
                    selecionando = False; TELA_INICIO = False

def tela_final():
    global TELA_FIM, TELA_INICIO, resultado_final
    selecionando = True
    while selecionando:
        if resultado_final == "vitoria" and fundo_vitoria:
            TELA.blit(fundo_vitoria, (0, 0))
        elif resultado_final == "derrota" and fundo_derrota:
            TELA.blit(fundo_derrota, (0, 0))
        else:
            TELA.fill(PRETO)
        desenhar_caixa_texto("Pressione ENTER para reiniciar", 400)
        pygame.display.flip()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                selecionando = False; TELA_FIM = False; TELA_INICIO = True

while True:
    if TELA_INICIO: tela_inicio()
    rodando = True
    while rodando:
        clock.tick(60)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    chutar()

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and jogador.left > 0:
            jogador.x -= 3; bola.x -= 3
        if teclas[pygame.K_RIGHT] and jogador.right < WIDTH:
            jogador.x += 3; bola.x += 3

        mover_bola()
        mover_goleiro()
        atualizar_animacoes()

        desenhar_campo()
        pygame.display.flip()

        tempo_passado = int(time.time() - tempo_inicial)
        if tempo_passado >= tempo_total:
            rodando = False
            if pontos > 9: resultado_final = "vitoria"
            else: resultado_final = "derrota"
            TELA_FIM = True

    if TELA_FIM: tela_final()
