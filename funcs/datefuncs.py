from datetime import datetime


def format_curr_datetime(format='%Y%m%d%H%M%S'):
    return str(datetime.now().strftime(format))


def format_curr_date(format='%Y%m%d'):
    return str(datetime.now().strftime(format))


def format_curr_time(format='%H%M%S'):
    return str(datetime.now().strftime(format))
