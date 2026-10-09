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
from entidades import (
    ChefeFrota,
    Nave,
    NaveInimiga,
    Tiro,
    TiroEspecialTitan,
    calcular_meta_frota,
    gerar_frota_inimiga,
)
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


def test_chefe_frota_tem_vida_escalavel_e_alternancia_de_salvas():
    chefe = ChefeFrota(400, 90, fase_atual=2)
    alvo = pygame.sprite.Sprite()
    alvo.rect = pygame.Rect(400, 500, 40, 40)

    primeira_salva = chefe.criar_tiros(alvo)
    chefe.cooldown_tiro = 0
    segunda_salva = chefe.criar_tiros(alvo)

    assert chefe.vida == chefe.vida_maxima == 200
    assert len(primeira_salva) == len(segunda_salva) == 3
    assert {tiro.velocidade for tiro in primeira_salva} == {5}
    assert {tiro.velocidade for tiro in segunda_salva} == {7}
    assert chefe.cooldown_tiro > 0


def test_chefe_carrega_imagem_correspondente_a_fase(monkeypatch):
    pygame.init()
    pygame.display.set_mode((800, 600))
    imagens_carregadas = []

    def carregar_imagem(caminho):
        nome_arquivo = os.path.basename(caminho)
        imagens_carregadas.append(nome_arquivo)
        if nome_arquivo.endswith(".jpg"):
            raise pygame.error("imagem JPG ainda não está disponível")
        return pygame.Surface((300, 200), pygame.SRCALPHA)

    monkeypatch.setattr(pygame.image, "load", carregar_imagem)
    nomes_esperados = ("chefe.png", "chefe2.png", "chefe3.png", "chefe4.png")

    for fase, nome_esperado in enumerate(nomes_esperados, start=1):
        chefe = ChefeFrota(400, 90, fase_atual=fase)

        assert chefe.imagem_arquivo == nome_esperado
        assert imagens_carregadas[-2:] == [
            f"{nome_esperado.removesuffix('.png')}.jpg",
            nome_esperado,
        ]
        assert chefe.image.get_width() <= 180
        assert chefe.image.get_height() <= 120


def test_tiro_basico_tem_mais_dano_e_velocidade():
    tiro = Tiro(100, 100, 90)

    assert tiro.velocidade == 16
    assert tiro.dano_inimigo == 2
    assert tiro.vy == -16


def test_tiro_basico_preserva_trajetoria_diagonal():
    tiro = Tiro(100, 100, 45)

    for _ in range(10):
        tiro.update()

    deslocamento_esperado = tiro.velocidade * 10 / 2**0.5
    assert abs(tiro.rect.centerx - (100 + deslocamento_esperado)) <= 1
    assert abs(tiro.rect.centery - (100 - deslocamento_esperado)) <= 1


def test_tiros_basicos_variem_por_modelo_mantendo_dano_total_equilibrado():
    scout = Nave(100, 100, "Scout.png").criar_tiros_basicos()
    titan = Nave(100, 100, "Titan.png").criar_tiros_basicos()
    phantom = Nave(100, 100, "Phantom.png").criar_tiros_basicos()
    aegis = Nave(100, 100, "Aegis.png").criar_tiros_basicos()
    vanguard = Nave(100, 100, "Vanguard.png").criar_tiros_basicos()

    assert len(scout) == len(titan) == len(aegis) == len(vanguard) == 1
    assert len(phantom) == 2
    assert scout[0].velocidade > vanguard[0].velocidade
    assert titan[0].velocidade < vanguard[0].velocidade
    assert titan[0].image_original.get_width() > vanguard[0].image_original.get_width()
    assert aegis[0].image_original.get_width() > vanguard[0].image_original.get_width()
    todos_os_tiros = (scout, titan, phantom, aegis, vanguard)
    assert all(
        sum(tiro.dano_inimigo for tiro in tiros) == 2
        for tiros in todos_os_tiros
    )
    assert len({(tiro.rect.centerx, tiro.rect.centery) for tiro in phantom}) == 2


def test_upgrade_de_dano_aumenta_dano_total_dos_tiros_basicos():
    for arquivo_nave in (
        "Vanguard.png",
        "Scout.png",
        "Titan.png",
        "Phantom.png",
        "Aegis.png",
    ):
        nave = Nave(
            100,
            100,
            arquivo_nave,
            {"velocidade": 1, "cadencia": 1, "especial": 1, "dano": 3},
        )
        tiros = nave.criar_tiros_basicos()

        assert sum(tiro.dano_inimigo for tiro in tiros) == 4


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


def test_jogador_ganha_energia_proporcional_ao_dano():
    jogador = Nave(100, 100, "Vanguard.png")

    jogador.adicionar_energia_por_dano(1)
    assert jogador.energia_especial == 0

    jogador.adicionar_energia_por_dano(1)
    assert jogador.energia_especial == 1

    jogador.adicionar_energia_por_dano(5)
    assert jogador.energia_especial == 3
    assert jogador.progresso_energia_especial == 50


def test_upgrades_de_vida_manobrabilidade_e_recarga_alteram_a_nave():
    base = Nave(100, 100, "Vanguard.png")
    aprimorada = Nave(
        100,
        100,
        "Vanguard.png",
        {
            "velocidade": 1,
            "cadencia": 1,
            "especial": 1,
            "dano": 1,
            "vida": 3,
            "manobrabilidade": 2,
            "recarga": 2,
        },
    )

    assert aprimorada.vida_maxima == 140
    assert aprimorada.velocidade_giro > base.velocidade_giro
    aprimorada.adicionar_energia_por_dano(5)
    assert aprimorada.energia_especial == 3


def test_recarga_especial_nao_guarda_progresso_acima_do_limite():
    jogador = Nave(
        100,
        100,
        "Vanguard.png",
        {"velocidade": 1, "cadencia": 1, "especial": 1, "recarga": 6},
    )
    jogador.energia_especial = 99

    jogador.adicionar_energia_por_dano(5)

    assert jogador.energia_especial == jogador.energia_maxima
    assert jogador.progresso_energia_especial == 0


def test_upgrade_de_recarga_aumenta_ganho_de_energia_direto():
    jogador = Nave(
        100,
        100,
        "Vanguard.png",
        {"velocidade": 1, "cadencia": 1, "especial": 1, "recarga": 2},
    )

    jogador.adicionar_energia(20)

    assert jogador.energia_especial == 24


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
