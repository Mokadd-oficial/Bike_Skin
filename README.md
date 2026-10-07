# BikeSkin Studio — MVP

Editor local para aplicar uma imagem em recortes de quadros de bicicleta. Os layouts e projetos são mantidos em arquivos JSON em `data/` (criados automaticamente na primeira execução).

O editor aceita várias artes por projeto. Cada template pode usar uma arte diferente, com escala e posicionamento próprios. O botão **Gerar PDF para impressão** cria uma capa com a prévia da bicicleta e uma página de corte por template, no tamanho informado em milímetros, com linha tracejada e renderização de 300 DPI. Para manter as dimensões físicas, imprima o arquivo em **100% / tamanho real**, sem ajuste automático de página.

## Rodar localmente

No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

## Área de desenvolvimento

Abra `http://127.0.0.1:5000/dev`. A senha padrão deste MVP é `admin123`.

Para não deixar a senha no código, antes de iniciar defina uma variável de ambiente:

```powershell
$env:DEV_PASSWORD = "sua-senha-segura"
python app.py
```

No canto do desenvolvedor, cada polígono usa coordenadas `[x, y]` no canvas de 760 × 500 px. As medidas em centímetros são os valores de produção do adesivo. Para uma versão final, substitua esses polígonos de demonstração pelas máscaras SVG/medições fornecidas pelo fabricante.

## Onde inserir artes e máscaras reais

- O usuário envia as artes pela interface; elas não são gravadas pelo MVP, apenas sua posição/escala é salva em `data/projects.json`.
- As máscaras de exemplo vivem no `data/layouts.json`, gerado a partir de `DEFAULT_LAYOUTS` em `app.py`. Edite pelo `/dev` ou substitua o JSON.
- O desenho cinza da bicicleta é uma ilustração de referência em `static/script.js`, na função `drawBikeBase()`. Troque-o por SVGs/fotos-base de cada modelo quando disponíveis.
