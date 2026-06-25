# app.py
import customtkinter as ctk
import threading
import time
import os
import json
import psutil
import ctypes
from datetime import datetime

from optimizer import get_ram_usage, optimize_ram, optimize_ram_agressivo
from tray import SystemTray

APP_NAME    = "RAM Optimizer"
CONFIG_PATH = os.path.join(os.environ.get("APPDATA", "."), "RAMOptimizer", "config.json")

CONFIG_PADRAO = {
    "ram_threshold": 88,
    "monitor_interval": 60,
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


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_NAME)
        self.geometry("480x140")
        self.resizable(False, False)
        self.configure(fg_color="#1e1e2e")

        self._centralizar_janela()

        config = carregar_config()
        self._ram_threshold    = config.get("ram_threshold", 88)
        self._monitor_interval = config.get("monitor_interval", 60)

        self._monitorando = True
        self._otimizando  = False
        self._minimizado  = False

        # Cache de RAM lido em thread separada
        self._ram_cache = {"percent": 0, "used_gb": 0.0, "total_gb": 0.0}
        self._iniciar_leitura_ram()

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
        self.after(100, self._minimizar_para_bandeja)

    def _iniciar_leitura_ram(self):
        """
        Lê RAM em thread separada a cada 1s.
        Evita bloquear a thread principal do tkinter.
        """
        def _loop():
            while self._monitorando:
                try:
                    mem = psutil.virtual_memory()
                    self._ram_cache = {
                        "percent": mem.percent,
                        "used_gb": round(mem.used / (1024 ** 3), 1),
                        "total_gb": round(mem.total / (1024 ** 3), 1),
                    }
                except Exception:
                    pass
                time.sleep(1)

        threading.Thread(target=_loop, daemon=True).start()

    def _centralizar_janela(self):
        self.update_idletasks()
        largura = 480
        altura  = 140
        x = (self.winfo_screenwidth()  // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura  // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _criar_widgets(self):
        self.configure(fg_color="#1e1e2e")

        # ── Corpo principal ───────────────────────────────────────────
        frame_corpo = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=0)
        frame_corpo.pack(fill="both", expand=True, padx=16, pady=10)

        # ── Card RAM ──────────────────────────────────────────────────
        frame_ram = ctk.CTkFrame(
            frame_corpo,
            fg_color="#181825",
            corner_radius=12,
            border_width=1,
            border_color="#2a2a3a"
        )
        frame_ram.pack(side="left", fill="both", expand=True, padx=(0, 14))

        frame_gb = ctk.CTkFrame(frame_ram, fg_color="transparent")
        frame_gb.pack(fill="x", padx=16, pady=(14, 0))

        self.label_gb_usado = ctk.CTkLabel(
            frame_gb,
            text="0.0",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#cdd6f4",
            fg_color="transparent"
        )
        self.label_gb_usado.pack(side="left")

        ctk.CTkLabel(
            frame_gb,
            text=" GB",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#a6adc8",
            fg_color="transparent"
        ).pack(side="left", pady=(6, 0))

        self.label_total = ctk.CTkLabel(
            frame_gb,
            text="/ 0 GB",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#6c7086",
            fg_color="transparent"
        )
        self.label_total.pack(side="right", pady=(6, 0))

        self.label_percent = ctk.CTkLabel(
            frame_ram,
            text="0% em uso",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#a6e3a1",
            fg_color="transparent"
        )
        self.label_percent.pack(anchor="w", padx=16, pady=(2, 8))

        self.barra_ram = ctk.CTkProgressBar(
            frame_ram,
            height=9,
            corner_radius=99,
            fg_color="#313244",
            progress_color="#a6e3a1"
        )
        self.barra_ram.pack(fill="x", padx=16, pady=(0, 14))
        self.barra_ram.set(0)

        # ── Lado direito ──────────────────────────────────────────────
        frame_direito = ctk.CTkFrame(frame_corpo, fg_color="transparent", width=170)
        frame_direito.pack(side="left", fill="y")
        frame_direito.pack_propagate(False)

        frame_centro = ctk.CTkFrame(frame_direito, fg_color="transparent")
        frame_centro.place(relx=0.5, rely=0.5, anchor="center")

        self.botao_otimizar = ctk.CTkButton(
            frame_centro,
            text="⚡ Otimizar",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=160,
            height=40,
            corner_radius=11,
            fg_color="#89b4fa",
            hover_color="#739df6",
            text_color="#11111b",
            command=self._otimizar_manual
        )
        self.botao_otimizar.pack(pady=(0, 8))

        frame_inferior = ctk.CTkFrame(frame_centro, fg_color="transparent")
        frame_inferior.pack()

        self.botao_agressivo = ctk.CTkButton(
            frame_inferior,
            text="🔥 Agressivo",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=115,
            height=32,
            corner_radius=11,
            fg_color="#2a1822",
            hover_color="#33192a",
            text_color="#f38ba8",
            border_width=1,
            border_color="#3d1f2d",
            command=self._otimizar_agressivo
        )
        self.botao_agressivo.pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            frame_inferior,
            text="⚙",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#181825",
            hover_color="#313244",
            text_color="#a6adc8",
            border_width=1,
            border_color="#2a2a3a",
            font=ctk.CTkFont(size=16),
            command=self._abrir_configuracoes
        ).pack(side="left")

    def _atualizar_interface(self):
        """Usa o cache de RAM lido em thread separada."""
        try:
            ram     = self._ram_cache
            percent = ram["percent"]

            # Sempre atualiza bandeja
            self.tray.atualizar_tooltip(
                f"RAM: {ram['used_gb']} GB / {ram['total_gb']} GB ({percent:.1f}%)"
            )
            self.tray.atualizar_icone(percent)

            # Só atualiza widgets se visível
            if not self._minimizado:
                self.label_gb_usado.configure(text=f"{ram['used_gb']}")
                self.label_total.configure(text=f"/ {ram['total_gb']} GB")
                self.label_percent.configure(text=f"{percent:.1f}% em uso")
                self.barra_ram.set(percent / 100)

                if percent >= 90:
                    cor = "#f38ba8"
                elif percent >= 75:
                    cor = "#fab387"
                else:
                    cor = "#a6e3a1"

                self.barra_ram.configure(progress_color=cor)
                self.label_percent.configure(text_color=cor)

        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")

        self.after(1000, self._atualizar_interface)

    def _loop_monitoramento(self):
        while self._monitorando:
            contador = 0
            while contador < self._monitor_interval:
                if not self._monitorando:
                    return
                time.sleep(1)
                contador += 1
            ram = self._ram_cache
            if ram["percent"] >= self._ram_threshold:
                optimize_ram()
                _notificar("⚡ RAM Otimizada", f"Uso estava em {ram['percent']:.1f}%.")

    def _otimizar_manual(self):
        if self._otimizando:
            return
        self._otimizando = True

        def _fazer():
            self.after(0, lambda: self.botao_otimizar.configure(
                state="disabled", text="..."
            ))
            optimize_ram()
            self.after(0, lambda: self.botao_otimizar.configure(
                state="normal", text="⚡  Otimizar"
            ))
            self._otimizando = False

        threading.Thread(target=_fazer, daemon=True).start()

    def _otimizar_agressivo(self):
        if self._otimizando:
            return
        self._otimizando = True

        def _fazer():
            self.after(0, lambda: self.botao_agressivo.configure(
                state="disabled", text="..."
            ))
            optimize_ram_agressivo()
            self.after(0, lambda: self.botao_agressivo.configure(
                state="normal", text="🔥 Agressivo"
            ))
            self._otimizando = False

        threading.Thread(target=_fazer, daemon=True).start()

    def _minimizar_para_bandeja(self):
        self._minimizado = True
        self.withdraw()

    def _mostrar_janela(self):
        self._minimizado = False
        self.deiconify()
        self.lift()
        self.focus_force()

    def _fechar_app(self):
        self._monitorando = False
        self.tray.parar()
        self.quit()
        self.destroy()

    # ── Configurações ─────────────────────────────────────────────────

    def _abrir_configuracoes(self):
        if hasattr(self, '_janela_config') and self._janela_config.winfo_exists():
            self._janela_config.focus_force()
            return

        self._janela_config = ctk.CTkToplevel(self)
        self._janela_config.title("Configurações")
        self._janela_config.geometry("340x340")
        self._janela_config.resizable(False, False)
        self._janela_config.configure(fg_color="#1e1e2e")
        self._janela_config.after(100, self._janela_config.lift)
        self._janela_config.after(100, self._janela_config.focus_force)
        self._janela_config.grab_set()

        frame_corpo = ctk.CTkFrame(self._janela_config, fg_color="#1e1e2e", corner_radius=0)
        frame_corpo.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            frame_corpo,
            text="Otimizar automaticamente acima de:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#a6adc8",
            fg_color="transparent"
        ).pack(anchor="w")

        self._label_threshold = ctk.CTkLabel(
            frame_corpo,
            text=f"{self._ram_threshold}%",
            font=ctk.CTkFont(family="Segoe UI", size=46, weight="bold"),
            text_color="#89b4fa",
            fg_color="transparent"
        )
        self._label_threshold.pack(pady=(6, 10))

        self._slider_threshold = ctk.CTkSlider(
            frame_corpo,
            from_=50, to=95,
            number_of_steps=45,
            button_color="#cdd6f4",
            button_hover_color="#cdd6f4",
            progress_color="#89b4fa",
            fg_color="#45475a",
            command=self._atualizar_threshold_label
        )
        self._slider_threshold.set(self._ram_threshold)
        self._slider_threshold.pack(fill="x", pady=(0, 4))

        frame_pcts = ctk.CTkFrame(frame_corpo, fg_color="transparent")
        frame_pcts.pack(fill="x", pady=(0, 18))
        ctk.CTkLabel(frame_pcts, text="50%", font=ctk.CTkFont(size=11), text_color="#585b70", fg_color="transparent").pack(side="left")
        ctk.CTkLabel(frame_pcts, text="95%", font=ctk.CTkFont(size=11), text_color="#585b70", fg_color="transparent").pack(side="right")

        ctk.CTkLabel(
            frame_corpo,
            text="Intervalo de monitoramento (segundos):",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#a6adc8",
            fg_color="transparent"
        ).pack(anchor="w", pady=(0, 8))

        self._entry_intervalo = ctk.CTkEntry(
            frame_corpo,
            height=44,
            corner_radius=9,
            fg_color="#181825",
            border_color="#2a2a3a",
            border_width=1,
            text_color="#cdd6f4",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            justify="left"
        )
        self._entry_intervalo.insert(0, str(self._monitor_interval))
        self._entry_intervalo.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(
            frame_corpo,
            text="💾  Salvar",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=46,
            corner_radius=10,
            fg_color="#89b4fa",
            hover_color="#739df6",
            text_color="#11111b",
            command=self._salvar_configuracoes
        ).pack(fill="x")

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
        optimizer.RAM_THRESHOLD = novo_threshold

        salvar_config({
            "ram_threshold":    novo_threshold,
            "monitor_interval": novo_intervalo,
        })

        self._janela_config.destroy()