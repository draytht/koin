from datetime import date, timedelta


def start_of_month(d: date | None = None) -> date:
    d = d or date.today()
    return d.replace(day=1)


def days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


def format_date(d: date) -> str:
    return d.strftime("%b %d, %Y")
