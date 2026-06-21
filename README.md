# 🧠 RAM Optimizer

> Otimizador de RAM para Windows com interface gráfica, ícone dinâmico na bandeja e detecção automática de jogos.

---

## ✨ Funcionalidades

- 📊 Monitoramento de RAM em tempo real com barra de progresso colorida
- 🔋 Ícone na bandeja que muda de cor conforme o uso de RAM
- ⚡ Otimização suave — libera processos ociosos sem afetar o que está em uso
- 🔥 Otimização agressiva — libera toda a memória possível, igual ao Reduce Memory
- 🎮 Detecção de jogos — pausa a otimização automática e libera RAM ao abrir um jogo
- 🔔 Notificações nativas do Windows ao otimizar em background
- ⚙️ Janela de configurações com lista de jogos editável e barra de pesquisa
- 🌙 Tema escuro

---

## 🖥️ Interface


---

## 📁 Estrutura do projeto

```
RAM_Optimizer/
├── src/
│   ├── main.py        # Ponto de entrada
│   ├── app.py         # Janela principal (customtkinter)
│   ├── tray.py        # Ícone na bandeja (pystray)
│   └── optimizer.py   # Lógica de otimização de RAM
├── assets/
│   └── icon.ico       # Ícone do programa
├── .gitignore
├── requirements.txt   # Dependências Python
├── Dockerfile
├── docker-compose.yml
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
pyinstaller --onefile --windowed --name "RAMOptimizer" --icon assets/icon.ico src/main.py
```

O executável será gerado em `dist/RAMOptimizer.exe`.

> O arquivo `assets/icon.ico` já está incluído no repositório.

---

## 🔁 Como iniciar com o Windows

1. Pressione `Win + R`
2. Digite `shell:startup` e aperte Enter
3. Arraste o `RAMOptimizer.exe` para a pasta que abrir

> O programa inicia automaticamente sem mexer no registro do Windows.

---

## ⚡ Modos de otimização

| Modo | Descrição |
|------|-----------|
| **Otimizar Agora** | Libera memória de processos ociosos (CPU < 1%). Seguro para uso durante jogos |
| **Otimizar Agressivo** | Libera memória de todos os processos, igual ao Reduce Memory. Ideal para liberar RAM antes de jogar |

---

## 🎮 Detecção de jogos

Quando um jogo da lista é detectado abrindo:

1. O programa libera RAM automaticamente de forma preventiva
2. Uma notificação do Windows é exibida
3. A otimização automática fica pausada enquanto o jogo estiver rodando
4. Ao fechar o jogo, o monitoramento volta ao normal

A lista de jogos pode ser editada em **⚙ Configurações → Gerenciar jogos**, com barra de pesquisa e todos os processos ativos listados para seleção.

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

Clique no ícone para abrir a janela. Clique direito para acessar o menu rápido.

---

## 🛠️ Configurações

As configurações são salvas automaticamente em `%APPDATA%\RAMOptimizer\config.json` e podem ser alteradas pelo botão **⚙ Configurações** dentro do programa:

| Configuração       | Padrão | Descrição                              |
|--------------------|--------|----------------------------------------|
| Threshold de RAM   | 88%    | % de RAM para disparar otimização      |
| Intervalo          | 60s    | Intervalo de monitoramento             |
| Processos de jogos | ...    | Lista de executáveis de jogos          |

---

## 📋 Changelog

### v2.0
- Correção de bug de múltiplas threads ao clicar rápido no botão otimizar
- Intervalo de monitoramento agora atualiza em runtime sem reiniciar
- Permissão reduzida no acesso a processos (`PROCESS_SET_QUOTA`)
- Detecção de jogos movida para timer de 10s (era 1s — muito pesado)
- Notificações nativas do Windows ao otimizar em background
- Lista de jogos editável com barra de pesquisa e processos ativos
- Limpeza preventiva de RAM ao detectar abertura de jogo
- Novo botão **Otimizar Agressivo** — libera toda RAM possível igual ao Reduce Memory
- Configurações salvas em JSON — sem dependência de arquivo `.env`
- Fechar janela minimiza para bandeja em vez de encerrar

### v1.0
- Versão inicial

---