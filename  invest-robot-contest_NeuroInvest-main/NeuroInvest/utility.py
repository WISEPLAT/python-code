from datetime import datetime, timezone

def currentTimestamp():
    return int(datetime.now(timezone.utc).timestamp())