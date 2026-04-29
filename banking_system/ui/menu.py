import sys
from typing import Optional
from config import Colors, Messages, PAGINATION_LIMIT, MIN_INITIAL_DEPOSIT_SAVINGS, MIN_INITIAL_DEPOSIT_CHECKING
from models.account import Account
from services.account_service import AccountService
from services.transaction_service import TransactionService
from services.product_service import ProductService
from services.loan_service import LoanService
from services.key_transfer_service import KeyTransferService
from ui.display import clear_screen, print_header, print_box, print_guide, print_error, print_success, print_warning, print_table, format_currency
from ui.validators import get_valid_amount, get_valid_name, get_valid_document, get_valid_pin, get_account_number, get_simple_pin, get_valid_phone, get_valid_email, _show_prompt_screen
from utils.exceptions import BankException, CancelOperationException

class MenuController:
    def __init__(self, account_service: AccountService, transaction_service: TransactionService, product_service: ProductService, loan_service: LoanService, key_service: KeyTransferService):
        self.account_service = account_service
        self.transaction_service = transaction_service
        self.product_service = product_service
        self.loan_service = loan_service
        self.key_service = key_service
        self.current_user: Optional[Account] = None

    def pause(self):
        input(f"\n{Colors.OKCYAN}Presione ENTER para continuar...{Colors.ENDC}")

    def run(self):
        while True:
            if self.current_user is None:
                self.show_welcome_screen()
            else:
                self.show_main_menu()

    def show_welcome_screen(self):
        clear_screen()
        print_header(Messages.WELCOME, "Acceso al Sistema")
        print_box([
            "[1] Iniciar sesión",
            "[2] Crear cuenta nueva",
            "[3] Acerca del sistema",
            "[0] Salir"
        ])
        
        choice = input(Messages.PROMPT).strip()
        
        if choice == '1':
            self.login()
        elif choice == '2':
            self.create_account()
        elif choice == '3':
            self.about()
        elif choice == '0':
            clear_screen()
            print(f"{Colors.OKGREEN}Gracias por utilizar el Sistema Bancario. ¡Hasta pronto!{Colors.ENDC}")
            sys.exit(0)
        else:
            print_error(Messages.ERR_INVALID_OPTION)
            self.pause()

    def login(self):
        header = "INICIAR SESIÓN"
        try:
            acc_num = get_account_number("Número de Cuenta: ", header)
            pin = get_simple_pin("PIN de Seguridad", header)
            
            self.current_user = self.account_service.authenticate(acc_num, pin)
            print_success(Messages.SUCCESS_LOGIN)
            self.pause()
        except CancelOperationException:
            print_error("Operación cancelada por el usuario.")
            self.pause()
        except BankException as e:
            print_error(str(e))
            self.pause()

    def create_account(self):
        header = "CREAR NUEVA CUENTA"
        try:
            name = get_valid_name("Nombre Completo: ", header)
            doc = get_valid_document("Documento de Identidad: ", header)
            phone = get_valid_phone(header)
            email = get_valid_email("Correo Electrónico: ", header)
            
            clear_screen()
            print_header(header)
            
            print_guide("Seleccione el tipo de cuenta que desea abrir. (Ahorros: Depósito mín. $10,000 | Corriente: Depósito mín. $50,000)")
            print(f"{Colors.OKCYAN}Tipo de Cuenta:{Colors.ENDC}")
            print("  [1] Ahorros")
            print("  [2] Corriente")
            tipo_sel = input("Seleccione tipo (1 o 2): ").strip()
            if tipo_sel.lower() == 'c':
                raise CancelOperationException()
                
            if tipo_sel not in ['1', '2']:
                print_error("Tipo de cuenta inválido.")
                self.pause()
                return
            acc_type = 'ahorros' if tipo_sel == '1' else 'corriente'
            
            min_dep = MIN_INITIAL_DEPOSIT_SAVINGS if acc_type == 'ahorros' else MIN_INITIAL_DEPOSIT_CHECKING
            amount = get_valid_amount("Depósito Inicial (COP): $", min_dep, 999999999, header)
            pin = get_valid_pin("Asigne un PIN de Seguridad", doc, header)
            
            account = self.account_service.create_account(name, doc, acc_type, amount, pin, phone, email)
            
            clear_screen()
            print_header("CUENTA CREADA EXITOSAMENTE")
            print_box([
                f"Titular: {account.owner_name}",
                f"Documento: {account.owner_id}",
                f"Tipo: {account.account_type.capitalize()}",
                f"N° de Cuenta: {Colors.WARNING}{account.account_number}{Colors.ENDC}{Colors.OKBLUE}",
                f"Saldo Inicial: {format_currency(account.balance)}"
            ])
            print_warning("GUARDE SU NÚMERO DE CUENTA. LO NECESITARÁ PARA INICIAR SESIÓN.")
            self.pause()
            
        except CancelOperationException:
            print_error("Operación cancelada por el usuario.")
            self.pause()
        except BankException as e:
            print_error(str(e))
            self.pause()

    def about(self):
        clear_screen()
        print_header("ACERCA DEL SISTEMA")
        print_box([
            "Sistema Bancario en Consola",
            "Versión: 1.0",
            "Arquitectura Clean Code en Python.",
            "Desarrollado para simular un entorno transaccional real.",
            "Persistencia en JSON con bloqueo de concurrencia."
        ])
        self.pause()

    def show_main_menu(self):
        clear_screen()
        # Actualizar datos del usuario por si hubo cambios en otra sesión
        try:
            self.current_user = self.account_service.find_by_id(self.current_user.account_id)
        except:
            self.current_user = None
            return

        print_header("PANEL PRINCIPAL", f"Cuenta: {self.current_user.account_number}")
        print_box([
            f"Titular: {self.current_user.owner_name}",
            f"Tipo:    {self.current_user.account_type.capitalize()}",
            f"Saldo:   {format_currency(self.current_user.balance)}"
        ])
        
        print(f"\n{Colors.OKCYAN}  OPERACIONES DISPONIBLES{Colors.ENDC}")
        print("  [1] Consultar saldo")
        print("  [2] Realizar depósito")
        print("  [3] Realizar retiro")
        print("  [4] Transferir fondos")
        print("  [5] Historial de transacciones")
        print("  [6] Cambiar PIN")
        print("  [7] Mis datos personales")
        print("  [8] Mis Tarjetas y Productos")
        print("  [9] Solicitar producto")
        print("  [10] Portal de Llaves (Transfiya)")
        print("  [11] Pagar mis cuentas")
        print("  [12] Aportes a Inversión/Ahorro")
        print("  [0] Cerrar Sesión")
        
        opcion = input(f"\n{Colors.OKCYAN}{Messages.PROMPT}{Colors.ENDC}").strip()
        
        if opcion == '1':
            self.check_balance()
        elif opcion == '2':
            self.deposit()
        elif opcion == '3':
            self.withdraw()
        elif opcion == '4':
            self.transfer()
        elif opcion == '5':
            self.transaction_history()
        elif opcion == '6':
            self.change_pin()
        elif opcion == '7':
            self.personal_data()
        elif opcion == '8':
            self.view_products()
        elif opcion == '9':
            self.request_product()
        elif opcion == '10':
            self.keys_portal()
        elif opcion == '11':
            self.pay_loans()
        elif opcion == '12':
            self.fund_investments()
        elif opcion == '0':
            self.current_user = None
            print_success("Sesión cerrada correctamente.")
            self.pause()
        else:
            print_error(Messages.ERR_INVALID_OPTION)
            self.pause()

    def check_balance(self):
        clear_screen()
        print_header("CONSULTA DE SALDO")
        print_box([
            f"Cuenta: {self.current_user.account_number}",
            f"Saldo Disponible: {format_currency(self.current_user.balance)}"
        ])
        self.pause()

    def deposit(self):
        header = "DEPÓSITO EN EFECTIVO"
        try:
            amount = get_valid_amount("Monto a depositar: $", 1000, 50000000, header)
            
            clear_screen()
            print_header(header)
            
            print(f"\n{Colors.WARNING}Confirmación:{Colors.ENDC} ¿Desea depositar {format_currency(amount)}? (S/N)")
            if input(">>> ").strip().lower() != 's':
                print_error("Operación cancelada.")
                self.pause()
                return
                
            tx = self.transaction_service.deposit(self.current_user, amount)
            print_success(f"Depósito de {format_currency(amount)} realizado exitosamente.")
            print(f"Nuevo saldo: {format_currency(tx.balance_after)}")
            self.pause()
        except CancelOperationException:
            print_error("Operación cancelada por el usuario.")
            self.pause()
        except BankException as e:
            print_error(str(e))
            self.pause()

    def _select_source_of_funds(self, header):
        print_guide("Seleccione el origen de los fondos:")
        print("  [1] Tarjeta Débito (Saldo de la cuenta)")
        
        products = self.product_service.get_products_by_account(self.current_user.account_id)
        tarjetas_credito = [p for p in products if p.product_type == "credito"]
        
        loans = self.loan_service.get_loans_by_account(self.current_user.account_id)
        prestamos_activos = [l for l in loans if l.status == "activo" and l.fondos_disponibles > 0]
        
        opt_idx = 2
        options_map = {'1': ("cuenta", None, self.current_user.balance, self.current_user)}
        
        if tarjetas_credito:
            for tc in tarjetas_credito:
                disp = tc.details.get('disponible', 0)
                print(f"  [{opt_idx}] Tarjeta Crédito {tc.details.get('numero_tarjeta', 'N/A')} (Disp: {format_currency(disp)})")
                options_map[str(opt_idx)] = ("tarjeta_credito", tc.product_id, disp, tc)
                opt_idx += 1
                
        if prestamos_activos:
            for l in prestamos_activos:
                print(f"  [{opt_idx}] Préstamo {l.loan_type.capitalize()} (Disp: {format_currency(l.fondos_disponibles)})")
                options_map[str(opt_idx)] = ("prestamo", l.loan_id, l.fondos_disponibles, l)
                opt_idx += 1
                
        print("  [C] Cancelar")
        sel = input(f"\n{Colors.OKCYAN}>>> {Colors.ENDC}").strip().lower()
        if sel == 'c': raise CancelOperationException()
        if sel not in options_map: raise BankException("Opción inválida.")
        return options_map[sel]

    def withdraw(self):
        header = "RETIRO DE FONDOS"
        clear_screen()
        print_header(header)
        try:
            tipo, obj_id, disp, obj = self._select_source_of_funds(header)
            
            amount = get_valid_amount("Monto a retirar: $", 1000, disp, header)
            
            if tipo == "cuenta":
                pin = get_simple_pin("Ingrese su PIN", header)
                self.transaction_service.withdraw(self.current_user, amount, pin)
                print_success(f"Retiro de {format_currency(amount)} exitoso desde cuenta principal.")
            elif tipo == "tarjeta_credito":
                pin = get_simple_pin("Ingrese su PIN para confirmar avance", header)
                self.account_service.verify_pin(self.current_user, pin)
                obj.details['disponible'] -= amount
                obj.details['deuda_actual'] += amount
                prods = self.product_service.get_all_products()
                for i, p in enumerate(prods):
                    if p.product_id == obj.product_id: prods[i] = obj
                self.product_service._save_products(prods)
                
                from models.transaction import Transaction
                tx = Transaction(account_id=self.current_user.account_id, transaction_type="avance_tarjeta", amount=amount, balance_before=self.current_user.balance, balance_after=self.current_user.balance, description=f"Avance TC {obj.details.get('numero_tarjeta')}")
                self.transaction_service._append_transaction(tx)
                print_success(f"Avance de {format_currency(amount)} exitoso desde tarjeta de crédito. ¡Retire su dinero!")
            elif tipo == "prestamo":
                pin = get_simple_pin("Ingrese su PIN para confirmar", header)
                self.account_service.verify_pin(self.current_user, pin)
                obj.fondos_disponibles -= amount
                all_loans = self.loan_service.get_all_loans()
                for i, l in enumerate(all_loans):
                    if l.loan_id == obj.loan_id: all_loans[i] = obj
                self.loan_service._save_loans(all_loans)
                
                from models.transaction import Transaction
                tx = Transaction(account_id=self.current_user.account_id, transaction_type="disposicion_credito", amount=amount, balance_before=self.current_user.balance, balance_after=self.current_user.balance, description=f"Disposición de préstamo {obj.loan_type}")
                self.transaction_service._append_transaction(tx)
                print_success(f"Disposición de {format_currency(amount)} exitosa desde el préstamo. ¡Retire su dinero!")
        except CancelOperationException:
            print_error("Operación cancelada por el usuario.")
        except BankException as e:
            print_error(str(e))
        self.pause()

    def transfer(self):
        header = "TRANSFERENCIA DE FONDOS"
        clear_screen()
        print_header(header)
        try:
            tipo, obj_id, disp, obj = self._select_source_of_funds(header)
            
            amount = get_valid_amount("Monto a transferir: $", 1000, disp, header)
            target_acc = get_account_number("Número de cuenta destino: ", header)
            
            if tipo == "cuenta":
                pin = get_simple_pin("PIN de Seguridad para autorizar", header)
                self.transaction_service.transfer(self.current_user, target_acc, amount, pin, "")
                print_success(f"Transferencia de {format_currency(amount)} exitosa desde cuenta principal.")
            else:
                pin = get_simple_pin("PIN de Seguridad para autorizar", header)
                self.account_service.verify_pin(self.current_user, pin)
                
                # Ejecutar transferencia "virtual" inyectando el dinero a la cuenta destino
                target = self.account_service.find_by_number(target_acc)
                target.balance += amount
                self.account_service.update_account(target)
                
                from models.transaction import Transaction
                desc = ""
                if tipo == "tarjeta_credito":
                    obj.details['disponible'] -= amount
                    obj.details['deuda_actual'] += amount
                    prods = self.product_service.get_all_products()
                    for i, p in enumerate(prods):
                        if p.product_id == obj.product_id: prods[i] = obj
                    self.product_service._save_products(prods)
                    desc = "Transferencia desde Tarjeta Crédito"
                else:
                    obj.fondos_disponibles -= amount
                    all_loans = self.loan_service.get_all_loans()
                    for i, l in enumerate(all_loans):
                        if l.loan_id == obj.loan_id: all_loans[i] = obj
                    self.loan_service._save_loans(all_loans)
                    desc = "Transferencia desde Préstamo"
                    
                tx_out = Transaction(account_id=self.current_user.account_id, target_account_id=target.account_id, transaction_type="transferencia", amount=amount, balance_before=self.current_user.balance, balance_after=self.current_user.balance, description=desc)
                tx_in = Transaction(account_id=target.account_id, target_account_id=self.current_user.account_id, transaction_type="transferencia_recibida", amount=amount, balance_before=target.balance-amount, balance_after=target.balance, description=f"Recibido de {self.current_user.owner_name} ({desc})")
                
                txs = self.transaction_service.get_all_transactions()
                txs.append(tx_out)
                txs.append(tx_in)
                self.transaction_service._save_transactions(txs)
                
                print_success(f"Transferencia de {format_currency(amount)} exitosa.")
        except CancelOperationException:
            print_error("Operación cancelada por el usuario.")
        except BankException as e:
            print_error(str(e))
            self.pause()

    def transaction_history(self):
        history = self.transaction_service.get_account_history(self.current_user.account_id)
        
        page = 0
        total_pages = (len(history) + PAGINATION_LIMIT - 1) // PAGINATION_LIMIT if history else 1
        
        while True:
            clear_screen()
            print_header(f"HISTORIAL DE TRANSACCIONES (Pág {page+1}/{total_pages})")
            
            start_idx = page * PAGINATION_LIMIT
            end_idx = start_idx + PAGINATION_LIMIT
            current_page_txs = history[start_idx:end_idx]
            
            headers = ["Fecha/Hora", "Tipo", "Monto"]
            rows = []
            
            for tx in current_page_txs:
                dt = tx.timestamp[:16].replace('T', ' ')
                tipo = tx.transaction_type.upper()
                
                # Formatear el monto según si es ingreso o egreso
                outgoing_types = ['retiro', 'transferencia', 'pago_credito', 'pago_tarjeta', 'avance_tarjeta', 'disposicion_credito', 'comision']
                is_outgoing = tx.account_id == self.current_user.account_id and tx.transaction_type in outgoing_types
                
                if is_outgoing:
                    monto_str = f"{Colors.FAIL}- {format_currency(tx.amount)}{Colors.ENDC}"
                else:
                    monto_str = f"{Colors.OKGREEN}+ {format_currency(tx.amount)}{Colors.ENDC}"
                    
                rows.append([dt, tipo[:14], monto_str])
                
            print_table(headers, rows, [16, 15, 20])
            
            print(f"\n{Colors.OKCYAN}[N] Siguiente  [A] Anterior  [0] Volver{Colors.ENDC}")
            opt = input(">>> ").strip().lower()
            if opt == 'n' and page < total_pages - 1:
                page += 1
            elif opt == 'a' and page > 0:
                page -= 1
            elif opt == '0':
                break

    def change_pin(self):
        header = "CAMBIO DE PIN"
        try:
            current_pin = get_simple_pin("Ingrese PIN actual", header)
            self.account_service.verify_pin(self.current_user, current_pin)
            
            new_pin = get_valid_pin("Nuevo PIN", self.current_user.owner_id, header)
            # Aplicamos el nuevo hash
            self.current_user.pin = self.account_service._hash_pin(new_pin, self.current_user.account_id)
            self.account_service.update_account(self.current_user)
            
            print_success("PIN actualizado exitosamente.")
            self.pause()
        except CancelOperationException:
            print_error("Operación cancelada por el usuario.")
            self.pause()
        except BankException as e:
            print_error(str(e))
            self.pause()

    def personal_data(self):
        clear_screen()
        print_header("MIS DATOS PERSONALES")
        print_box([
            f"Titular:       {self.current_user.owner_name}",
            f"Documento ID:  {self.current_user.owner_id}",
            f"Teléfono:      {self.current_user.phone}",
            f"Correo:        {self.current_user.email}",
            f"Tipo de Cuenta:{self.current_user.account_type.capitalize()}",
            f"N° de Cuenta:  {self.current_user.account_number}",
            f"Fecha Creación:{self.current_user.created_at[:10]}"
        ])
        self.pause()

    def view_products(self):
        while True:
            clear_screen()
            print_header("MIS TARJETAS Y PRODUCTOS")
            
            print("  [1] Ver mis tarjetas")
            print("  [2] Ver mis créditos y préstamos")
            print("  [3] Ver mis inversiones y ahorros")
            print("  [0] Volver al menú principal")
            
            opc = input(f"\n{Colors.OKCYAN}>>> {Colors.ENDC}").strip()
            
            if opc == '0':
                break
            elif opc == '1':
                self._show_cards()
            elif opc == '2':
                self._show_loans()
            elif opc == '3':
                self._show_investments()
            else:
                print_error("Opción inválida.")
                self.pause()

    def _show_cards(self):
        clear_screen()
        print_header("MIS TARJETAS")
        products = self.product_service.get_products_by_account(self.current_user.account_id)
        
        # Tarjeta Débito por defecto de la cuenta
        print_box([
            f"Tarjeta Débito (Básica)",
            f"Número:           {self.current_user.account_number}",
            f"Saldo Disponible: {format_currency(self.current_user.balance)}"
        ])
        
        # Otras tarjetas (Crédito, etc)
        tarjetas = [p for p in products if p.product_category == "tarjeta"]
        for p in tarjetas:
            if p.product_type == "credito":
                print_box([
                    f"Tarjeta Crédito:  {p.details.get('numero_tarjeta', 'N/A')}",
                    f"Estado:           {p.status.capitalize()}",
                    f"Cupo Aprobado:    {format_currency(p.details.get('cupo_aprobado', 0))}",
                    f"Deuda Actual:     {format_currency(p.details.get('deuda_actual', 0))}",
                    f"Cupo Disponible:  {format_currency(p.details.get('disponible', 0))}"
                ])
            else:
                print_box([
                    f"Tarjeta {p.product_type.capitalize()}",
                    f"Estado: {p.status.capitalize()}"
                ])
        self.pause()

    def _show_loans(self):
        clear_screen()
        print_header("CRÉDITOS Y PRÉSTAMOS ACTIVOS")
        loans = self.loan_service.get_loans_by_account(self.current_user.account_id)
        
        if not loans:
            print_warning("No tiene créditos ni préstamos activos.")
        else:
            for l in loans:
                abonado = max(0, l.principal - l.remaining_balance)
                print_box([
                    f"Tipo:       {l.loan_type.capitalize()}",
                    f"Estado:     {l.status.capitalize()}",
                    f"Aceptado:   {format_currency(l.principal)}",
                    f"Disponible: {format_currency(l.fondos_disponibles)}",
                    f"Abonado:    {format_currency(abonado)}",
                    f"Deuda:      {format_currency(l.remaining_balance)}",
                    f"Cuota:      {format_currency(l.monthly_installment)}"
                ])
        self.pause()

    def _show_investments(self):
        clear_screen()
        print_header("INVERSIONES Y AHORRO")
        products = self.product_service.get_products_by_account(self.current_user.account_id)
        ahorros = [p for p in products if p.product_type == "programado"]
        fondos = [p for p in products if p.product_type == "fondo"]
        otros = [p for p in products if p.product_category != "tarjeta" and p.product_type not in ("programado", "fondo")]
        
        if not ahorros and not fondos and not otros:
            print_warning("No tiene inversiones ni ahorros adicionales contratados.")
            self.pause()
            return
            
        if ahorros:
            print(f"\n{Colors.OKGREEN}=== MIS AHORROS PROGRAMADOS ==={Colors.ENDC}")
            for p in ahorros:
                nombre = p.details.get('nombre', '')
                meta = p.details.get('meta', 0)
                cuota = p.details.get('cuota_mensual', 0)
                dia = p.details.get('dia_retiro', 1)
                saldo = p.details.get('saldo_actual', 0)
                print_box([
                    f"Propósito:     {nombre}",
                    f"Meta Total:    {format_currency(meta)}",
                    f"Saldo Ahorro:  {format_currency(saldo)}",
                    f"Cuota Mensual: {format_currency(cuota)}",
                    f"Día de Débito: {dia} de cada mes",
                    f"Estado:        {p.status.capitalize()}"
                ])
                
        if fondos:
            print(f"\n{Colors.WARNING}=== MIS FONDOS DE INVERSIÓN ==={Colors.ENDC}")
            for p in fondos:
                nombre = p.details.get('nombre', '')
                monto_ini = p.details.get('monto_inicial', 0)
                saldo = p.details.get('saldo_actual', 0)
                tasa = p.details.get('tasa_mensual', 0.08)
                print_box([
                    f"Fondo:         {nombre}",
                    f"Inversión Base:{format_currency(monto_ini)}",
                    f"Saldo Actual:  {format_currency(saldo)}",
                    f"Rendimientos:  {format_currency(saldo - monto_ini)}",
                    f"Tasa Retorno:  {tasa*100}% Mensual",
                    f"Estado:        {p.status.capitalize()}"
                ])
                
        if otros:
            print(f"\n{Colors.OKCYAN}=== OTROS PRODUCTOS ==={Colors.ENDC}")
            for p in otros:
                print_box([
                    f"Categoría: {p.product_category.capitalize()}",
                    f"Tipo:      {p.product_type.capitalize()}",
                    f"Estado:    {p.status.capitalize()}"
                ])
                
        self.pause()

    def request_product(self):
        header = "SOLICITAR PRODUCTO"
        clear_screen()
        print_header(header)
        print("  [1] Créditos")
        print("  [2] Ahorro / Inversión")
        print("  [3] Tarjetas")
        print("  [C] Cancelar")
        
        choice = input(f"\n{Colors.OKCYAN}Seleccione categoría >>> {Colors.ENDC}").strip().lower()
        if choice == 'c': return
        
        try:
            if choice == '1':
                print_guide("1. Libranza | 2. Libre Inversión | 3. Vehicular | 4. Vivienda")
                sub = input("Seleccione crédito >>> ").strip()
                if sub == 'c': return
                
                if sub == '1':
                    monto = get_valid_amount("Monto solicitado: $", 500000, 100000000, header)
                    ingreso = get_valid_amount("Su salario mensual: $", 1000000, 50000000, header)
                    meses = int(get_valid_amount("Plazo en meses (12-72): ", 12, 72, header))
                    loan = self.loan_service.request_loan(self.current_user, "libranza", monto, meses, ingreso)
                elif sub == '2':
                    monto = get_valid_amount("Monto solicitado: $", 1000000, 50000000, header)
                    ingreso = get_valid_amount("Su ingreso mensual: $", 1000000, 50000000, header)
                    meses = int(get_valid_amount("Plazo en meses (12-60): ", 12, 60, header))
                    loan = self.loan_service.request_loan(self.current_user, "libre_inversion", monto, meses, ingreso)
                elif sub == '3':
                    veh_valor = get_valid_amount("Valor del vehículo: $", 15000000, 300000000, header)
                    monto = get_valid_amount("Monto a financiar: $", 10000000, veh_valor*0.8, header)
                    ingreso = get_valid_amount("Su ingreso mensual: $", 1000000, 50000000, header)
                    meses = int(get_valid_amount("Plazo en meses (12-84): ", 12, 84, header))
                    loan = self.loan_service.request_loan(self.current_user, "vehicular", monto, meses, ingreso)
                elif sub == '4':
                    viv_valor = get_valid_amount("Valor del inmueble: $", 80000000, 1000000000, header)
                    monto = get_valid_amount("Monto a financiar: $", 30000000, viv_valor*0.7, header)
                    ingreso = get_valid_amount("Su ingreso mensual: $", 2000000, 50000000, header)
                    meses = int(get_valid_amount("Plazo en años (5-30): ", 5, 30, header)) * 12
                    loan = self.loan_service.request_loan(self.current_user, "vivienda", monto, meses, ingreso)
                else:
                    print_error("Opción inválida.")
                    self.pause()
                    return
                
                if loan.status == "activo":
                    print_success(f"Crédito aprobado. Cuota: {format_currency(loan.monthly_installment)}. ¡Monto {format_currency(loan.principal)} disponible para retiro/transferencia!")
                else:
                    print_error("Crédito rechazado por capacidad de endeudamiento (Cuota mayor al 30% del ingreso).")
                    
            elif choice == '2':
                print_guide("1. Ahorro programado | 2. Fondo de inversión")
                sub = input(f"{Colors.OKCYAN}Seleccione >>> {Colors.ENDC}").strip()
                if sub == '1':
                    nombre = input(f"{Colors.OKCYAN}Propósito del Ahorro (Ej. Futura Casa): {Colors.ENDC}").strip() or "Ahorro Programado"
                    meta = get_valid_amount("Meta de ahorro total esperada: $", 100000, 1000000000, header)
                    meses = int(get_valid_amount("Plazo de ahorro (en meses): ", 1, 120, header))
                    dia = int(get_valid_amount("Día del mes para el débito automático (1-28): ", 1, 28, header))
                    
                    cuota_mensual = meta / meses
                    
                    details = {
                        "nombre": nombre,
                        "meta": meta,
                        "meses": meses,
                        "dia_retiro": dia,
                        "cuota_mensual": cuota_mensual,
                        "saldo_actual": 0.0
                    }
                    self.product_service.create_product(self.current_user, "ahorro", "programado", details)
                    
                    clear_screen()
                    print_success("¡Ahorro Programado creado exitosamente!")
                    print(f"\n{Colors.OKCYAN}=== RECIBO DE CONSTITUCIÓN DE AHORRO ==={Colors.ENDC}")
                    print_box([
                        f"Producto:        Ahorro Programado",
                        f"Propósito:       {nombre}",
                        f"Meta Total:      {format_currency(meta)}",
                        f"Plazo (Meses):   {meses}",
                        f"Cuota Mensual:   {format_currency(cuota_mensual)}",
                        f"Día de Débito:   {dia} de cada mes"
                    ])
                    
                elif sub == '2':
                    nombre = input(f"{Colors.OKCYAN}Nombre del Fondo (Ej. Fondo Universitario): {Colors.ENDC}").strip() or "Fondo de Inversión"
                    monto = get_valid_amount("Inversión inicial: $", 500000, 1000000000, header)
                    tasa = 0.08
                    
                    details = {
                        "nombre": nombre,
                        "monto_inicial": monto,
                        "saldo_actual": monto,
                        "tasa_mensual": tasa
                    }
                    self.product_service.create_product(self.current_user, "inversion", "fondo", details)
                    
                    # Para la inversión retiramos el dinero de la cuenta real
                    self.current_user.balance -= monto
                    self.account_service.update_account(self.current_user)
                    from models.transaction import Transaction
                    tx = Transaction(self.current_user.account_id, transaction_type="retiro", amount=monto, balance_before=self.current_user.balance+monto, balance_after=self.current_user.balance, description="Constitución de Fondo de Inversión")
                    self.transaction_service._append_transaction(tx)
                    
                    clear_screen()
                    print_success("¡Fondo de Inversión constituido exitosamente!")
                    print(f"\n{Colors.OKCYAN}=== RECIBO DE INVERSIÓN ==={Colors.ENDC}")
                    print_box([
                        f"Producto:        Fondo de Inversión",
                        f"Nombre:          {nombre}",
                        f"Inversión Base:  {format_currency(monto)}",
                        f"Tasa de Retorno: {tasa*100}% Mensual",
                        f"Crec. Esperado:  {format_currency(monto * tasa)} por mes"
                    ])
                    
            elif choice == '3':
                print_guide("1. Tarjeta Crédito | 2. Tarjeta Débito Beneficios")
                sub = input("Seleccione >>> ").strip()
                if sub == '1':
                    cupo = max(1000000.0, self.current_user.balance * 0.5)
                    import random
                    num_tarjeta = f"4123-{random.randint(1000,9999):04d}-{random.randint(1000,9999):04d}-{random.randint(1000,9999):04d}"
                    detalles = {
                        "numero_tarjeta": num_tarjeta,
                        "cupo_aprobado": cupo,
                        "deuda_actual": 0.0,
                        "disponible": cupo
                    }
                    self.product_service.create_product(self.current_user, "tarjeta", "credito", detalles)
                    print_success(f"Tarjeta de crédito aprobada. Cupo asignado: {format_currency(cupo)}.")
                elif sub == '2':
                    self.product_service.create_product(self.current_user, "tarjeta", "debito", {"beneficios": True})
                    print_success("Nueva tarjeta débito generada.")
                    
        except CancelOperationException:
            pass
        self.pause()

    def keys_portal(self):
        while True:
            header = "PORTAL DE LLAVES (TRANSFIYA)"
            clear_screen()
            print_header(header)
            
            keys = self.key_service.get_keys_by_account(self.current_user.account_id)
            
            print_guide("Transfiere a otros contactos usando solo su alias, teléfono o email.")
            if keys:
                print(f"\n{Colors.OKCYAN}TUS LLAVES ACTIVAS:{Colors.ENDC}")
                for k in keys:
                    print_box([
                        f"Tipo:  {k.key_type.upper()}",
                        f"Valor: {k.key_value}"
                    ])
            else:
                print_warning("No tienes llaves registradas. Registra una para que te transfieran.")
                
            print(f"\n{Colors.OKCYAN}OPCIONES DEL PORTAL:{Colors.ENDC}")
            print("  [1] Transferir fondos a una llave")
            print("  [2] Registrar nueva llave")
            print("  [0] Volver al menú principal")
            
            opc = input(f"\n{Colors.OKCYAN}>>> {Colors.ENDC}").strip()
            if opc == '0':
                break
            elif opc == '1':
                self._transfer_by_key_logic(header)
            elif opc == '2':
                self._register_key_logic(header)
            else:
                print_error("Opción inválida.")
                self.pause()

    def _transfer_by_key_logic(self, header):
        clear_screen()
        print_header("TRANSFERIR A LLAVE")
        try:
            key_val = input(f"{Colors.OKCYAN}Ingrese la llave destino (Celular, Correo, Alias): {Colors.ENDC}").strip()
            if key_val.lower() == 'c': raise CancelOperationException()
            
            target_account = self.key_service.resolve_key(key_val)
            print_guide(f"Destinatario verificado: {target_account.owner_name} (Cuenta N° {target_account.account_number})")
            
            amount = get_valid_amount("Monto a transferir: $", 1000, 10000000, header)
            pin = get_simple_pin("PIN de Seguridad para autorizar", header)
            
            self.transaction_service.transfer(self.current_user, target_account.account_number, amount, pin, f"Transfiya a llave: {key_val}")
            print_success(f"Transferencia de {format_currency(amount)} exitosa.")
        except CancelOperationException:
            pass
        except BankException as e:
            print_error(str(e))
        self.pause()

    def _register_key_logic(self, header):
        clear_screen()
        print_header("REGISTRAR NUEVA LLAVE")
        print_guide("Elija el tipo de llave que desea registrar a su cuenta actual.")
        print("  [1] Número Celular")
        print("  [2] Correo Electrónico")
        print("  [3] Alias")
        print("  [C] Cancelar")
        
        opc = input(f"\n{Colors.OKCYAN}>>> {Colors.ENDC}").strip().lower()
        if opc == 'c': return
        
        tipo_map = {'1': 'celular', '2': 'correo', '3': 'alias'}
        tipo = tipo_map.get(opc)
        if not tipo:
            print_error("Opción inválida.")
            self.pause()
            return
            
        val = input(f"{Colors.OKCYAN}Ingrese su {tipo}: {Colors.ENDC}").strip()
        if val.lower() == 'c': return
        
        try:
            self.key_service.register_key(self.current_user, tipo, val)
            print_success(f"¡Llave tipo '{tipo}' registrada con éxito! Ya pueden transferirte a este dato.")
        except BankException as e:
            print_error(str(e))
        self.pause()

    def pay_loans(self):
        while True:
            header = "PAGAR MIS CUENTAS"
            clear_screen()
            print_header(header)
            
            print("  [1] Pagar Tarjeta de Crédito")
            print("  [2] Pagar Préstamos / Créditos")
            print("  [0] Volver al menú principal")
            
            opc = input(f"\n{Colors.OKCYAN}>>> {Colors.ENDC}").strip()
            
            if opc == '0':
                break
            elif opc == '1':
                self._pay_credit_cards(header)
            elif opc == '2':
                self._pay_active_loans(header)
            else:
                print_error("Opción inválida.")
                self.pause()

    def _pay_active_loans(self, header):
        clear_screen()
        print_header("PAGO DE PRÉSTAMOS")
        loans = self.loan_service.get_loans_by_account(self.current_user.account_id)
        active_loans = [l for l in loans if l.status == "activo" and l.remaining_balance > 0]
        
        if not active_loans:
            print_warning("No tiene créditos activos con deuda pendiente.")
            self.pause()
            return
            
        for i, l in enumerate(active_loans):
            abonado = max(0, l.principal - l.remaining_balance)
            print_box([
                f"ID Opción: [{i}]",
                f"Crédito:   {l.loan_type.capitalize()}",
                f"Abonado:   {format_currency(abonado)}",
                f"Deuda:     {format_currency(l.remaining_balance)}",
                f"Cuota:     {format_currency(l.monthly_installment)}"
            ])
            
        try:
            sel = input(f"\n{Colors.OKCYAN}Seleccione el ID del crédito a pagar (o 'C' para cancelar): {Colors.ENDC}").strip()
            if sel.lower() == 'c': return
            if not sel.isdigit(): raise ValueError()
            idx = int(sel)
            if idx < 0 or idx >= len(active_loans):
                print_error("ID inválido.")
                self.pause()
                return
                
            loan = active_loans[idx]
            min_pay = min(loan.monthly_installment, loan.remaining_balance)
            print_guide(f"Valor de la cuota mensual: {format_currency(loan.monthly_installment)}. El pago mínimo es esta cuota. Puede abonar un valor mayor para pago a capital.")
            monto = get_valid_amount("Monto a pagar: $", min_pay, loan.remaining_balance, header)
            
            pin = get_simple_pin("PIN de Seguridad", header)
            self.account_service.verify_pin(self.current_user, pin)
            
            self.loan_service.pay_installment(self.current_user, loan.loan_id, monto, self.account_service, self.transaction_service)
            
            # Re-fetch the loan to check its new status
            updated_loan = next((l for l in self.loan_service.get_all_loans() if l.loan_id == loan.loan_id), None)
            
            if updated_loan and updated_loan.status == "pagado":
                clear_screen()
                intereses = (loan.monthly_installment * loan.term_months) - loan.principal
                total_pagado = loan.principal + intereses
                
                print_success("¡Felicitaciones! Ha liquidado totalmente su crédito.")
                print(f"{Colors.WARNING}Gracias por confiar en nuestro Banco para impulsar sus proyectos financieros.{Colors.ENDC}")
                print(f"\n{Colors.OKCYAN}=== FACTURA DE LIQUIDACIÓN DE CRÉDITO ==={Colors.ENDC}")
                print_box([
                    f"Tipo de Crédito:  {loan.loan_type.capitalize()}",
                    f"Capital Prestado: {format_currency(loan.principal)}",
                    f"Intereses Totales:{format_currency(intereses)}",
                    f"TOTAL PAGADO:     {format_currency(total_pagado)}"
                ])
                
                # Borrar el crédito como solicitó el usuario
                all_loans = self.loan_service.get_all_loans()
                all_loans = [l for l in all_loans if l.loan_id != loan.loan_id]
                self.loan_service._save_loans(all_loans)
                print_guide("El registro de este crédito ha sido archivado y eliminado de sus productos activos.")
            else:
                print_success(f"Pago de {format_currency(monto)} aplicado correctamente a su crédito.")
            
        except ValueError:
            print_error("Entrada inválida.")
        except CancelOperationException:
            pass
        except BankException as e:
            print_error(str(e))
        self.pause()

    def _pay_credit_cards(self, header):
        clear_screen()
        print_header("PAGO DE TARJETAS DE CRÉDITO")
        
        products = self.product_service.get_products_by_account(self.current_user.account_id)
        credit_cards = [p for p in products if p.product_type == "credito" and p.details.get('deuda_actual', 0) > 0]
        
        if not credit_cards:
            print_warning("No tiene tarjetas de crédito con deuda pendiente.")
            self.pause()
            return
            
        for i, tc in enumerate(credit_cards):
            deuda = tc.details.get('deuda_actual', 0)
            print_box([
                f"ID Opción: [{i}]",
                f"Tarjeta:   {tc.details.get('numero_tarjeta')}",
                f"Deuda:     {format_currency(deuda)}"
            ])
            
        try:
            opc = input(f"\n{Colors.OKCYAN}Seleccione el ID de la tarjeta a pagar (o 'C' para cancelar): {Colors.ENDC}").strip()
            if opc.lower() == 'c': return
            if not opc.isdigit(): raise ValueError()
            idx = int(opc)
            if idx < 0 or idx >= len(credit_cards):
                print_error("Opción fuera de rango.")
                self.pause()
                return
                
            tc = credit_cards[idx]
            deuda = tc.details.get('deuda_actual', 0)
            
            print_guide(f"Deuda Total: {format_currency(deuda)}. Puede abonar parcialmente (Mínimo $1,000).")
            monto = get_valid_amount("Monto a pagar: $", 1000, deuda, header)
            
            pin = get_simple_pin("PIN de Seguridad", header)
            self.account_service.verify_pin(self.current_user, pin)
            
            if self.current_user.balance < monto:
                raise BankException("Saldo insuficiente en su cuenta principal para realizar este pago.")
                
            balance_before = self.current_user.balance
            self.current_user.balance -= monto
            self.account_service.update_account(self.current_user)
            
            tc.details['deuda_actual'] -= monto
            tc.details['disponible'] += monto
            
            prods = self.product_service.get_all_products()
            for k, p in enumerate(prods):
                if p.product_id == tc.product_id: prods[k] = tc
            self.product_service._save_products(prods)
            
            from models.transaction import Transaction
            tx = Transaction(
                account_id=self.current_user.account_id,
                transaction_type="pago_tarjeta",
                amount=monto,
                balance_before=balance_before,
                balance_after=self.current_user.balance,
                description=f"Pago a TC {tc.details.get('numero_tarjeta')}"
            )
            self.transaction_service._append_transaction(tx)
            
            print_success(f"Pago de Tarjeta de Crédito por {format_currency(monto)} registrado con éxito.")
            
        except ValueError:
            print_error("Entrada inválida.")
        except CancelOperationException:
            pass
        except BankException as e:
            print_error(str(e))
        self.pause()

    def fund_investments(self):
        header = "APORTES A INVERSIÓN Y AHORRO"
        clear_screen()
        print_header(header)
        
        products = self.product_service.get_products_by_account(self.current_user.account_id)
        inversiones = [p for p in products if p.product_category != "tarjeta"]
        
        if not inversiones:
            print_warning("No tiene inversiones ni ahorros contratados.")
            self.pause()
            return
            
        for i, p in enumerate(inversiones):
            if p.product_type == "programado":
                saldo = p.details.get('saldo_actual', 0)
                cuota = p.details.get('cuota_mensual', 0)
                print_box([
                    f"ID Opción: [{i}]",
                    f"Producto:  Ahorro Programado",
                    f"Saldo:     {format_currency(saldo)}",
                    f"Cuota Sug: {format_currency(cuota)}"
                ])
            elif p.product_type == "fondo":
                saldo = p.details.get('saldo_actual', 0)
                print_box([
                    f"ID Opción: [{i}]",
                    f"Producto:  Fondo de Inversión",
                    f"Saldo:     {format_currency(saldo)}"
                ])
                
        try:
            opc = input(f"\n{Colors.OKCYAN}Seleccione el ID del producto (o 'C' para cancelar): {Colors.ENDC}").strip()
            if opc.lower() == 'c': return
            if not opc.isdigit(): raise ValueError()
            idx = int(opc)
            if idx < 0 or idx >= len(inversiones):
                raise BankException("Opción fuera de rango.")
                
            inv = inversiones[idx]
            if inv.product_type == "programado":
                monto = get_valid_amount("Monto a aportar: $", 1000, 100000000, header)
            else:
                monto = get_valid_amount("Monto a invertir: $", 10000, 1000000000, header)
                
            pin = get_simple_pin("PIN de Seguridad", header)
            self.account_service.verify_pin(self.current_user, pin)
            
            if self.current_user.balance < monto:
                raise BankException("Saldo insuficiente en su cuenta principal.")
                
            # Deduct from account
            self.current_user.balance -= monto
            self.account_service.update_account(self.current_user)
            
            # Add to investment
            inv.details['saldo_actual'] = inv.details.get('saldo_actual', 0) + monto
            if inv.product_type == "fondo":
                inv.details['monto_inicial'] = inv.details.get('monto_inicial', 0) + monto
                
            prods = self.product_service.get_all_products()
            for k, p in enumerate(prods):
                if p.product_id == inv.product_id: prods[k] = inv
            self.product_service._save_products(prods)
            
            # Create transaction
            from models.transaction import Transaction
            tx = Transaction(self.current_user.account_id, transaction_type="retiro", amount=monto, balance_before=self.current_user.balance+monto, balance_after=self.current_user.balance, description=f"Aporte a {inv.product_type.capitalize()} ({inv.details.get('nombre', '')})")
            self.transaction_service._append_transaction(tx)
            
            # Check meta cumplida for Ahorro Programado
            if inv.product_type == "programado" and inv.details['saldo_actual'] >= inv.details.get('meta', float('inf')):
                clear_screen()
                print_success(f"¡Felicidades! Ha alcanzado la meta de su Ahorro: {inv.details.get('nombre', '')}")
                print(f"Saldo Actual: {format_currency(inv.details['saldo_actual'])} | Meta Original: {format_currency(inv.details.get('meta', 0))}")
                print("\n¿Qué desea hacer con su ahorro?")
                print("  [1] Aumentar meta y continuar ahorrando")
                print("  [2] Retirar el ahorro a mi cuenta principal")
                opc_meta = input(f"\n{Colors.OKCYAN}>>> {Colors.ENDC}").strip()
                
                if opc_meta == '1':
                    nueva_meta = get_valid_amount("Nueva Meta de ahorro total esperada: $", inv.details['saldo_actual'] + 10000, 1000000000, header)
                    meses = int(get_valid_amount("Nuevo plazo adicional (en meses): ", 1, 120, header))
                    dia = int(get_valid_amount("Día del mes para el débito automático (1-28): ", 1, 28, header))
                    
                    inv.details['meta'] = nueva_meta
                    inv.details['meses'] = meses
                    inv.details['dia_retiro'] = dia
                    inv.details['cuota_mensual'] = (nueva_meta - inv.details['saldo_actual']) / meses
                    
                    for k, p in enumerate(prods):
                        if p.product_id == inv.product_id: prods[k] = inv
                    self.product_service._save_products(prods)
                    print_success("La meta y las condiciones de su ahorro han sido actualizadas.")
                    
                elif opc_meta == '2':
                    saldo_a_retirar = inv.details['saldo_actual']
                    self.current_user.balance += saldo_a_retirar
                    self.account_service.update_account(self.current_user)
                    
                    tx_ret = Transaction(self.current_user.account_id, transaction_type="deposito", amount=saldo_a_retirar, balance_before=self.current_user.balance-saldo_a_retirar, balance_after=self.current_user.balance, description=f"Retiro de Ahorro Cumplido ({inv.details.get('nombre', '')})")
                    self.transaction_service._append_transaction(tx_ret)
                    
                    # Inactivate or delete product
                    prods = [p for p in prods if p.product_id != inv.product_id]
                    self.product_service._save_products(prods)
                    
                    print_success(f"El ahorro por {format_currency(saldo_a_retirar)} ha sido depositado en su cuenta principal exitosamente.")
                    self.pause()
                    return
            
            clear_screen()
            print_success("¡Aporte realizado con éxito!")
            print(f"\n{Colors.OKCYAN}=== COMPROBANTE DE APORTE ==={Colors.ENDC}")
            nuevo_saldo = inv.details['saldo_actual']
            
            if inv.product_type == "fondo":
                tasa = inv.details.get('tasa_mensual', 0.08)
                crec_esperado = nuevo_saldo * tasa
                print_box([
                    f"Producto:        {inv.product_type.capitalize()}",
                    f"Aporte Realizado:{format_currency(monto)}",
                    f"Nuevo Saldo Total:{format_currency(nuevo_saldo)}",
                    f"Tasa Crecimiento:{tasa*100}% Mensual",
                    f"Crecimiento Est.:{format_currency(crec_esperado)} por mes"
                ])
            else:
                print_box([
                    f"Producto:        {inv.product_type.capitalize()}",
                    f"Aporte Realizado:{format_currency(monto)}",
                    f"Nuevo Saldo Total:{format_currency(nuevo_saldo)}"
                ])
            
        except ValueError:
            print_error("Entrada inválida.")
        except CancelOperationException:
            pass
        except BankException as e:
            print_error(str(e))
        self.pause()
