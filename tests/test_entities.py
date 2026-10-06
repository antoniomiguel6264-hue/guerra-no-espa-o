from entidades import (
    Asteroide,
    Explosao,
    Nave,
    NaveInimiga,
    Tiro,
    TiroEspecial,
    TiroEspecialAegis,
    TiroEspecialLaser,
    TiroEspecialTitan,
    TiroInimigo,
    calcular_meta_frota,
    gerar_frota_infinita,
    gerar_frota_inimiga,
)
from game.entities.effects import Explosao as ExplosaoModulo
from game.entities.enemies import (
    Asteroide as AsteroideModulo,
    NaveInimiga as NaveInimigaModulo,
    calcular_meta_frota as calcular_meta_frota_modulo,
    gerar_frota_infinita as gerar_frota_infinita_modulo,
    gerar_frota_inimiga as gerar_frota_inimiga_modulo,
)
from game.entities.player import Nave as NaveModulo
from game.entities.projectiles import (
    Tiro as TiroModulo,
    TiroEspecial as TiroEspecialModulo,
    TiroEspecialAegis as TiroEspecialAegisModulo,
    TiroEspecialLaser as TiroEspecialLaserModulo,
    TiroEspecialTitan as TiroEspecialTitanModulo,
    TiroInimigo as TiroInimigoModulo,
)


def test_entidades_mantem_imports_anteriores_e_expoe_modulos_por_responsabilidade():
    assert Nave is NaveModulo
    assert Tiro is TiroModulo
    assert TiroEspecial is TiroEspecialModulo
    assert TiroInimigo is TiroInimigoModulo
    assert TiroEspecialLaser is TiroEspecialLaserModulo
    assert TiroEspecialTitan is TiroEspecialTitanModulo
    assert TiroEspecialAegis is TiroEspecialAegisModulo
    assert Explosao is ExplosaoModulo
    assert NaveInimiga is NaveInimigaModulo
    assert Asteroide is AsteroideModulo
    assert gerar_frota_inimiga is gerar_frota_inimiga_modulo
    assert gerar_frota_infinita is gerar_frota_infinita_modulo
    assert calcular_meta_frota is calcular_meta_frota_modulo
