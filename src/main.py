# main.py
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tray import criar_icone_por_nivel
from app import App


def main():
    app = App()

    # Salva o ícone na pasta temp do sistema
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    icone_path = os.path.join(os.environ.get("TEMP", base_path), "ram_optimizer_icon.ico")
    icone      = criar_icone_por_nivel(20)
    icone.save(icone_path, format="ICO")
    app.iconbitmap(icone_path)

    app.mainloop()


if __name__ == "__main__":
    main()