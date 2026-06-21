# optimizer.py
import psutil
import ctypes

# Valores padrão — alteráveis via janela de Configurações
RAM_THRESHOLD = 88
GAME_PROCESSES = [
    "Overwatch.exe", "cs2.exe", "valorant.exe", "RainbowSix.exe",
    "GTA5.exe", "Cyberpunk2077.exe", "eldenring.exe",
    "FortniteClient-Win64-Shipping.exe", "VALORANT.exe", "LeagueOfLegends.exe"
]


def get_ram_usage() -> dict:
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used_gb": round(mem.used / (1024 ** 3), 1),
        "total_gb": round(mem.total / (1024 ** 3), 1),
    }


def is_game_running() -> bool:
    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name'].lower()
            for game in GAME_PROCESSES:
                if game.strip().lower() == proc_name:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def optimize_ram() -> int:
    SYSTEM_PROCESSES = {
        "system", "svchost.exe", "lsass.exe", "csrss.exe",
        "wininit.exe", "services.exe", "smss.exe", "winlogon.exe",
        "explorer.exe", "dwm.exe", "taskmgr.exe"
    }

    otimizados = 0

    for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
        try:
            nome = proc.info['name'].lower()
            pid  = proc.info['pid']

            if nome in SYSTEM_PROCESSES:
                continue

            cpu = proc.cpu_percent(interval=0.0)
            if cpu > 1.0:
                continue

            # 0x0100 = PROCESS_SET_QUOTA — permissão mínima necessária
            handle = ctypes.windll.kernel32.OpenProcess(0x0100, False, pid)

            if handle:
                ctypes.windll.kernel32.SetProcessWorkingSetSize(
                    handle,
                    ctypes.c_size_t(-1),
                    ctypes.c_size_t(-1)
                )
                ctypes.windll.kernel32.CloseHandle(handle)
                otimizados += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue

    return otimizados