import datetime

def timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
