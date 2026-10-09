import pygame


class Impacto(pygame.sprite.Sprite):
    def __init__(self, x, y, alvo):
        super().__init__()
        if alvo not in ("asteroide", "nave"):
            raise ValueError(f"Tipo de impacto desconhecido: {alvo}")

        self.x = x
        self.y = y
        self.alvo = alvo
        self.vida = 8
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.atualizar_visual()

    def atualizar_visual(self):
        progresso = 1 - self.vida / 8
        self.image.fill((0, 0, 0, 0))
        centro = (20, 20)

        if self.alvo == "asteroide":
            for indice in range(8):
                angulo = indice * 45
                inicio = 5 + int(progresso * 3)
                fim = 11 + int(progresso * 8)
                ponto_inicio = (
                    centro[0] + int(pygame.math.Vector2(1, 0).rotate(angulo).x * inicio),
                    centro[1] - int(pygame.math.Vector2(1, 0).rotate(angulo).y * inicio),
                )
                ponto_fim = (
                    centro[0] + int(pygame.math.Vector2(1, 0).rotate(angulo).x * fim),
                    centro[1] - int(pygame.math.Vector2(1, 0).rotate(angulo).y * fim),
                )
                pygame.draw.line(
                    self.image,
                    (255, 190 - indice * 8, 55, 255 - int(progresso * 180)),
                    ponto_inicio,
                    ponto_fim,
                    2,
                )
            pygame.draw.circle(self.image, (255, 245, 180, 255), centro, 3)
        else:
            raio = 5 + int(progresso * 10)
            alpha = 255 - int(progresso * 180)
            pygame.draw.circle(self.image, (80, 230, 255, alpha), centro, raio, 2)
            pygame.draw.circle(self.image, (220, 255, 255, alpha), centro, 3)
            pygame.draw.line(self.image, (130, 245, 255, alpha), (8, 20), (15, 20), 2)
            pygame.draw.line(self.image, (130, 245, 255, alpha), (25, 20), (32, 20), 2)
            pygame.draw.line(self.image, (130, 245, 255, alpha), (20, 8), (20, 15), 2)
            pygame.draw.line(self.image, (130, 245, 255, alpha), (20, 25), (20, 32), 2)

    def update(self):
        self.vida -= 1
        if self.vida <= 0:
            self.kill()
            return
        self.atualizar_visual()


class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y, cor=(255, 180, 70), raio_inicial=18):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.cor = cor
        self.vida = 12
        self.max_vida = 12
        self.raio_inicial = raio_inicial
        self.atualizar_visual()

    def atualizar_visual(self):
        progresso = 1 - (self.vida / self.max_vida)
        raio = int(self.raio_inicial + progresso * 40)
        tamanho = raio * 2 + 18
        imagem = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        alpha = max(20, int(255 * (self.vida / self.max_vida)))
        pygame.draw.circle(imagem, (*self.cor, alpha), (tamanho // 2, tamanho // 2), raio)
        pygame.draw.circle(imagem, (255, 255, 255, alpha), (tamanho // 2, tamanho // 2), max(3, raio // 3))
        self.image = imagem
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.vida -= 1
        if self.vida <= 0:
            self.kill()
            return
        self.atualizar_visual()
