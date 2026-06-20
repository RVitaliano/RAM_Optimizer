# startup.py
import winreg
import sys
import os

# Chave do registro onde ficam programas que iniciam com o Windows
REGISTRO_CHAVE = r"Software\Microsoft\Windows\CurrentVersion\Run"
REGISTRO_NOME  = "RAMOptimizer"


def adicionar_startup() -> bool:
    try:
        chave = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRO_CHAVE,
            0,
            winreg.KEY_SET_VALUE
        )
        caminho_exe = sys.executable
        winreg.SetValueEx(chave, REGISTRO_NOME, 0, winreg.REG_SZ, caminho_exe)
        winreg.CloseKey(chave)
        return True
    except Exception as e:
        print(f"Erro ao adicionar ao startup: {e}")
        return False


def remover_startup() -> bool:
    try:
        chave = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRO_CHAVE,
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(chave, REGISTRO_NOME)
        winreg.CloseKey(chave)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"Erro ao remover do startup: {e}")
        return False


def esta_no_startup() -> bool:
    try:
        chave = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REGISTRO_CHAVE,
            0,
            winreg.KEY_READ
        )
        winreg.QueryValueEx(chave, REGISTRO_NOME)
        winreg.CloseKey(chave)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False