from datetime import datetime
import email, pytz

def convert_date(d):
    utctimestamp = email.Utils.mktime_tz(email.Utils.parsedate_tz(d))
    utcdate = datetime.fromtimestamp(utctimestamp, pytz.utc)
    return utcdate
