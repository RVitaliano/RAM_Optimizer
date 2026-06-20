# 🧠 RAM Optimizer

> Otimizador de RAM para Windows com interface gráfica, ícone dinâmico na bandeja e detecção automática de jogos.

---

## ✨ Funcionalidades

- 📊 Monitoramento de RAM em tempo real com barra de progresso colorida
- 🔋 Ícone na bandeja que muda de cor conforme o uso de RAM
- ⚡ Otimização automática quando RAM ultrapassa o threshold configurado
- 🎮 Detecção de jogos — pausa a otimização enquanto jogo estiver rodando
- ⚙️ Janela de configurações integrada (sem precisar editar arquivos)
- 🌙 Tema escuro

---

## 🖥️ Interface

<p align="center">
  <img src="assets/preview.png" width="400" alt="RAM Optimizer screenshot"/>
</p>

---

## 📁 Estrutura do projeto

```
RAM_Optimizer/
├── src/
│   ├── main.py        # Ponto de entrada
│   ├── app.py         # Janela principal (customtkinter)
│   ├── tray.py        # Ícone na bandeja (pystray)
│   └── optimizer.py   # Lógica de otimização de RAM
├── assets/            # Ícones gerados automaticamente
├── .env               # Configurações do programa
├── .gitignore
├── requirements.txt   # Dependências Python
└── README.md
```

---

## ⚙️ Requisitos

- Windows 10 ou 11
- Python 3.13+

---

## 🚀 Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/RVitaliano/RAM_Optimizer.git
cd RAM_Optimizer

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/Scripts/activate   # Git Bash
# ou
venv\Scripts\activate          # CMD / PowerShell

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o programa
python src/main.py
```

---

## 📦 Como gerar o .exe

```bash

# 1. Gera o executável
pyinstaller --onefile --windowed --name "RAMOptimizer" --icon assets/icon.ico src/main.py
```

O executável será gerado em `dist/RAMOptimizer.exe`.

---

## 🔁 Como iniciar com o Windows

1. Pressione `Win + R`
2. Digite `shell:startup` e aperte Enter
3. Arraste o `RAMOptimizer.exe` para a pasta que abrir

> Dessa forma o programa inicia automaticamente sem mexer no registro do Windows

---

## 🛠️ Configuração

Edite o arquivo `.env` na raiz do projeto ou use o botão **⚙ Configurações** dentro do programa:

| Variável         | Padrão        | Descrição                              |
|------------------|---------------|----------------------------------------|
| `APP_NAME`       | RAM Optimizer | Nome exibido na janela                 |
| `RAM_THRESHOLD`  | 88            | % de RAM para disparar otimização      |
| `MONITOR_INTERVAL` | 60          | Intervalo de monitoramento (segundos)  |
| `GAME_PROCESSES` | Overwatch.exe, cs2.exe... | Lista de executáveis de jogos |

---

## 🔋 Ícone da bandeja

O ícone muda de cor automaticamente conforme o uso de RAM:

| Uso        | Cor          |
|------------|--------------|
| Até 30%    | 🔵 Azul      |
| Até 50%    | 🟢 Verde     |
| Até 60%    | 🟡 Amarelo   |
| Até 75%    | 🟠 Laranja   |
| Acima 75%  | 🔴 Vermelho  |

---