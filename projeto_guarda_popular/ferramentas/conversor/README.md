# Conversão em lote confirmada em Linux

Código local que chama a biblioteca oficial CodeWalker.Core. Não contém o código upstream.

Na máquina preparada:

```bash
cd /workspace/projeto-guarda-popular/ferramentas/conversor
DOTNET_CLI_HOME=/workspace/tools/dotnet-home NUGET_PACKAGES=/workspace/tools/nuget /workspace/tools/dotnet/dotnet build -c Release
/workspace/tools/dotnet/dotnet bin/Release/net8.0/vano_converter.dll /workspace/sedeppl-ajustada/stream /workspace/projeto-guarda-popular/convertidos /workspace/tools
```

O terceiro argumento é a pasta que contém `CodeWalker/CodeWalker.Core/strings.txt` e `shader_names.txt`. A tabela de shaders foi derivada de `szio/gta5/Shaders.xml` no ambiente. Em outra máquina, ajustar `-p:CodeWalkerRoot=/caminho/CodeWalker` na compilação e fornecer uma pasta de ferramentas válida no terceiro argumento. Não há chamada a Wine ou DirectX.

Lê YDR/YFT/YTD/YBN/YTYP/YMAP do primeiro diretório, sem recursão; grava XMLs e DDS em pastas por asset no segundo. Os originais nunca são gravados. Código de saída diferente de zero indica falha; conferir as linhas FAIL e o total. A extração por pasta é necessária porque existem texturas homônimas com conteúdo diferente. O programa deve ser chamado com diretórios de entrada e saída distintos.

No caso deste repositório, a conversão integral original produziu 76 sucessos. Não é necessário exportar manualmente pelo CodeWalker Windows. O compilador e a biblioteca ficam em /workspace/tools; esse diretório não integra o ZIP de apresentação.
