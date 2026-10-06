import os
import threading

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def test_arquivos_do_projeto_sao_resolvidos_no_diretorio_do_repositorio():
    import main
    import salvamento

    assert os.path.isabs(salvamento.ARQUIVO_DADOS)
    assert os.path.isabs(salvamento.ARQUIVO_RANKING)
    assert os.path.commonpath([os.path.dirname(salvamento.ARQUIVO_DADOS), os.path.dirname(main.__file__)]) == os.path.dirname(main.__file__)

import pygame

import config
import main
from entidades import Nave, NaveInimiga, TiroEspecialTitan, calcular_meta_frota, gerar_frota_inimiga
from salvamento import listar_ranking, salvar_pontuacao


def test_frota_inimiga_preserva_fases_e_gera_navios():
    frota = gerar_frota_inimiga(3)

    assert len(frota) > 0
    assert all(getattr(nave, "fase", None) == 3 for nave in frota)
    assert all(0 <= nave.rect.x <= config.LARGURA for nave in frota)
    assert all(nave.rect.y < config.ALTURA for nave in frota)


def test_meta_dedicada_para_modo_frota():
    frota = gerar_frota_inimiga(2)
    meta = calcular_meta_frota(2, frota)

    assert meta > 0
    assert meta >= len(frota) * 25


def test_modo_frota_nao_cria_asteroides():
    asteroides = main.criar_asteroides_iniciais(2, modo_frota=True)

    assert len(asteroides) == 0


def test_frota_inimiga_tem_vida_e_tiro_fraco():
    nave = NaveInimiga(100, 100, fase_atual=2)
    assert nave.vida >= 3

    alvo = main.Nave(200, 300, "Vanguard.png")
    tiro = nave.criar_tiro(alvo)

    assert tiro is not None
    assert tiro.velocidade < 10
    assert tiro.dano == 1


def test_jogador_usa_barra_de_vida():
    jogador = Nave(100, 100, "Vanguard.png")

    assert jogador.vida_maxima > 0
    assert jogador.vida == jogador.vida_maxima

    jogador.perder_vida()
    assert jogador.vida < jogador.vida_maxima
    assert not hasattr(jogador, "vidas")


def test_jogador_recupera_vida_ao_destruir_inimigo():
    jogador = Nave(100, 100, "Vanguard.png")
    jogador.vida = 40

    jogador.recuperar_vida(20)
    assert jogador.vida > 60
    assert jogador.vida <= jogador.vida_maxima
    jogador.recuperar_vida(80)
    assert jogador.vida == jogador.vida_maxima


def test_jogador_ganha_energia_pelo_valor_passado():
    jogador = Nave(100, 100, "Vanguard.png")
    jogador.energia_especial = 40

    jogador.adicionar_energia(25)
    assert jogador.energia_especial == 65

    jogador.adicionar_energia(100)
    assert jogador.energia_especial == jogador.energia_maxima


def test_jogador_recupera_vida_mais_generosamente():
    jogador = Nave(100, 100, "Vanguard.png")
    jogador.vida = 30

    jogador.recuperar_vida()
    assert jogador.vida > 55
    assert jogador.vida <= jogador.vida_maxima


def test_jogador_recupera_vida_a_cada_200_pontos():
    jogador = Nave(100, 100, "Vanguard.png")
    jogador.vida = 60

    jogador.aplicar_pontos_para_cura(200)
    assert jogador.vida == 65

    jogador.aplicar_pontos_para_cura(200)
    assert jogador.vida == 70


def test_titan_aumenta_duracao_do_especial_com_upgrade():
    jogador = Nave(100, 100, "Titan.png", {"velocidade": 1, "cadencia": 1, "especial": 3})

    especial = jogador.criar_tiro_especial()[0]

    assert isinstance(especial, TiroEspecialTitan)
    assert especial.vida > 36


def test_titan_especial_tem_raio_limitado_e_dano_escalavel():
    raios = [TiroEspecialTitan(100, 100, nivel=nivel).raio for nivel in range(1, 6)]

    assert raios == [83, 98, 113, 120, 120]
    assert all(raio <= 120 for raio in raios)
    assert TiroEspecialTitan(100, 100, nivel=3).dano >= 3


def test_titan_efeito_visual_nao_ultrapassa_o_raio_ao_terminar():
    especial = TiroEspecialTitan(100, 100, nivel=5)

    for _ in range(especial.vida):
        especial.update()

    centro = especial.image.get_rect().center
    pixels_visiveis = [
        (x, y)
        for x in range(especial.image.get_width())
        for y in range(especial.image.get_height())
        if especial.image.get_at((x, y)).a > 0
    ]
    maior_distancia = max(
        ((x - centro[0]) ** 2 + (y - centro[1]) ** 2) ** 0.5
        for x, y in pixels_visiveis
    )

    assert not especial.alive()
    assert maior_distancia <= especial.raio + 1


def test_titan_efeito_visual_usa_paleta_vermelha():
    especial = TiroEspecialTitan(100, 100)
    cores_visiveis = {
        especial.image.get_at((x, y))[:3]
        for x in range(especial.image.get_width())
        for y in range(especial.image.get_height())
        if especial.image.get_at((x, y)).a > 0
    }

    assert any(vermelho > verde and vermelho > azul for vermelho, verde, azul in cores_visiveis)
    assert not any(azul > vermelho for vermelho, _, azul in cores_visiveis)


def test_especiais_das_outras_naves_tem_papeis_balanceados():
    vanguard = Nave(100, 100, "Vanguard.png").criar_tiro_especial()
    scout = Nave(100, 100, "Scout.png").criar_tiro_especial()[0]
    phantom = Nave(100, 100, "Phantom.png").criar_tiro_especial()
    aegis = Nave(100, 100, "Aegis.png").criar_tiro_especial()[0]

    assert len(vanguard) == 3
    assert all(tiro.dano_inimigo == 2 and tiro.limite_alvos == 3 for tiro in vanguard)
    assert scout.dano_inimigo == 5
    assert scout.limite_alvos is None
    assert len(phantom) == 7
    assert all(tiro.dano_inimigo == 1 and tiro.limite_alvos == 1 for tiro in phantom)
    assert aegis.dano_inimigo == 3
    assert aegis.intervalo_dano == 20
    assert aegis.max_vida == 180


def test_especial_vanguard_atinge_cada_alvo_uma_vez_e_perfura_tres():
    especial = Nave(100, 100, "Vanguard.png").criar_tiro_especial()[0]
    grupo = pygame.sprite.Group(especial)
    alvos = [pygame.sprite.Sprite() for _ in range(4)]

    assert especial.registrar_impacto_inimigo(alvos[0])
    assert not especial.registrar_impacto_inimigo(alvos[0])
    assert especial.registrar_impacto_inimigo(alvos[1])
    assert especial.alive()
    assert especial.registrar_impacto_inimigo(alvos[2])

    assert not especial.alive()
    assert len(grupo) == 0

def test_aegis_especial_dura_no_maximo_tres_segundos_ativo():
    jogador = Nave(100, 100, "Aegis.png")
    jogador.aegis_ativo = True
    especial = jogador.criar_tiro_especial()[0]
    grupo = pygame.sprite.Group(especial)
    assert especial in grupo

    for _ in range(especial.max_vida):
        especial.update()

    assert not especial.alive()
    assert len(grupo) == 0
    assert not jogador.aegis_ativo


def test_modo_infinito_nao_gera_frota_inimiga():
    frota_1 = main.gerar_frota_infinita(0)
    frota_2 = main.gerar_frota_infinita(500)

    assert frota_1 == []
    assert frota_2 == []


def test_dano_asteroide_e_reduzido_no_modo_infinito():
    assert main.calcular_dano_asteroide("asteroides") == 20
    assert main.calcular_dano_asteroide("infinito") == 10
    assert main.calcular_dano_asteroide("frota_inimiga") == 20


def test_ranking_salva_pontuacao_no_banco():
    salvar_pontuacao(1200, "infinito", "Vanguard.png")
    ranking = listar_ranking(limit=20)

    assert any(item["pontuacao"] == 1200 for item in ranking)
    assert any(item["modo"] == "infinito" for item in ranking)


def test_modo_frota_renderiza_hud_sem_erro():
    main.inicializar_app()
    texto = main.texto_com_borda(main.fonte_hud, "MODO: FROTA INIMIGA", main.AMARELO)

    assert texto is not None
    assert texto.get_width() > 0
