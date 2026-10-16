# Instalação do Boteco Colorado MLO

O pacote contém os binários GTA compilados: 5 YDR, 1 YBN, 1 YTD e 1 YTYP. Não é necessário Blender ou .NET para instalar esses arquivos.

1. Abra o CodeWalker e carregue `stream/vano_bc_arquetipos.ytyp`, disponibilizando também os YDR, YBN e YTD da mesma pasta.
2. Abra `exemplos/vano_bc_implantacao_origem.ymap`. Selecione a instância `vano_bc_mlo` e mova/rotacione para o local escolhido. Não coloque os cinco modelos internos separadamente.
3. Recalcule os extents e salve o YMAP posicionado em `stream/`.
4. Copie a pasta `vano_boteco_colorado` para `resources/[maps]/` do servidor e adicione `ensure vano_boteco_colorado` ao `server.cfg`.
5. Teste passagem, colisão, mudança entre salas, visibilidade, iluminação e desempenho no FiveM antes de usar em produção.

**O exemplo está na origem. Não o instale sem reposicionar. Sem YMAP posicionado em `stream/`, o boteco não aparece automaticamente no mapa.**

O acesso nas grades é sempre aberto. Há salão, área de apoio/circulação, banheiro e depósito vazios. Não há móveis, louças sanitárias nem folhas de portas internas. A identidade gráfica da placa é uma reconstrução visual da foto, sem equivalência exata da arte original.

A estrutura MLO, os portais, as texturas, os arquivos binários e a malha de colisão foram conferidos. Não houve teste dentro do cliente GTA/FiveM neste ambiente. O `.blend`, as fontes, scripts, previews e relatórios estão no pacote completo e na pasta do projeto do repositório.
