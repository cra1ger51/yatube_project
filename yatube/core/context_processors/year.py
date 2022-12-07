import datetime as dt


def year(request) -> int:
    """Добавляет переменную с текущим годом."""
    return {
        'year': dt.datetime.today().year
    }
