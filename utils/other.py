from datetime import datetime, timezone, timedelta

def convert_unix_to_msk(unix_time):

    date = datetime.utcfromtimestamp(unix_time)

    msk_time = date.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=3)))

    return msk_time.strftime('%d.%m.%Y %H:%M')

def format_report_data_to_text(data):
    return f'1. {data["count"]} {data["day_time"]}\n2. {data["replace_count"]}\n3. {data["balance_remain"]}'

