class BankException(Exception):
    """Excepción base para el sistema bancario."""
    pass

class CancelOperationException(Exception):
    """Excepción lanzada cuando el usuario cancela una operación."""
    pass

class AccountNotFoundError(BankException):
    """Se busca una cuenta que no existe en el sistema."""
    pass

class InsufficientFundsError(BankException):
    """El saldo es insuficiente para el monto solicitado."""
    pass

class AccountInactiveError(BankException):
    """Se intenta operar sobre una cuenta bloqueada."""
    pass

class InvalidAmountError(BankException):
    """El monto ingresado es negativo, cero o supera límites."""
    pass

class InvalidPinError(BankException):
    """El PIN ingresado no coincide con el almacenado."""
    pass

class DailyLimitExceededError(BankException):
    """Se supera el límite diario de operaciones."""
    pass

class DuplicateAccountError(BankException):
    """Se intenta crear una cuenta ya existente."""
    pass

class DataCorruptionError(BankException):
    """El archivo JSON contiene datos inválidos o corruptos."""
    pass
