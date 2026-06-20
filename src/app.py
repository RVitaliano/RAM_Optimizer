# app.py
# Interface gráfica principal usando customtkinter

import customtkinter as ctk
import threading
import time
import os
from dotenv import load_dotenv

from optimizer import get_ram_usage, optimize_ram, should_auto_optimize, is_game_running
from tray import SystemTray

load_dotenv()

APP_NAME         = os.getenv("APP_NAME", "RAM Optimizer")
RAM_THRESHOLD    = int(os.getenv("RAM_THRESHOLD", 88))
MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", 60))


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_NAME)
        self.geometry("400x560")
        self.resizable(False, False)

        self._centralizar_janela()

        self._monitorando       = True
        self._ultima_otimizacao = "Nunca"

        self._criar_widgets()

        self.tray = SystemTray(
            on_abrir    = self._mostrar_janela,
            on_otimizar = self._otimizar_manual,
            on_fechar   = self._fechar_app
        )
        self.tray.iniciar()

        self.protocol("WM_DELETE_WINDOW", self._minimizar_para_bandeja)

        monitor_thread = threading.Thread(
            target=self._loop_monitoramento,
            daemon=True
        )
        monitor_thread.start()

        self._atualizar_interface()

    def _centralizar_janela(self):
        self.update_idletasks()
        largura = 400
        altura  = 560
        x = (self.winfo_screenwidth()  // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura  // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _criar_widgets(self):
        frame_principal = ctk.CTkFrame(self, corner_radius=0)
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Título ────────────────────────────────────────────────────
        ctk.CTkLabel(
            frame_principal,
            text="🧠 RAM Optimizer",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            frame_principal,
            text="Monitoramento inteligente de memória",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 20))

        # ── Card de uso de RAM ────────────────────────────────────────
        frame_ram = ctk.CTkFrame(frame_principal)
        frame_ram.pack(fill="x", padx=15, pady=10)

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

        self.barra_ram = ctk.CTkProgressBar(
            frame_ram,
            width=300,
            height=15,
            corner_radius=5
        )
        self.barra_ram.pack(pady=15)
        self.barra_ram.set(0)

        # ── Status ────────────────────────────────────────────────────
        frame_status = ctk.CTkFrame(frame_principal)
        frame_status.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            frame_status,
            text="STATUS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="gray"
        ).pack(pady=(10, 5))

        self.label_status = ctk.CTkLabel(
            frame_status,
            text="⏳ Iniciando...",
            font=ctk.CTkFont(size=13)
        )
        self.label_status.pack()

        self.label_ultima = ctk.CTkLabel(
            frame_status,
            text=f"Última otimização: {self._ultima_otimizacao}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.label_ultima.pack(pady=(5, 10))

        # ── Botão otimizar ────────────────────────────────────────────
        self.botao_otimizar = ctk.CTkButton(
            frame_principal,
            text="⚡ Otimizar Agora",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=55,
            width=220,
            corner_radius=10,
            command=self._otimizar_manual
        )
        self.botao_otimizar.pack(pady=15)

        # ── Botão configurações ───────────────────────────────────────
        ctk.CTkButton(
            frame_principal,
            text="⚙ Configurações",
            font=ctk.CTkFont(size=11),
            height=30,
            fg_color="transparent",
            border_width=1,
            hover_color="#2a2a3e",
            command=self._abrir_configuracoes
        ).pack(pady=(0, 5))

        # ── Botão minimizar ───────────────────────────────────────────
        ctk.CTkButton(
            frame_principal,
            text="Minimizar para bandeja",
            font=ctk.CTkFont(size=11),
            height=30,
            fg_color="transparent",
            border_width=1,
            hover_color="#2a2a3e",
            command=self._minimizar_para_bandeja
        ).pack(pady=(0, 10))

    def _atualizar_interface(self):
        try:
            ram     = get_ram_usage()
            percent = ram["percent"]

            self.label_ram.configure(
                text=f"{ram['used_gb']} GB / {ram['total_gb']} GB"
            )
            self.label_percent.configure(text=f"{percent:.1f}% em uso")
            self.barra_ram.set(percent / 100)

            if percent >= 90:
                cor = "#e74c3c"
            elif percent >= 75:
                cor = "#f39c12"
            else:
                cor = "#2ecc71"
            self.barra_ram.configure(progress_color=cor)

            if is_game_running():
                self.label_status.configure(
                    text="🎮 Jogo detectado — otimização pausada",
                    text_color="#f39c12"
                )
            else:
                self.label_status.configure(
                    text="✅ Monitorando...",
                    text_color="#2ecc71"
                )

            self.tray.atualizar_tooltip(f"RAM Optimizer — {percent:.1f}% em uso")
            self.tray.atualizar_icone(percent)

        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")

        self.after(1000, self._atualizar_interface)

    def _loop_monitoramento(self):
        while self._monitorando:
            time.sleep(MONITOR_INTERVAL)
            if should_auto_optimize():
                n = optimize_ram()
                from datetime import datetime
                agora = datetime.now().strftime("%H:%M:%S")
                self._ultima_otimizacao = f"{agora} ({n} processos)"
                self.after(0, self._atualizar_label_ultima)

    def _atualizar_label_ultima(self):
        self.label_ultima.configure(
            text=f"Última otimização: {self._ultima_otimizacao}"
        )

    def _otimizar_manual(self):
        def _fazer():
            self.after(0, lambda: self.botao_otimizar.configure(
                state="disabled", text="Otimizando..."
            ))
            n = optimize_ram()
            from datetime import datetime
            agora = datetime.now().strftime("%H:%M:%S")
            self._ultima_otimizacao = f"{agora} ({n} processos)"
            self.after(0, lambda: self.botao_otimizar.configure(
                state="normal", text="⚡ Otimizar Agora"
            ))
            self.after(0, self._atualizar_label_ultima)

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

    def _abrir_configuracoes(self):
        if hasattr(self, '_janela_config') and self._janela_config.winfo_exists():
            self._janela_config.focus_force()
            return

        self._janela_config = ctk.CTkToplevel(self)
        self._janela_config.title("Configurações")
        self._janela_config.geometry("320x280")
        self._janela_config.resizable(False, False)
        self._janela_config.grab_set()

        frame = ctk.CTkFrame(self._janela_config, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="⚙ Configurações",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))

        # ── Threshold ─────────────────────────────────────────────────
        ctk.CTkLabel(
            frame,
            text="Otimizar automaticamente acima de:",
            font=ctk.CTkFont(size=12)
        ).pack()

        self._label_threshold = ctk.CTkLabel(
            frame,
            text=f"{RAM_THRESHOLD}%",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self._label_threshold.pack(pady=5)

        self._slider_threshold = ctk.CTkSlider(
            frame,
            from_=50,
            to=95,
            number_of_steps=45,
            command=self._atualizar_threshold_label
        )
        self._slider_threshold.set(RAM_THRESHOLD)
        self._slider_threshold.pack(pady=5, padx=20, fill="x")

        # ── Intervalo ─────────────────────────────────────────────────
        ctk.CTkLabel(
            frame,
            text="Intervalo de monitoramento (segundos):",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(15, 0))

        self._entry_intervalo = ctk.CTkEntry(
            frame,
            width=80,
            justify="center"
        )
        self._entry_intervalo.insert(0, str(MONITOR_INTERVAL))
        self._entry_intervalo.pack(pady=5)

        # ── Salvar ────────────────────────────────────────────────────
        ctk.CTkButton(
            frame,
            text="💾 Salvar",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            command=self._salvar_configuracoes
        ).pack(pady=15, padx=20, fill="x")

    def _atualizar_threshold_label(self, valor):
        self._label_threshold.configure(text=f"{int(valor)}%")

    def _salvar_configuracoes(self):
        global RAM_THRESHOLD, MONITOR_INTERVAL

        novo_threshold = int(self._slider_threshold.get())

        try:
            novo_intervalo = int(self._entry_intervalo.get())
            if novo_intervalo < 10:
                novo_intervalo = 10
        except ValueError:
            novo_intervalo = MONITOR_INTERVAL

        RAM_THRESHOLD    = novo_threshold
        MONITOR_INTERVAL = novo_intervalo

        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                linhas = f.readlines()

            novas_linhas = []
            for linha in linhas:
                if linha.startswith("RAM_THRESHOLD="):
                    novas_linhas.append(f"RAM_THRESHOLD={novo_threshold}\n")
                elif linha.startswith("MONITOR_INTERVAL="):
                    novas_linhas.append(f"MONITOR_INTERVAL={novo_intervalo}\n")
                else:
                    novas_linhas.append(linha)

            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(novas_linhas)

        except Exception as e:
            print(f"Erro ao salvar .env: {e}")

        import optimizer
        optimizer.RAM_THRESHOLD = novo_threshold

        self._janela_config.destroy()