# optimizer.py
import psutil
import ctypes
import os
import threading

# Valores padrão — alteráveis via janela de Configurações
RAM_THRESHOLD  = 88
GAME_PROCESSES = []

# Prioridade abaixo do normal para o próprio processo
# Garante que o RAM Optimizer nunca compete com outros programas
ctypes.windll.kernel32.SetPriorityClass(
    ctypes.windll.kernel32.GetCurrentProcess(),
    0x00004000  # BELOW_NORMAL_PRIORITY_CLASS
)


def get_ram_usage() -> dict:
    """Lê uso de RAM em thread separada para não bloquear a UI."""
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used_gb": round(mem.used / (1024 ** 3), 1),
        "total_gb": round(mem.total / (1024 ** 3), 1),
    }


def limpar_standby_list():
    """
    Limpa o Standby List do Windows.
    Páginas em RAM que não estão em uso ativo mas ainda ocupam espaço.
    API oficial do Windows via ntdll.
    """
    try:
        ntdll = ctypes.windll.ntdll
        SYSTEM_MEMORY_LIST_INFORMATION = 0x50
        MemoryPurgeStandbyList = ctypes.c_ulong(4)
        ntdll.NtSetSystemInformation(
            SYSTEM_MEMORY_LIST_INFORMATION,
            ctypes.byref(MemoryPurgeStandbyList),
            ctypes.sizeof(MemoryPurgeStandbyList)
        )
    except Exception as e:
        print(f"Erro ao limpar standby list: {e}")


def optimize_ram() -> int:
    """Modo suave — só processos ociosos (CPU < 1%)."""
    SYSTEM_PROCESSES = {
        "system", "svchost.exe", "lsass.exe", "csrss.exe",
        "wininit.exe", "services.exe", "smss.exe", "winlogon.exe",
        "dwm.exe", "taskmgr.exe"
    }
    otimizados = 0
    for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
        try:
            nome = proc.info['name'].lower()
            pid  = proc.info['pid']
            if nome in SYSTEM_PROCESSES:
                continue
            if proc.cpu_percent(interval=0.0) > 1.0:
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
    limpar_standby_list()
    return otimizados


def optimize_ram_agressivo() -> int:
    """Modo agressivo — todos os processos, igual ao Reduce Memory."""
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
    limpar_standby_list()
    return otimizados


def should_auto_optimize() -> bool:
    ram = get_ram_usage()
    return ram["percent"] >= RAM_THRESHOLD