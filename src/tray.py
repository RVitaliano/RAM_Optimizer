# tray.py
from PIL import Image, ImageDraw
import threading
import os


def _cor_por_percent(percent: float):
    if percent <= 30:
        return "#00aaff"
    elif percent <= 50:
        return "#00cc66"
    elif percent <= 60:
        return "#f0c020"
    elif percent <= 75:
        return "#f07820"
    else:
        return "#e03030"


def criar_icone_por_nivel(percent: float) -> Image.Image:
    W, H = 32, 32
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cor  = _cor_por_percent(percent)

    barras_cheias = round(percent / 10)

    draw.rectangle([12, 1, 19, 4], fill="#cccccc", outline="#555555", width=1)
    draw.rectangle([4, 4, 27, 31], fill="#1a1a1a", outline="#cccccc", width=2)

    for i in range(10):
        y_bottom = 29 - (i * 2)
        y_top    = y_bottom - 1
        if i < barras_cheias:
            draw.rectangle([7, y_top, 24, y_bottom], fill=cor)
        else:
            draw.rectangle([7, y_top, 24, y_bottom], fill="#333333")

    return img


class SystemTray:
    def __init__(self, on_abrir, on_otimizar, on_fechar):
        self.on_abrir    = on_abrir
        self.on_otimizar = on_otimizar
        self.on_fechar   = on_fechar
        self.icone       = None
        self._thread     = None
        self._percent    = -1.0

    def _criar_menu(self):
        import pystray
        return pystray.Menu(
            pystray.MenuItem("Abrir",          self._acao_abrir,    default=True),
            pystray.MenuItem("Otimizar agora", self._acao_otimizar),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Fechar",         self._acao_fechar),
        )

    def _acao_abrir(self, icon, item):
        threading.Thread(target=self.on_abrir, daemon=True).start()

    def _acao_otimizar(self, icon, item):
        threading.Thread(target=self.on_otimizar, daemon=True).start()

    def _acao_fechar(self, icon, item):
        self.parar()
        self.on_fechar()

    def iniciar(self):
        import pystray
        imagem     = criar_icone_por_nivel(0)
        self.icone = pystray.Icon(
            "RAM Optimizer",
            imagem,
            "RAM Optimizer",
            self._criar_menu()
        )
        self._thread = threading.Thread(target=self.icone.run, daemon=True)
        self._thread.start()

    def parar(self):
        if self.icone:
            self.icone.stop()

    def atualizar_tooltip(self, texto: str):
        if self.icone:
            self.icone.title = texto

    def atualizar_icone(self, percent: float):
        nivel = round(percent / 10) * 10
        if self.icone and nivel != self._percent:
            self._percent      = nivel
            self.icone.icon    = criar_icone_por_nivel(percent)