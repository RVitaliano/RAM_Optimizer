# app.py
import customtkinter as ctk
import threading
import time
import os
import json
import psutil
import ctypes

from optimizer import get_ram_usage, optimize_ram, is_game_running
from tray import SystemTray

APP_NAME    = "RAM Optimizer"
CONFIG_PATH = os.path.join(os.environ.get("APPDATA", "."), "RAMOptimizer", "config.json")

CONFIG_PADRAO = {
    "ram_threshold": 88,
    "monitor_interval": 60,
    "game_processes": [
        "Overwatch.exe", "cs2.exe", "valorant.exe", "RainbowSix.exe",
        "GTA5.exe", "Cyberpunk2077.exe", "eldenring.exe",
        "FortniteClient-Win64-Shipping.exe", "VALORANT.exe", "LeagueOfLegends.exe"
    ]
}


def carregar_config() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return CONFIG_PADRAO.copy()


def salvar_config(config: dict):
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")


def _notificar(titulo: str, mensagem: str):
    try:
        from winotify import Notification, audio
        toast = Notification(
            app_id="RAM Optimizer",
            title=titulo,
            msg=mensagem,
            duration="short"
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception:
        pass


def optimize_ram_agressivo() -> int:
    SYSTEM_PROCESSES = {
        "system", "svchost.exe", "lsass.exe", "csrss.exe",
        "wininit.exe", "services.exe", "smss.exe", "winlogon.exe",
        "dwm.exe", "taskmgr.exe"
    }
    otimizados = 0
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            nome = proc.info['name'].lower()
            pid  = proc.info['pid']
            if nome in SYSTEM_PROCESSES:
                continue
            handle = ctypes.windll.kernel32.OpenProcess(0x0100, False, pid)
            if handle:
                ctypes.windll.kernel32.SetProcessWorkingSetSize(
                    handle, ctypes.c_size_t(-1), ctypes.c_size_t(-1)
                )
                ctypes.windll.kernel32.CloseHandle(handle)
                otimizados += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue
    return otimizados


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_NAME)
        self.geometry("400x460")
        self.resizable(False, False)

        self._centralizar_janela()

        config = carregar_config()
        self._ram_threshold    = config["ram_threshold"]
        self._monitor_interval = config["monitor_interval"]
        self._game_processes   = config["game_processes"]

        self._monitorando  = True
        self._otimizando   = False
        self._jogo_rodando = False

        self._criar_widgets()

        self.tray = SystemTray(
            on_abrir    = self._mostrar_janela,
            on_otimizar = self._otimizar_manual,
            on_fechar   = self._fechar_app
        )
        self.tray.iniciar()

        self.protocol("WM_DELETE_WINDOW", self._minimizar_para_bandeja)

        threading.Thread(target=self._loop_monitoramento, daemon=True).start()

        self._atualizar_interface()
        self._checar_jogos()

    def _centralizar_janela(self):
        self.update_idletasks()
        largura = 400
        altura  = 460
        x = (self.winfo_screenwidth()  // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura  // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _criar_widgets(self):
        frame_principal = ctk.CTkFrame(self, corner_radius=0)
        frame_principal.pack(fill="both", expand=True, padx=15, pady=15)

        # ── Título ────────────────────────────────────────────────────
        ctk.CTkLabel(
            frame_principal,
            text="🧠 RAM Optimizer",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            frame_principal,
            text="Monitoramento inteligente de memória",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))

        # ── Card RAM ──────────────────────────────────────────────────
        frame_ram = ctk.CTkFrame(frame_principal)
        frame_ram.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            frame_ram,
            text="USO DE RAM",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="gray"
        ).pack(pady=(10, 0))

        self.label_ram = ctk.CTkLabel(
            frame_ram,
            text="Carregando...",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.label_ram.pack(pady=5)

        self.label_percent = ctk.CTkLabel(
            frame_ram,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.label_percent.pack()

        self.label_status = ctk.CTkLabel(
            frame_ram,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#f39c12"
        )
        self.label_status.pack()

        self.barra_ram = ctk.CTkProgressBar(frame_ram, width=300, height=15, corner_radius=5)
        self.barra_ram.pack(pady=12)
        self.barra_ram.set(0)

        # ── Botão otimizar suave ──────────────────────────────────────
        self.botao_otimizar = ctk.CTkButton(
            frame_principal,
            text="⚡ Otimizar Agora",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=55,
            width=220,
            corner_radius=10,
            command=self._otimizar_manual
        )
        self.botao_otimizar.pack(pady=(12, 5))

        # ── Botão otimizar agressivo ──────────────────────────────────
        self.botao_agressivo = ctk.CTkButton(
            frame_principal,
            text="🔥 Otimizar Agressivo",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=38,
            width=200,
            corner_radius=10,
            fg_color="#8B0000",
            hover_color="#600000",
            command=self._otimizar_agressivo
        )
        self.botao_agressivo.pack(pady=(0, 10))

        # ── Botão configurações ───────────────────────────────────────
        ctk.CTkButton(
            frame_principal,
            text="⚙ Configurações",
            font=ctk.CTkFont(size=12),
            height=38,
            fg_color="transparent",
            border_width=1,
            hover_color="#2a2a3e",
            command=self._abrir_configuracoes
        ).pack(pady=(0, 10))

    def _checar_jogos(self):
        jogo_agora = is_game_running()
        if jogo_agora and not self._jogo_rodando:
            threading.Thread(target=self._limpeza_pre_jogo, daemon=True).start()
        self._jogo_rodando = jogo_agora
        self.after(10000, self._checar_jogos)

    def _limpeza_pre_jogo(self):
        optimize_ram()
        _notificar("🎮 Jogo detectado", "RAM liberada antes do jogo iniciar.")

    def _atualizar_interface(self):
        try:
            ram     = get_ram_usage()
            percent = ram["percent"]

            self.label_ram.configure(text=f"{ram['used_gb']} GB / {ram['total_gb']} GB")
            self.label_percent.configure(text=f"{percent:.1f}% em uso")
            self.barra_ram.set(percent / 100)

            if percent >= 90:
                cor = "#e74c3c"
            elif percent >= 75:
                cor = "#f39c12"
            else:
                cor = "#2ecc71"
            self.barra_ram.configure(progress_color=cor)

            if self._jogo_rodando:
                self.label_status.configure(text="🎮 Jogo ativo — otimização pausada")
            else:
                self.label_status.configure(text="")

            self.tray.atualizar_tooltip(f"RAM Optimizer — {percent:.1f}% em uso")
            self.tray.atualizar_icone(percent)

        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")

        self.after(1000, self._atualizar_interface)

    def _loop_monitoramento(self):
        while self._monitorando:
            for _ in range(self._monitor_interval):
                if not self._monitorando:
                    return
                time.sleep(1)
            if self._jogo_rodando:
                continue
            ram = get_ram_usage()
            if ram["percent"] >= self._ram_threshold:
                optimize_ram()
                _notificar(
                    "⚡ RAM Otimizada",
                    f"Uso estava em {ram['percent']:.1f}%."
                )

    def _otimizar_manual(self):
        if self._otimizando:
            return
        self._otimizando = True

        def _fazer():
            self.after(0, lambda: self.botao_otimizar.configure(
                state="disabled", text="Otimizando..."
            ))
            optimize_ram()
            self.after(0, lambda: self.botao_otimizar.configure(
                state="normal", text="⚡ Otimizar Agora"
            ))
            self._otimizando = False

        threading.Thread(target=_fazer, daemon=True).start()

    def _otimizar_agressivo(self):
        if self._otimizando:
            return
        self._otimizando = True

        def _fazer():
            self.after(0, lambda: self.botao_agressivo.configure(
                state="disabled", text="Otimizando..."
            ))
            optimize_ram_agressivo()
            self.after(0, lambda: self.botao_agressivo.configure(
                state="normal", text="🔥 Otimizar Agressivo"
            ))
            self._otimizando = False

        threading.Thread(target=_fazer, daemon=True).start()

    def _minimizar_para_bandeja(self):
        self.withdraw()

    def _mostrar_janela(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _fechar_app(self):
        self._monitorando = False
        self.tray.parar()
        self.quit()
        self.destroy()

    # ── Janela de Configurações ───────────────────────────────────────

    def _abrir_configuracoes(self):
        if hasattr(self, '_janela_config') and self._janela_config.winfo_exists():
            self._janela_config.focus_force()
            return

        self._janela_config = ctk.CTkToplevel(self)
        self._janela_config.title("Configurações")
        self._janela_config.geometry("360x480")
        self._janela_config.resizable(False, False)
        self._janela_config.after(100, self._janela_config.lift)
        self._janela_config.after(100, self._janela_config.focus_force)
        self._janela_config.grab_set()

        frame = ctk.CTkFrame(self._janela_config, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="⚙ Configurações",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))

        # ── Threshold ─────────────────────────────────────────────────
        ctk.CTkLabel(frame, text="Otimizar automaticamente acima de:", font=ctk.CTkFont(size=12)).pack()

        self._label_threshold = ctk.CTkLabel(
            frame,
            text=f"{self._ram_threshold}%",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self._label_threshold.pack(pady=5)

        self._slider_threshold = ctk.CTkSlider(
            frame, from_=50, to=95, number_of_steps=45,
            command=self._atualizar_threshold_label
        )
        self._slider_threshold.set(self._ram_threshold)
        self._slider_threshold.pack(pady=5, padx=20, fill="x")

        # ── Intervalo ─────────────────────────────────────────────────
        ctk.CTkLabel(frame, text="Intervalo de monitoramento (segundos):", font=ctk.CTkFont(size=12)).pack(pady=(15, 0))

        self._entry_intervalo = ctk.CTkEntry(frame, width=80, justify="center")
        self._entry_intervalo.insert(0, str(self._monitor_interval))
        self._entry_intervalo.pack(pady=5)

        # ── Jogos configurados ────────────────────────────────────────
        ctk.CTkLabel(frame, text="Jogos configurados:", font=ctk.CTkFont(size=12)).pack(pady=(15, 0))

        self._label_jogos = ctk.CTkLabel(
            frame,
            text=f"{len(self._game_processes)} jogos na lista",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self._label_jogos.pack()

        ctk.CTkButton(
            frame,
            text="🎮 Gerenciar jogos",
            font=ctk.CTkFont(size=11),
            height=30,
            fg_color="transparent",
            border_width=1,
            hover_color="#2a2a3e",
            command=self._abrir_gerenciar_jogos
        ).pack(pady=5)

        # ── Salvar ────────────────────────────────────────────────────
        ctk.CTkButton(
            frame,
            text="💾 Salvar",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            command=self._salvar_configuracoes
        ).pack(pady=20, padx=20, fill="x")

    def _abrir_gerenciar_jogos(self):
        if hasattr(self, '_janela_jogos') and self._janela_jogos.winfo_exists():
            self._janela_jogos.focus_force()
            return

        self._janela_jogos = ctk.CTkToplevel(self._janela_config)
        self._janela_jogos.title("Gerenciar Jogos")
        self._janela_jogos.geometry("360x560")
        self._janela_jogos.resizable(False, False)
        self._janela_jogos.after(100, self._janela_jogos.lift)
        self._janela_jogos.after(100, self._janela_jogos.focus_force)
        self._janela_jogos.grab_set()

        frame = ctk.CTkFrame(self._janela_jogos, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            frame,
            text="🎮 Gerenciar Jogos",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text="Marque os processos que são jogos:",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack()

        # ── Barra de pesquisa ─────────────────────────────────────────
        self._entry_pesquisa = ctk.CTkEntry(
            frame,
            placeholder_text="🔍 Pesquisar processo...",
            height=35
        )
        self._entry_pesquisa.pack(fill="x", padx=10, pady=10)
        self._entry_pesquisa.bind("<KeyRelease>", self._filtrar_processos)

        # ── Lista com scroll ──────────────────────────────────────────
        self._frame_lista = ctk.CTkScrollableFrame(frame, height=300)
        self._frame_lista.pack(fill="x", padx=5, pady=5)

        self._todos_processos = set()
        for proc in psutil.process_iter(['name']):
            try:
                nome = proc.info['name']
                if nome and nome.endswith('.exe'):
                    self._todos_processos.add(nome)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        jogos_marcados = set(self._game_processes)
        self._checkboxes = {}
        self._ordem_processos = sorted(jogos_marcados) + sorted(self._todos_processos - jogos_marcados)
        self._renderizar_lista(self._ordem_processos)

        # ── Botão confirmar ───────────────────────────────────────────
        ctk.CTkButton(
            frame,
            text="✅ Confirmar",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            command=self._confirmar_jogos
        ).pack(pady=10, padx=10, fill="x")

    def _renderizar_lista(self, processos):
        for widget in self._frame_lista.winfo_children():
            widget.destroy()

        jogos_marcados = set(self._game_processes)

        for nome in processos:
            if nome in self._checkboxes:
                var = self._checkboxes[nome]
            else:
                var = ctk.StringVar(value="on" if nome in jogos_marcados else "off")
                self._checkboxes[nome] = var

            ctk.CTkCheckBox(
                self._frame_lista,
                text=nome,
                variable=var,
                onvalue="on",
                offvalue="off",
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", pady=2)

    def _filtrar_processos(self, event=None):
        termo = self._entry_pesquisa.get().lower().strip()
        filtrados = [p for p in self._ordem_processos if termo in p.lower()] if termo else self._ordem_processos
        self._renderizar_lista(filtrados)

    def _confirmar_jogos(self):
        self._game_processes = [
            nome for nome, var in self._checkboxes.items()
            if var.get() == "on"
        ]
        self._label_jogos.configure(text=f"{len(self._game_processes)} jogos na lista")
        self._janela_jogos.destroy()

    def _atualizar_threshold_label(self, valor):
        self._label_threshold.configure(text=f"{int(valor)}%")

    def _salvar_configuracoes(self):
        novo_threshold = int(self._slider_threshold.get())

        try:
            novo_intervalo = int(self._entry_intervalo.get())
            if novo_intervalo < 10:
                novo_intervalo = 10
        except ValueError:
            novo_intervalo = self._monitor_interval

        self._ram_threshold    = novo_threshold
        self._monitor_interval = novo_intervalo

        import optimizer
        optimizer.RAM_THRESHOLD  = novo_threshold
        optimizer.GAME_PROCESSES = self._game_processes

        salvar_config({
            "ram_threshold":    novo_threshold,
            "monitor_interval": novo_intervalo,
            "game_processes":   self._game_processes
        })

        self._janela_config.destroy()