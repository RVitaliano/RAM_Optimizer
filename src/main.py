import sys
import os
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))

from tray import criar_icone_por_nivel
from app import App


def main():
    app = App()

    # Quando é .exe o PyInstaller extrai para uma pasta temporária
    # sys._MEIPASS = caminho dessa pasta temporária
    # Quando é script normal, usa o diretório do próprio arquivo
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Salva o .ico na pasta temp do sistema (sempre existe)
    icone_path = os.path.join(os.environ.get("TEMP", base_path), "ram_optimizer_icon.ico")

    # Gera e salva o ícone
    icone = criar_icone_por_nivel(20)
    icone.save(icone_path, format="ICO")

    # Define o ícone da janela
    app.iconbitmap(icone_path)

    app.mainloop()


if __name__ == "__main__":
    main()