Pasta de capturas de tela

Coloque aqui as imagens de captura que aparecem como anexos na conversa. Os nomes sugeridos abaixo são os que o repositório espera para referência nas documentações.

Arquivos esperados (exemplo):
- `capture_1.png`  — screenshot 1 (BigQuery: brt_gps_raw schema)
- `capture_2.png`  — screenshot 2 (BigQuery: external_brt_gps_data schema)
- `capture_3.png`  — screenshot 3 (BigQuery: stg_brt_gps_cleaned schema)

Como colocar as imagens:
1. Baixe as imagens anexadas na conversa (ou copie-as do seu ambiente local).
2. Salve-as em `docs/capturas/` com os nomes acima (`capture_1.png`, `capture_2.png`, `capture_3.png`).

Exemplo (PowerShell):
```powershell
# no PowerShell, estando no root do projeto
# crie a pasta localmente (caso não exista)
New-Item -ItemType Directory -Path .\docs\capturas -Force

# copie as imagens para a pasta (exemplo local)
Copy-Item -Path "C:\Users\ingri\Downloads\screenshot1.png" -Destination .\docs\capturas\capture_1.png
Copy-Item -Path "C:\Users\ingri\Downloads\screenshot2.png" -Destination .\docs\capturas\capture_2.png
Copy-Item -Path "C:\Users\ingri\Downloads\screenshot3.png" -Destination .\docs\capturas\capture_3.png

# adicionar e commitar
git add docs\capturas\*
git commit -m "chore: add capture placeholders and screenshots"
``` 

Se preferir, posso criar o commit por você depois que você confirmar que colocou as imagens na pasta.