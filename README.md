# 🧠 RAM Optimizer

> Otimizador de RAM para Windows com interface compacta, ícone dinâmico na bandeja e dois modos de otimização.

---

## ✨ Funcionalidades

- 📊 Monitoramento de RAM em tempo real
- 🔋 Ícone na bandeja que muda de cor conforme o uso de RAM
- ⚡ Otimização suave — libera processos ociosos sem afetar o que está em uso
- 🔥 Otimização agressiva — libera toda a memória possível, igual ao Reduce Memory
- 🧹 Limpeza do Standby List do Windows em toda otimização
- 🔔 Notificações nativas do Windows ao otimizar em background
- ⚙️ Configurações simples com threshold e intervalo ajustáveis
- 🌙 Tema escuro moderno
- 🪶 Leve — inicia minimizado na bandeja e usa CPU mínima em background

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
├── requirements.txt
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

> O programa já inicia minimizado na bandeja — não abre janela ao ligar o PC.

---

## ⚡ Modos de otimização

| Modo | Descrição |
|------|-----------|
| **⚡ Otimizar** | Libera memória de processos ociosos (CPU < 1%). Seguro e rápido |
| **🔥 Agressivo** | Libera memória de todos os processos + Standby List. Máxima liberação |

Ambos os modos limpam o **Standby List** do Windows ao final, liberando páginas em RAM que não estão sendo usadas ativamente.

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

As configurações são salvas automaticamente em `%APPDATA%\RAMOptimizer\config.json` e podem ser alteradas pelo botão **⚙** dentro do programa:

| Configuração       | Padrão | Descrição                         |
|--------------------|--------|-----------------------------------|
| Threshold de RAM   | 88%    | % de RAM para disparar otimização |
| Intervalo          | 60s    | Intervalo de monitoramento        |

---

## 🪶 Desempenho em background

Quando minimizado o programa:
- Lê RAM em thread separada para não bloquear nada
- Roda com prioridade `BELOW_NORMAL` para nunca competir com outros programas
- Atualiza apenas o ícone da bandeja, sem redesenhar a interface

---

## 📋 Changelog

### v1.0.2
- Novo layout compacto e moderno (widget horizontal)
- Inicia minimizado na bandeja automaticamente
- Limpeza do Standby List do Windows em toda otimização
- Processo do programa roda com prioridade abaixo do normal
- Leitura de RAM em thread separada — UI nunca trava
- Quando minimizado, widgets não são redesenhados (economia de CPU)
- Configurações aplicadas corretamente em runtime
- Removida detecção automática de jogos (simplificação)

### v1.0.1
- Botão Otimizar Agressivo
- Notificações nativas do Windows
- Configurações salvas em JSON
- Correção de bug de múltiplas threads

### v1.0.0
- Versão inicial

---