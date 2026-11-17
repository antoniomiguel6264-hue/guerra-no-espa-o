# guerra no espaço
 um jogo feito em pygame usando IA

## Campanha

A campanha tem 10 fases compartilhadas entre os modos Asteroides e Frota
Inimiga. Concluir uma fase em qualquer um dos modos libera a fase seguinte
para ambos. Ao vencer as fases 5 e 10, use **Resgatar recompensa** no menu
pós-fase para liberar, respectivamente, a nave Hyperion e a skin Titan Hellion
Core no hangar. A skin Hellion mantém as características da Titan, mas troca
seu especial por uma explosão de fogo em área com dano contínuo. O especial da
Dreadnought agora dispara um projétil que explode ao atingir um alvo e causa
dano aos inimigos próximos. No modo Frota Inimiga, há batalhas contra chefes a
cada duas fases: nas fases 2, 4, 6, 8 e 10.

## Atalho Linux com ícone

O executável Linux não incorpora um ícone de arquivo. Para abrir o jogo pelo
desktop ou pelo menu de aplicativos com um ícone, gere o executável Linux e
execute `./criar_atalho_linux.sh` na pasta do projeto. O script cria os
atalhos usando `icone.png` e aponta para `dist/GuerraNoEspaco/GuerraNoEspaco`.

## Executável para Windows

O executável é compilado pelo GitHub Actions em um runner Windows. Para gerar e
baixar a versão:

1. Envie este workflow para o GitHub; o primeiro build começa automaticamente
   após o push.
2. Para builds posteriores, também é possível executar **Build Windows
   executable** na aba **Actions** do repositório.
3. Ao terminar, abra a execução do workflow e baixe o artefato
   **GuerraNoEspaco-Windows**.
4. Extraia o arquivo ZIP e execute `GuerraNoEspaco.exe` dentro da pasta
   `GuerraNoEspaco`.

Mantenha a pasta extraída inteira: o `.exe` usa arquivos que ficam ao lado dele.

O ícone do executável do Windows é definido por `icone.ico`. Para trocá-lo,
substitua esse arquivo e execute novamente o workflow.
