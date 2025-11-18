# Em store/core/exceptions.py


class BaseException(Exception):
    """Exceção base para a aplicação."""

    pass


class DatabaseException(BaseException):
    """Levantada quando ocorre um erro na camada da base de dados."""

    pass
