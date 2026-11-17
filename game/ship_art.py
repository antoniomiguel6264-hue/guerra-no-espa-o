import pygame


ARQUIVOS_IMAGEM_NAVE = {
    "tempest": "Tempest .png",
    "nova": "nova.jpg",
    "wraith": "wrat.png",
    "dreadnought": "Dreadnought.png",
    "vortex": "Vortex .png",
    "seraph": "Seraph.png",
    "hyperion": "Hyperion.png",
    "titan hellion core": "titan Hellion Core.png",
}


def criar_imagem_nave(modelo):
    imagem = pygame.Surface((200, 200), pygame.SRCALPHA)
    centro = (100, 100)

    if modelo == "tempest":
        pygame.draw.polygon(
            imagem, (30, 145, 180),
            [(100, 12), (184, 150), (135, 137), (100, 165), (65, 137), (16, 150)],
        )
        pygame.draw.polygon(
            imagem, (90, 235, 255),
            [(100, 20), (118, 132), (100, 157), (82, 132)],
        )
        pygame.draw.polygon(
            imagem, (20, 70, 100),
            [(37, 137), (75, 151), (66, 177), (28, 159)],
        )
        pygame.draw.polygon(
            imagem, (20, 70, 100),
            [(163, 137), (125, 151), (134, 177), (172, 159)],
        )
        pygame.draw.ellipse(imagem, (210, 255, 255), (90, 67, 20, 43))
        pygame.draw.circle(imagem, (255, 190, 90), (100, 170), 8)
    elif modelo == "nova":
        pygame.draw.polygon(
            imagem, (180, 65, 35),
            [(100, 16), (129, 66), (185, 91), (147, 126), (151, 174), (100, 155), (49, 174), (53, 126), (15, 91), (71, 66)],
        )
        pygame.draw.polygon(
            imagem, (255, 135, 65),
            [(100, 24), (116, 83), (168, 96), (130, 120), (137, 160), (100, 143), (63, 160), (70, 120), (32, 96), (84, 83)],
        )
        pygame.draw.polygon(
            imagem, (255, 220, 135),
            [(100, 35), (116, 119), (100, 145), (84, 119)],
        )
        pygame.draw.circle(imagem, (255, 245, 190), centro, 12)
        pygame.draw.circle(imagem, (255, 90, 40), (61, 145), 9)
        pygame.draw.circle(imagem, (255, 90, 40), (139, 145), 9)
    elif modelo == "wraith":
        pygame.draw.polygon(
            imagem, (52, 42, 100),
            [(100, 10), (122, 76), (190, 131), (145, 139), (127, 177), (100, 151), (73, 177), (55, 139), (10, 131), (78, 76)],
        )
        pygame.draw.polygon(
            imagem, (120, 90, 210),
            [(100, 17), (111, 112), (100, 157), (89, 112)],
        )
        pygame.draw.polygon(
            imagem, (35, 30, 70),
            [(27, 130), (75, 126), (67, 151), (42, 146)],
        )
        pygame.draw.polygon(
            imagem, (35, 30, 70),
            [(173, 130), (125, 126), (133, 151), (158, 146)],
        )
        pygame.draw.ellipse(imagem, (165, 220, 255), (91, 65, 18, 38))
        pygame.draw.polygon(imagem, (200, 125, 255), [(100, 158), (111, 178), (100, 173), (89, 178)])
    elif modelo == "dreadnought":
        pygame.draw.polygon(
            imagem, (75, 84, 105),
            [(100, 12), (139, 58), (188, 84), (159, 142), (138, 177), (100, 157), (62, 177), (41, 142), (12, 84), (61, 58)],
        )
        pygame.draw.polygon(
            imagem, (145, 160, 185),
            [(100, 24), (120, 78), (100, 145), (80, 78)],
        )
        pygame.draw.rect(imagem, (255, 120, 60), (43, 98, 20, 38), border_radius=5)
        pygame.draw.rect(imagem, (255, 120, 60), (137, 98, 20, 38), border_radius=5)
        pygame.draw.ellipse(imagem, (185, 235, 255), (88, 65, 24, 36))
    elif modelo == "vortex":
        pygame.draw.polygon(
            imagem, (36, 105, 100),
            [(100, 9), (119, 78), (188, 117), (144, 132), (127, 178), (100, 150), (73, 178), (56, 132), (12, 117), (81, 78)],
        )
        pygame.draw.polygon(
            imagem, (80, 220, 185),
            [(100, 18), (110, 110), (100, 151), (90, 110)],
        )
        pygame.draw.polygon(imagem, (150, 255, 215), [(100, 31), (115, 113), (100, 133), (85, 113)])
        pygame.draw.circle(imagem, (240, 255, 235), (100, 87), 12)
        pygame.draw.circle(imagem, (35, 65, 90), (48, 126), 9)
        pygame.draw.circle(imagem, (35, 65, 90), (152, 126), 9)
    elif modelo == "seraph":
        pygame.draw.polygon(
            imagem, (135, 115, 45),
            [(100, 11), (120, 74), (190, 53), (158, 121), (176, 158), (126, 145), (100, 183), (74, 145), (24, 158), (42, 121), (10, 53), (80, 74)],
        )
        pygame.draw.polygon(
            imagem, (255, 220, 110),
            [(100, 20), (111, 111), (100, 159), (89, 111)],
        )
        pygame.draw.polygon(imagem, (255, 250, 210), [(100, 30), (118, 115), (100, 141), (82, 115)])
        pygame.draw.circle(imagem, (130, 245, 255), (100, 89), 12)
        pygame.draw.circle(imagem, (120, 255, 190), (62, 130), 8)
        pygame.draw.circle(imagem, (120, 255, 190), (138, 130), 8)
    else:
        raise ValueError(f"Modelo de nave desconhecido: {modelo}")

    return imagem
