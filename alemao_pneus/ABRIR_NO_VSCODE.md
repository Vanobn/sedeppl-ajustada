# Abrir o projeto no VS Code e Blender

## Baixar o repositório

Instale Git, VS Code e Blender 4.3.2. No terminal do VS Code (Terminal → Novo Terminal):

```bash
git clone https://github.com/Vanobn/sedeppl-ajustada.git
cd sedeppl-ajustada
git switch vano/alemao-pneus-mlo
code .
```

Se já clonou, abra a pasta do repositório no VS Code e execute:

```bash
git fetch origin
git switch vano/alemao-pneus-mlo
git pull --ff-only
```

O ramo acima contém a entrega deste PR. Depois que o PR for integrado, use `git switch main` e `git pull --ff-only`.

Não é necessário importar os arquivos um por um: **Arquivo → Abrir Pasta** no VS Code abre o repositório inteiro. A pasta `alemao_pneus/` reúne o projeto. Alternativamente, extraia `alemao_pneus_entrega.zip` e abra a pasta extraída, sem Git. O VS Code edita scripts, XMLs e documentação; o Blender abre os `.blend`.

## Windows — terminal PowerShell do VS Code

Com o terminal na raiz `sedeppl-ajustada`, use o caminho do seu Blender. Para a instalação padrão 4.3:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" ".\alemao_pneus\blender\alemao_pneus_pecas_editaveis.blend"
```

Para abrir o master GTA:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" ".\alemao_pneus\blender\alemao_pneus_master.blend"
```

Se o Blender estiver no PATH, basta:

```powershell
blender .\alemao_pneus\blender\alemao_pneus_pecas_editaveis.blend
```

Se a pasta de instalação for diferente, substitua o caminho de `blender.exe`. Não use `-b` para abrir a interface: essa opção executa em background.

## Linux / macOS

Na raiz do repositório:

```bash
blender ./alemao_pneus/blender/alemao_pneus_pecas_editaveis.blend
blender ./alemao_pneus/blender/alemao_pneus_master.blend
```

No macOS sem `blender` no PATH:

```bash
/Applications/Blender.app/Contents/MacOS/Blender ./alemao_pneus/blender/alemao_pneus_pecas_editaveis.blend
```

Execute um comando por vez, conforme o arquivo que deseja abrir. Se abriu apenas a pasta `alemao_pneus` no VS Code, remova `alemao_pneus/` dos caminhos dos comandos.

## Qual arquivo editar

- **`alemao_pneus_pecas_editaveis.blend`**: abre 601 peças independentes, para selecionar e alterar paredes, rodas, placas e estrutura. As mudanças nessa cópia não sincronizam automaticamente com o master de exportação.
- **`alemao_pneus_master.blend`**: versão de exportação GTA, com Sollumz, MLO, LODs, luzes e colisão. As peças visuais estão agrupadas por entidade; no modo de edição use `L` sobre uma peça para selecionar a geometria conectada.
- **`texturas/ap_*.png`**: fontes das texturas. As placas não têm telefones. Ao trocar uma imagem, recarregue-a e empacote-a novamente no Blender, além de atualizar os DDS/YTD para GTA.

Faça uma cópia do `.blend` antes de editar. Para importar/exportar os dados GTA, instale o **Sollumz oficial**: https://github.com/Sollumz/Sollumz . A versão usada nesta entrega está no commit `2cae10b4f14eb0ed2aea92bfd7d8a83fb4c8f769`; veja o README para as versões das ferramentas. Sem o addon é possível inspecionar a geometria, mas as propriedades GTA exigem o addon. No Blender, habilite-o antes de abrir o master. A prévia dos materiais também depende dele.

## Terminal remoto / ambiente na nuvem

O terminal integrado usa a máquina à qual o VS Code está conectado. Em uma sessão SSH/Codespaces/nuvem sem interface gráfica, `blender arquivo.blend` não abre uma janela no seu computador. Baixe o ZIP ou clone o ramo **no computador local** e use os comandos Windows/Linux/macOS acima para abrir a interface.

Neste ambiente de nuvem, a validação sem interface é:

```bash
cd /workspace/sedeppl-ajustada
BLENDER_USER_CONFIG=/workspace/tools/blender-config blender -b --python-exit-code 1 --python alemao_pneus/scripts/validar_blender.py
```

As ferramentas `/workspace/tools` pertencem ao ambiente preparado; elas não são incluídas no clone ou no ZIP. Para reconstrução/compilação local, prepare também Sollumz, szio, CodeWalker.Core, .NET 8 e as dependências Python descritas em `README.md`.
