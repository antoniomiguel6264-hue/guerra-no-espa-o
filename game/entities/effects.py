import pygame


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
