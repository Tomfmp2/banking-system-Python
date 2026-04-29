import os
from config import Colors
from typing import List, Tuple, Any

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str, subtitle: str = "", width: int = 60):
    """Renderiza un encabezado ASCII de alta calidad con colores ANSI."""
    print(f"{Colors.OKCYAN}╔{'═' * (width - 2)}╗{Colors.ENDC}")
    print(f"{Colors.OKCYAN}║{Colors.BOLD}{title.center(width - 2)}{Colors.ENDC}{Colors.OKCYAN}║{Colors.ENDC}")
    if subtitle:
        print(f"{Colors.OKCYAN}╠{'═' * (width - 2)}╣{Colors.ENDC}")
        print(f"{Colors.OKCYAN}║{subtitle.center(width - 2)}║{Colors.ENDC}")
    print(f"{Colors.OKCYAN}╚{'═' * (width - 2)}╝{Colors.ENDC}")

def print_box(content_lines: List[str], width: int = 60):
    """Imprime contenido dentro de un cuadro ASCII."""
    print(f"{Colors.OKBLUE}┌{'─' * (width - 2)}┐{Colors.ENDC}")
    for line in content_lines:
        # Asegura que la línea encaje en el ancho usando format
        formatted_line = f" {line} "
        visible_length = len(formatted_line) # Esto ignora si hay códigos ANSI ocultos, pero asumimos texto plano
        padding = (width - 2) - visible_length
        padding = max(0, padding)
        print(f"{Colors.OKBLUE}│{Colors.ENDC}{formatted_line}{' ' * padding}{Colors.OKBLUE}│{Colors.ENDC}")
    print(f"{Colors.OKBLUE}└{'─' * (width - 2)}┘{Colors.ENDC}")

def print_guide(msg: str):
    """Imprime un mensaje de guía en un recuadro dinámico con un signo ! amarillo, incluyendo recuadro de cancelar."""
    border = "─" * (len(msg) + 5)
    print(f"\n{Colors.WARNING}┌{border}┐{Colors.ENDC}")
    print(f"{Colors.WARNING}│ {Colors.BOLD}[!] {Colors.ENDC}{msg} {Colors.WARNING}│{Colors.ENDC}")
    print(f"{Colors.WARNING}└{border}┘{Colors.ENDC}")
    # Recuadro azul de cancelar
    print(f"{Colors.OKBLUE}┌───────────────┐{Colors.ENDC}")
    print(f"{Colors.OKBLUE}│ [C] Cancelar  │{Colors.ENDC}")
    print(f"{Colors.OKBLUE}└───────────────┘{Colors.ENDC}")

def print_error(msg: str):
    """Imprime un mensaje de error estilizado."""
    print(f"\n{Colors.FAIL}{Colors.BOLD} [✖] ERROR: {Colors.ENDC}{Colors.FAIL}{msg}{Colors.ENDC}")

def print_success(msg: str):
    """Imprime un mensaje de éxito estilizado."""
    print(f"\n{Colors.OKGREEN}{Colors.BOLD} [✔] ÉXITO: {Colors.ENDC}{Colors.OKGREEN}{msg}{Colors.ENDC}")

def print_warning(msg: str):
    """Imprime un mensaje de advertencia estilizado."""
    print(f"\n{Colors.WARNING}{Colors.BOLD} [!] ATENCIÓN: {Colors.ENDC}{Colors.WARNING}{msg}{Colors.ENDC}")

def print_table(headers: List[str], rows: List[List[Any]], widths: List[int]):
    """Imprime una tabla de datos formateada."""
    total_width = sum(widths) + len(headers) * 3 + 1
    
    # Imprimir encabezados
    print(f"{Colors.HEADER}┌" + "┬".join("─" * (w + 2) for w in widths) + f"┐{Colors.ENDC}")
    
    header_row = "│"
    for idx, header in enumerate(headers):
        header_row += f" {Colors.BOLD}{str(header).ljust(widths[idx])}{Colors.ENDC} │"
    print(header_row)
    
    print(f"{Colors.HEADER}├" + "┼".join("─" * (w + 2) for w in widths) + f"┤{Colors.ENDC}")
    
    # Imprimir filas
    if not rows:
        print(f"│ {Colors.WARNING}{'No hay registros disponibles'.center(total_width - 4)}{Colors.ENDC} │")
    else:
        for row in rows:
            row_str = "│"
            for idx, cell in enumerate(row):
                val = str(cell)
                # Aplicar color basado en el contenido para transacciones
                if val.startswith("+"):
                    val = f"{Colors.OKGREEN}{val}{Colors.ENDC}"
                elif val.startswith("-"):
                    val = f"{Colors.FAIL}{val}{Colors.ENDC}"
                
                # Necesitamos lidiar con el padding real ignorando secuencias ANSI
                visible_len = len(str(cell))
                padding = max(0, widths[idx] - visible_len)
                row_str += f" {val}{' ' * padding} │"
            print(row_str)
            
    print(f"{Colors.HEADER}└" + "┴".join("─" * (w + 2) for w in widths) + f"┘{Colors.ENDC}")

def format_currency(amount: float) -> str:
    """Formatea un valor flotante a moneda COP."""
    return f"${amount:,.2f}"
