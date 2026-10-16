from pathlib import Path
import json,subprocess,html
P=Path('/workspace/projeto-guarda-popular');m=json.loads((P/'vano_medidas.json').read_text());v=json.loads((P/'vano_validacao.json').read_text());a=json.loads((P/'analise_modelos.json').read_text());t=m['total'];fmt=lambda x:f'{x:.2f}'.replace('.',',')
rows=[]
for name,r in v['componentes'].items():rows.append('| '+name+' | '+' × '.join(fmt(d) for d in r['dimensoes'])+' | '+r['fontes']+' |')
summary=f'''# vano_ — Sede Guarda Popular: versão arquitetônica para avaliação

Arquivo principal: `vano_sede_master.blend`. Previews renderizados diretamente desse projeto: `vano_perspectiva.png`, `vano_frente.png` e `vano_planta.png`, além da vista interna `vano_patio.png`. A planta renderizada oculta somente as águas e juntas da cobertura central para permitir a leitura da implantação. O master permanece com a cobertura completa.

## Situação da entrega

Projeto Blender editável em metros, com reaproveitamento efetivo de malhas originais. Esta versão não é um recurso FiveM pronto nem comprova fidelidade integral à fotografia. Ainda requer refinamento visual, preparação dos shaders/UVs finais e da exportação, reconstrução das colisões da nova implantação e teste dentro do jogo. Não há medição de FPS ou aprovação da staff.

## Medidas extraídas da geometria

A medição percorre os vértices de malhas avaliadas, incluindo modificadores e textos convertidos temporariamente para medição, em coordenadas mundiais da cena `vano_PROJETO`, frame 1. A biblioteca de originais não integra os cálculos. A cota zero é o piso acabado; o embasamento fica 0,30 m abaixo dele.

| Grandeza | Medida | Limite | Margem |
|---|---:|---:|---:|
| Largura × comprimento | {fmt(t['largura'])} × {fmt(t['comprimento'])} m | implantação proposta | — |
| Área do envelope ocupado | {fmt(t['area_envelope'])} m² | 3.500 m² | {fmt(t['margem_area'])} m² |
| Altura máxima sobre o piso | {fmt(t['altura_acima_piso'])} m | 15 m | {fmt(t['margem_altura'])} m |
| Altura máxima dos muros | {fmt(t['altura_muros'])} m | 8,60 m | {fmt(t['margem_muros'])} m |

O terreno é um retângulo de geometria explícita; a área é largura × comprimento de seu envelope, que também contém os demais elementos. O total inclui edifícios, acessos, área coberta e pátio. Não representa soma das áreas de pavimentos.

Envelopes externos medidos dos conjuntos reaproveitados (largura X × comprimento Y × altura Z); não equivalem a medidas internas úteis:

| Conjunto | Dimensões em metros | Fontes |
|---|---|---|
'''+ '\n'.join(rows)+f'''

A cobertura industrial central tem aproximadamente 40,5 × 34 m, extraídos dos objetos de cobertura, com beirais próximos de 8,4 m e cumeeira próxima de 10,17 m. O pátio permanece conectado sob a cobertura; não há segundo acesso externo. Os afastamentos e áreas cobertas se sobrepõem intencionalmente na integração das alas, portanto não devem ser somados como áreas independentes. Conferir `vano_medidas.json` e `vano_validacao.json` para valores sem arredondamento.

## Reaproveitamento e desenvolvimento

- Bar: exterior e interior originais rotacionados para enfrentar a entrada. Removidos da cópia os muros, grades e piso antigo acoplados ao edifício; cobertura de telhas original preservada. Materiais de parede reinterpretados em vermelho e acrescentados caixilhos, vidro de apresentação, marquise suspensa, arandelas e identificação. A entrada térrea e as divisões originais requerem revisão de circulação antes do jogo.
- Alento: exterior e interior originais alinhados à lateral esquerda, com manutenção da escala. Removidos os elementos de perímetro antigo da cópia. Acrescentados terraço, balcão, cobertura leve, mesas e cadeiras. A integração das aberturas com o balcão ainda deve ser revisada em detalhe.
- Galpão: exterior e interior usados na oficina direita. Retirada a cobertura curva e abertas faces frontais da cópia; a cobertura central de baixa inclinação passa a cobrir o setor. Equipamentos de oficina moderados, sem props comerciais externos.
- Grande galpão central: estrutura nova desenvolvida em torno do programa, com pilares, banzos, diagonais, terças, águas com espessura, juntas, calhas, tubos e luminárias. O galpão original é pequeno para esse vão; não foi esticado indiscriminadamente para quarenta metros.
- Portão Alento: malha e UVs reaproveitadas, redimensionadas para o acesso único; inserido painel vermelho. Animação de estudo entre frames 1 e 100. Os dois extremos permanecem no perímetro. Isso não constitui um script funcional de portão FiveM.
- Muro XML `vano_muro1909_ext.model`: reutilizado com malha e UVs; novos muros frontais segmentados descrevem curvas suaves com grades simples.
- Quadro original: reaproveitado na ala de convivência. Demais props, faixas, portões e colisões estão disponíveis na biblioteca para seleção posterior, sem serem repetidos desnecessariamente.

A cena `vano_BIBLIOTECA_ORIGINAIS` guarda os 47 recursos de modelos/colisões importados, ocultos por coleção e sem deslocar suas coordenadas de origem. As cópias do projeto ficam em `vano_PROJETO`. Os arquivos binários do repositório permanecem intocados, com SHA-256 comparado ao inventário inicial.

## Ferramentas e conversão confirmada

- Blender 4.3.2, executado em background, CPU com seis threads.
- [CodeWalker oficial](https://github.com/dexyfex/CodeWalker), commit `485d56bec00262ed7fa472261cce7bbc6202b96e`: biblioteca `CodeWalker.Core`, compilada sem erros no SDK .NET 8.0.426 em Linux. O conversor usa `Load(byte[])` e `MetaXml.GetXml`, não a interface DirectX/Windows.
- [Sollumz oficial](https://github.com/Sollumz/Sollumz), commit `2cae10b4f14eb0ed2aea92bfd7d8a83fb4c8f769`; dependência `szio==1.4.0.dev2` instalada verificando o hash exigido pelo upstream.
- A dependência binária PyMateria do Sollumz está explicitamente limitada a Windows no código consultado. A rota Linux testada foi binário → CodeWalker.Core → XML/DDS → Sollumz → Blender. Não foi necessário Wine nem GTA instalado para a conversão destes arquivos soltos.
- 76 arquivos convertidos: 22 YDR, 16 YFT, 16 YTD, 9 YBN, 6 YTYP e 7 YMAP. Os 47 YDR/YFT/YBN foram importados. YMAP/YTYP foram inspecionados em XML; não foi reconstruída automaticamente a implantação antiga.

Os arquivos de conversão ficam em `convertidos/`. As texturas extraídas de cada asset ficam em `convertidos/texturas_por_asset/<arquivo>/`, preservando variantes homônimas. O diretório plano de DDS foi usado durante a investigação; para novos imports, preferir as cópias por asset. O código local do conversor está em `ferramentas/conversor/`; depende da biblioteca upstream, não incluída nesse subdiretório. O procedimento Windows não é necessário porque a conversão Linux foi executada com sucesso.

## Integridade, dependências e otimização

- Todos os 76 RSC7 passaram pela descompressão; a conversão XML também terminou com 76 sucessos e zero falhas. Isso não substitui a validação de renderização e física no GTA.
- O XML originalmente fornecido para o muro descreve DXT1; os dois DDS fornecidos têm cabeçalho DXT5. A nova exportação CodeWalker preserva os formatos decodificados dos binários.
- Foram encontradas variantes com nomes iguais em diferentes assets: `pplartenexusa.dds`, `ppl.dds`, `preto.dds` e `gz_v_cl_low_frank05.dds`. Não devem ser combinadas cegamente em uma única YTD. `variantes_texturas.json` registra hashes e origens.
- O catálogo plano contém 73 nomes DDS, 45 com dimensões não potência de dois e 49 com no máximo um nível de mipmap. As variantes por asset acrescentam conteúdos distintos; os 73 nomes não equivalem a 73 imagens únicas. Preparar mipmaps e avaliar redimensionamento antes da entrega para FiveM, preservando os originais.
- `nexus_ppl_loja` tem 19.464 triângulos; `nexus_murga_ppl`, 7.924. Foram inspecionados e importados na biblioteca, mas não instanciados em massa no projeto. O quadro tem 12 triângulos.
- A cena arquitetônica contém {t['triangulos_avaliados']:,} triângulos avaliados aproximadamente, contando textos e modificadores. Isso não é um orçamento final de draw calls, colisão ou VRAM. O master também contém a biblioteca completa e, por isso, seu tamanho em disco não representa o tamanho de um recurso final.
- Existem texturas de GTA base ausentes no repositório, especialmente nos arquivos `ch1_06b_*` e em ferragens da porta. Os placeholders permanecem identificáveis na biblioteca; os materiais usados na cena arquitetônica passaram pela verificação de imagens disponíveis/empacotadas.
- Os LOD distances de vários originais são 9998, inadequados como escolha automática para este novo projeto. Não os herdar na exportação final; definir LODs reais e distâncias após a implantação.
- Os YBN originais foram importados para referência. Como houve rotação, cortes, remoção de cobertura e mudança de implantação, não foram tratados como colisão pronta do novo conjunto.

## O que ainda impede uma entrega jogável

Preparar shaders GTA e propriedades Sollumz das novas peças; finalizar UVs e sinalização; substituir o medalhão tipográfico GP pelo emblema autorizado adequado; revisar passagens e aberturas; gerar colisões coerentes, LODs e mipmaps; compilar YDR/YBN/YTYP/YMAP; configurar o recurso e o controle de portão; posicionar e testar no CodeWalker/FiveM com GTA e credenciais de servidor disponíveis. Não foi criado um manifesto que apenas apontasse para arquivos ainda não exportados.

O enquadramento arquitetônico aproxima a referência, mas a ala de convivência ainda conserva a linguagem do Alento original e requer refinamento. Não há veículos, murais fotográficos novos nem decoração extensa. A vegetação é simplificada para estudo. A apresentação usa materiais Principled derivados das texturas originais; os shaders GTA dos originais continuam na biblioteca e não devem ser confundidos com esses materiais de avaliação.

## Abrir e reproduzir

Abrir `vano_sede_master.blend` no Blender. A cena de trabalho é `vano_PROJETO`, frame 1 com portão fechado. A biblioteca é uma segunda cena. As texturas disponíveis estão empacotadas. Sollumz é necessário para retomar o fluxo de importação/exportação com suas propriedades; a geometria comum pode ser examinada e editada sem ele.

Na máquina preparada, regenerar a base com `blender -b -t 6 --python gerar_base.py`; depois executar `BLENDER_USER_CONFIG=/workspace/tools/blender-config blender -b -t 6 --python desenvolver.py`. Completar com `preparar_cameras.py` e `preservar_variantes.py` para registrar as câmeras e vincular as variantes DDS por asset na biblioteca. A correção final registrou 114 vínculos de textura por origem. Os scripts usam caminhos absolutos deste workspace. A conversão e o importador estão documentados nos scripts locais. `validar_master.py` reabre o arquivo, compara os hashes dos originais, mede os conjuntos, confere texturas ativas e verifica os extremos do deslocamento do portão.

Não foi localizada licença explícita dos assets no repositório. A autorização do solicitante foi usada para a adaptação local; não há afirmação de titularidade ou permissão para redistribuição pública. O código upstream das ferramentas não foi incorporado ao pacote de apresentação. Sollumz declara GPL-3.0-or-later; conservar os avisos upstream ao redistribuí-lo.
'''
(P/'vano_relatorio.md').write_text(summary)
# Measured schematic of retained assemblies, useful beside the actual top render.
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="980" viewBox="0 0 900 980"><rect width="900" height="980" fill="#f5f2eb"/><style>text{font-family:Arial;fill:#272727} .title{font-size:24px;font-weight:bold}.label{font-size:14px}</style><text x="60" y="45" class="title">vano_ / GUARDA POPULAR — implantação</text><text x="60" y="72" class="label">Envelopes medidos da geometria • metros • acesso embaixo</text>']
scl=11;ox=440;oy=820
parts.append(f'<rect x="{ox-29*scl}" y="{oy-60*scl}" width="{58*scl}" height="{60*scl}" fill="#ddd9d1" stroke="#333" stroke-width="2"/>')
# main roof extent measured from geometry-created slab vertices: collection includes frame and drainage.
g=m['vano_Galpao'];x0,y0=g['min'][:2];x1,y1=g['max'][:2]
parts.append(f'<rect x="{ox+x0*scl}" y="{oy-y1*scl}" width="{(x1-x0)*scl}" height="{(y1-y0)*scl}" fill="#cec8bc" stroke="#555" stroke-dasharray="7 4"/><text x="{ox}" y="{oy-33*scl}" class="label">GALPÃO CENTRAL</text>')
colors=['#b54a46','#d48b79','#9ca5ac','#ae4c48','#ad9991']
for (name,r),col in zip(v['componentes'].items(),colors):
 if 'quadro' in name:continue
 x0,y0=r['min'][:2];x1,y1=r['max'][:2];w=x1-x0;h=y1-y0
 parts.append(f'<rect x="{ox+x0*scl}" y="{oy-y1*scl}" width="{w*scl}" height="{max(h*scl,3)}" fill="{col}" stroke="#553333"/>')
 label=name.removeprefix('vano_').replace('_',' ').upper();cx=ox+(x0+x1)*scl/2;cy=oy-(y0+y1)*scl/2
 parts.append(f'<text x="{cx}" y="{cy}" text-anchor="middle" class="label" transform="rotate(-90 {cx} {cy})">{html.escape(label)} / {fmt(w)} × {fmt(h)}</text>')
parts.extend(['<text x="440" y="850" text-anchor="middle" font-size="18">58,00 m</text><text x="95" y="490" transform="rotate(-90 95 490)" font-size="18">60,00 m</text><text x="60" y="905" class="label">Área ocupada: 3.480 m² • construção: 10,78 m • muros: 3,00 m</text><text x="60" y="930" class="label">Envelopes de conjuntos; não substitui planta executiva de paredes e circulação.</text></svg>'])
(P/'vano_implantacao_cotada.svg').write_text(''.join(parts))
print('Relatorio e esquema cotado gravados')
