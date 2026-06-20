# optimizer.py
# Responsável por: ler uso de RAM, detectar jogos, liberar memória

import psutil          # Lê informações do sistema (CPU, RAM, processos)
import ctypes          # Chama funções do Windows (API nativa)
import os              # Lê variáveis de ambiente e caminhos
from dotenv import load_dotenv  # Carrega o arquivo .env

# Carrega as variáveis do arquivo .env para o ambiente Python
load_dotenv()

# Lê o percentual limite do .env; se não existir, usa 88 como padrão
RAM_THRESHOLD = int(os.getenv("RAM_THRESHOLD", 88))

# Converte a string de jogos em uma lista Python
# Ex: "Overwatch.exe,cs2.exe" → ["Overwatch.exe", "cs2.exe"]
GAME_PROCESSES = os.getenv(
    "GAME_PROCESSES",
    "Overwatch.exe,cs2.exe,valorant.exe"
).split(",")


def get_ram_usage() -> dict:
    """
    Retorna um dicionário com informações de RAM.
    
    Retorna:
        {
          "percent": 72.3,       # Percentual usado (float)
          "used_gb": 11.5,       # GB em uso
          "total_gb": 16.0       # GB total
        }
    """
    # psutil.virtual_memory() retorna um objeto com vários atributos
    mem = psutil.virtual_memory()
    
    return {
        "percent": mem.percent,
        # mem.used está em bytes; dividimos por 1024³ para converter em GB
        "used_gb": round(mem.used / (1024 ** 3), 1),
        "total_gb": round(mem.total / (1024 ** 3), 1),
    }


def is_game_running() -> bool:
    """
    Verifica se algum jogo da lista está em execução.
    
    Percorre todos os processos ativos e compara o nome
    com a lista GAME_PROCESSES (sem diferenciar maiúsculas).
    
    Retorna:
        True  → há um jogo rodando (pausar otimização)
        False → nenhum jogo detectado
    """
    # psutil.process_iter(['name']) retorna um iterador de processos
    # com apenas o atributo 'name' carregado (mais eficiente)
    for proc in psutil.process_iter(['name']):
        try:
            # proc.info['name'] é o nome do executável, ex: "cs2.exe"
            # .lower() para comparação sem diferenciar maiúsculas
            proc_name = proc.info['name'].lower()
            
            # Verifica se esse processo está na lista de jogos
            for game in GAME_PROCESSES:
                if game.lower() == proc_name:
                    return True  # Jogo encontrado!
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # NoSuchProcess: processo morreu enquanto iterávamos
            # AccessDenied: sem permissão para ler esse processo
            # Em ambos os casos, simplesmente ignoramos e continuamos
            continue
    
    return False  # Nenhum jogo encontrado


def optimize_ram() -> int:
    """
    Libera memória de processos ociosos de forma suave.
    
    Estratégia:
    - Percorre processos com baixo uso de CPU
    - Chama SetProcessWorkingSetSize(-1, -1) via ctypes
      → Isso pede ao Windows para mover o working set do processo
        para o paginador (disco), sem matar o processo
      → É a mesma técnica do "Reduce Memory" original
    - Não toca em processos críticos do sistema
    
    Retorna:
        Número de processos otimizados
    """
    # Processos do sistema que NÃO devem ser tocados
    SYSTEM_PROCESSES = {
        "system", "svchost.exe", "lsass.exe", "csrss.exe",
        "wininit.exe", "services.exe", "smss.exe", "winlogon.exe",
        "explorer.exe", "dwm.exe", "taskmgr.exe"
    }
    
    otimizados = 0  # Contador de processos tratados
    
    for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
        try:
            nome = proc.info['name'].lower()
            pid  = proc.info['pid']
            
            # Pula processos do sistema
            if nome in SYSTEM_PROCESSES:
                continue
            
            # Só otimiza processos realmente ociosos (CPU < 1%)
            # cpu_percent=0.0 significa "lê sem intervalo" (snapshot)
            cpu = proc.cpu_percent(interval=0.0)
            if cpu > 1.0:
                continue
            
            # Abre o processo com permissão de escrita no working set
            # 0x1F0FFF = PROCESS_ALL_ACCESS (simplificado para fins didáticos)
            handle = ctypes.windll.kernel32.OpenProcess(
                0x1F0FFF,  # Permissão all-access
                False,     # Não herdar handle em processos filhos
                pid        # PID do processo alvo
            )
            
            if handle:
                # SetProcessWorkingSetSize com -1, -1 diz ao Windows:
                # "Remova as páginas desse processo da RAM física agora"
                # O processo continua rodando; se precisar das páginas,
                # o Windows as recarrega do page file automaticamente
                ctypes.windll.kernel32.SetProcessWorkingSetSize(
                    handle,
                    ctypes.c_size_t(-1),  # mínimo = sem limite mínimo
                    ctypes.c_size_t(-1)   # máximo = sem limite máximo
                )
                # Fecha o handle para não vazar recursos
                ctypes.windll.kernel32.CloseHandle(handle)
                otimizados += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue
    
    return otimizados


def should_auto_optimize() -> bool:
    """
    Decide se a otimização automática deve rodar agora.
    
    Condições para otimizar:
    1. Nenhum jogo está rodando
    2. Uso de RAM está acima do threshold definido no .env
    
    Retorna:
        True  → pode otimizar
        False → não otimizar agora
    """
    if is_game_running():
        return False  # Jogo ativo → não interferir
    
    ram = get_ram_usage()
    return ram["percent"] >= RAM_THRESHOLD