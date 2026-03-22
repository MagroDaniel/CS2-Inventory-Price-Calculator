# 📦 CS2 Inventory Exporter

Exporta seu inventário do **Counter-Strike 2** direto da Steam com as cotações atuais do mercado, gerando um arquivo `.csv` pronto para abrir no Excel.

---

## ✨ Funcionalidades

- Interface gráfica escura estilo gamer
- Busca automática de todos os itens do seu inventário CS2
- Cotação em tempo real via Steam Market (BRL, USD ou EUR)
- Tabela com itens carregando ao vivo durante a busca
- Valor total estimado do inventário
- Exportação para `.csv` compatível com Excel (separador `;`, decimal `,`)

---

## 🖥️ Como usar

### Opção 1 — Executável (Windows, sem instalar nada)

1. Baixe o `CS2_Inventory_Exporter.exe` na página de [Releases](../../releases)
2. Execute o arquivo
3. Informe seu **Steam ID64** e clique em **Buscar inventário**

### Opção 2 — Rodar pelo Python

**Pré-requisitos:** Python 3.10+ instalado com `pip`

```bash
pip install requests
python inventario_cs2_gui.py
```

### Opção 3 — Gerar o .exe você mesmo

```bash
pip install requests pyinstaller
python -m PyInstaller --onefile --windowed --name "CS2_Inventory_Exporter" inventario_cs2_gui.py
```

Ou simplesmente execute o `gerar_exe.bat` incluído no repositório.

---

## 🔑 Como encontrar seu Steam ID64

1. Acesse [steamid.io](https://steamid.io)
2. Cole a URL do seu perfil da Steam
3. Copie o número de 17 dígitos (**Steam ID64**)

> ⚠️ Seu inventário precisa estar **público** na Steam:  
> Perfil → Editar perfil → Privacidade → Inventário → **Público**

---

## 📄 Formato do CSV gerado

| # | Nome | market_hash_name | Quantidade | Preço unitário | Total | Negociável |
|---|------|-----------------|------------|----------------|-------|------------|
| 1 | AK-47 \| Redline (Field-Tested) | AK-47 \| Redline (Field-Tested) | 1 | 85,00 | 85,00 | Sim |

---

## ⚙️ Configurações

No arquivo `inventario_cs2_gui.py` você pode ajustar:

```python
time.sleep(3.0)  # Intervalo entre consultas (segundos) — reduza com cautela
```

| Valor | Velocidade | Risco de rate-limit |
|-------|-----------|---------------------|
| `3.0` | Lento | Nenhum |
| `1.5` | Moderado | Baixo |
| `1.0` | Rápido | Médio |
| `0.5` | Muito rápido | Alto |

---

## 🛠️ Tecnologias

- Python 3
- tkinter (interface gráfica)
- requests (chamadas à API da Steam)
- PyInstaller (geração do .exe)

---

## 📋 Requisitos

- Windows 10/11
- Python 3.10+ (apenas se for rodar pelo script)
- Inventário da Steam público
- Conexão com a internet

---

## ⚠️ Aviso

Este projeto usa a API pública da Steam Market. Não é afiliado à Valve Corporation. Use com responsabilidade para evitar bloqueios temporários por excesso de requisições.

---

## ☕ Apoie o projeto

Se este projeto te ajudou, considere fazer uma doação!

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Doar-ff5e5b?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/danielmagro)

**PIX:** `daniel.magro1998@gmail.com`

---

## 📝 Licença

MIT License — sinta-se livre para usar, modificar e distribuir.
