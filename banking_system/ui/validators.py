import getpass
import re
import sys
import os
from config import Colors, Messages
from ui.display import print_error, print_guide, clear_screen, print_header, print_box
from utils.exceptions import CancelOperationException

def _show_prompt_screen(header_title: str, guide_msg: str, error_msg: str, first_iter: bool, extra_box: list = None):
    if header_title:
        clear_screen()
        print_header(header_title)
        if guide_msg:
            print_guide(guide_msg)
        if extra_box:
            print_box(extra_box)
    elif first_iter:
        if guide_msg:
            print_guide(guide_msg)
        if extra_box:
            print_box(extra_box)
            
    if error_msg:
        print_error(error_msg)

def get_masked_input(prompt: str) -> str:
    """Lee input del usuario ocultándolo con asteriscos rojos."""
    print(f"{Colors.OKCYAN}{prompt} (Oculto): {Colors.ENDC}", end='', flush=True)
    password = []
    if os.name == 'nt':
        import msvcrt
        while True:
            char = msvcrt.getwch()
            if char in ('\r', '\n'):
                print('')
                break
            elif char == '\x08': # Backspace
                if len(password) > 0:
                    password.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif char == '\x03': # Ctrl+C
                raise KeyboardInterrupt
            elif char == '\x00' or char == '\xe0': # Special keys
                msvcrt.getwch()
            else:
                password.append(char)
                sys.stdout.write(f"{Colors.FAIL}*{Colors.ENDC}")
                sys.stdout.flush()
    else:
        pwd = getpass.getpass("")
        return pwd
    return ''.join(password)

def get_valid_amount(prompt: str, min_val: float, max_val: float, header_title: str = "") -> float:
    """Solicita y valida un monto numérico dentro de un rango."""
    error_msg = ""
    first_iter = True
    while True:
        _show_prompt_screen(header_title, f"El monto debe estar comprendido entre ${min_val:,.2f} y ${max_val:,.2f} COP.", error_msg, first_iter)
        first_iter = False
        error_msg = ""
        
        try:
            raw_val = input(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}").strip()
            if raw_val.lower() == 'c':
                raise CancelOperationException()
            
            val = raw_val.replace(',', '')
            amount = float(val)
            if amount < min_val:
                error_msg = f"El monto no puede ser menor a ${min_val:,.2f}"
                continue
            if amount > max_val:
                error_msg = f"El monto excede el límite permitido (${max_val:,.2f})"
                continue
            return amount
        except ValueError:
            error_msg = "Por favor ingrese un valor numérico válido."

def get_valid_name(prompt: str, header_title: str = "") -> str:
    """Valida que el nombre tenga al menos 3 palabras y solo contenga letras."""
    error_msg = ""
    first_iter = True
    while True:
        _show_prompt_screen(header_title, "Ingrese sus nombres y apellidos completos. Se requieren al menos 3 palabras (Ej. Juan Perez Gomez).", error_msg, first_iter)
        first_iter = False
        error_msg = ""
        
        name = input(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}").strip()
        if name.lower() == 'c':
            raise CancelOperationException()
            
        if not name:
            error_msg = "El nombre no puede estar vacío."
            continue
        
        words = name.split()
        if len(words) < 3:
            error_msg = "Debe ingresar su nombre completo (mínimo 3 palabras)."
            continue
            
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", name):
            error_msg = "El nombre solo debe contener letras."
            continue
            
        return " ".join(word.capitalize() for word in words)

def get_valid_document(prompt: str, header_title: str = "") -> str:
    """Valida un documento de identidad (entre 6 y 12 dígitos)."""
    error_msg = ""
    first_iter = True
    while True:
        _show_prompt_screen(header_title, "Ingrese su número de identificación sin puntos, espacios ni guiones (Debe tener entre 6 y 12 números).", error_msg, first_iter)
        first_iter = False
        error_msg = ""
        
        doc = input(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}").strip()
        if doc.lower() == 'c':
            raise CancelOperationException()
            
        if not doc.isdigit():
            error_msg = "El documento debe contener únicamente números."
            continue
        if len(doc) < 6 or len(doc) > 12:
            error_msg = "El documento debe tener entre 6 y 12 dígitos."
            continue
        return doc

def get_valid_pin(prompt: str, doc_number: str = "", header_title: str = "") -> str:
    """
    Solicita un PIN de forma segura.
    Valida que sea de 4 dígitos y no sea trivial.
    """
    error_msg = ""
    first_iter = True
    trivial_pins = ['1234', '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999', '4321']
    
    while True:
        _show_prompt_screen(header_title, "Cree un PIN de seguridad de 4 dígitos. Por su seguridad, evite secuencias simples (1234, 0000) o terminaciones de su documento.", error_msg, first_iter)
        first_iter = False
        error_msg = ""
        
        pin = get_masked_input(prompt).strip()
        if pin.lower() == 'c':
            raise CancelOperationException()
            
        if not pin.isdigit() or len(pin) != 4:
            error_msg = "El PIN debe ser exactamente de 4 dígitos numéricos."
            continue
        if pin in trivial_pins:
            error_msg = "PIN demasiado predecible. Elija uno más seguro."
            continue
        if doc_number and pin == doc_number[-4:]:
            error_msg = "El PIN no puede coincidir con los últimos 4 dígitos de su documento."
            continue
            
        # Confirmación
        print("") # Salto de línea
        confirm = get_masked_input("Confirme su PIN").strip()
        if confirm.lower() == 'c':
            raise CancelOperationException()
            
        if pin != confirm:
            error_msg = "Los PINs no coinciden. Intente de nuevo."
            continue
            
        return pin

def get_account_number(prompt: str, header_title: str = "") -> str:
    """Solicita y valida el formato de un número de cuenta (XXX-NNNNNN-YY)."""
    error_msg = ""
    first_iter = True
    while True:
        _show_prompt_screen(header_title, "Ingrese el número de cuenta exacto incluyendo los guiones. Ejemplo formato: 001-123456-89.", error_msg, first_iter)
        first_iter = False
        error_msg = ""
        
        acc = input(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}").strip()
        if acc.lower() == 'c':
            raise CancelOperationException()
            
        if not re.match(r"^\d{3}-\d{6}-\d{2}$", acc):
            error_msg = "Formato inválido. Debe ser XXX-NNNNNN-YY (Ej. 001-123456-89)."
            continue
        return acc

def get_simple_pin(prompt: str, header_title: str = "") -> str:
    """Solo solicita 4 dígitos para login sin confirmación ni validación de reglas."""
    error_msg = ""
    first_iter = True
    while True:
        _show_prompt_screen(header_title, "", error_msg, first_iter)
        first_iter = False
        error_msg = ""
        
        pin = get_masked_input(prompt).strip()
        if pin.lower() == 'c':
            raise CancelOperationException()
            
        if not pin.isdigit() or len(pin) != 4:
            error_msg = "El PIN debe ser exactamente de 4 dígitos."
            continue
        return pin

def get_valid_email(prompt: str, header_title: str = "") -> str:
    """Solicita y valida un correo electrónico."""
    error_msg = ""
    first_iter = True
    while True:
        _show_prompt_screen(header_title, "Ingrese un correo electrónico válido (Ej. usuario@dominio.com).", error_msg, first_iter)
        first_iter = False
        error_msg = ""
        
        email = input(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}").strip()
        if email.lower() == 'c':
            raise CancelOperationException()
            
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            error_msg = "Formato de correo electrónico inválido."
            continue
        return email.lower()

def get_valid_phone(header_title: str = "") -> str:
    """Solicita código de país y número de teléfono con validación de longitud."""
    countries = {
        '1': {'name': 'Colombia', 'code': '+57', 'length': 10},
        '2': {'name': 'México', 'code': '+52', 'length': 10},
        '3': {'name': 'España', 'code': '+34', 'length': 9},
        '4': {'name': 'Argentina', 'code': '+54', 'length': 10},
        '5': {'name': 'Estados Unidos', 'code': '+1', 'length': 10}
    }
    
    country_box = [f"[{k}] {v['name']} ({v['code']})" for k, v in countries.items()]
    error_msg = ""
    first_iter = True
    
    while True:
        _show_prompt_screen(header_title, "Seleccione su país para el código telefónico y luego ingrese su número.", error_msg, first_iter, extra_box=country_box)
        first_iter = False
        error_msg = ""
        
        country_sel = input(f"{Colors.OKCYAN}Seleccione ID de País: {Colors.ENDC}").strip()
        if country_sel.lower() == 'c':
            raise CancelOperationException()
        if country_sel not in countries:
            error_msg = "ID de país inválido."
            continue
            
        country = countries[country_sel]
        
        first_iter_phone = True
        error_msg_phone = ""
        while True:
            _show_prompt_screen(header_title, f"Ha seleccionado {country['name']}. Ingrese su número de {country['length']} dígitos.", error_msg_phone, first_iter_phone)
            first_iter_phone = False
            error_msg_phone = ""
            
            phone = input(f"{Colors.OKCYAN}Número de Teléfono ({country['length']} dígitos): {Colors.ENDC}").strip()
            if phone.lower() == 'c':
                raise CancelOperationException()
            if not phone.isdigit():
                error_msg_phone = "El número solo debe contener dígitos."
                continue
            if len(phone) != country['length']:
                error_msg_phone = f"El número para {country['name']} debe tener exactamente {country['length']} dígitos."
                continue
            
            return f"{country['code']} {phone}"
