from datetime import datetime


def parse_power_usage(hundred_days_kwh_data):
    today = datetime.now()
    days = today.day

    monthly_usage = 0.0
    daily_usage = []

    for day in range(days):
        s = hundred_days_kwh_data[6 * day : 6 * day + 2]
        c = hundred_days_kwh_data[6 * day + 2 : 6 * day + 4]
        f = hundred_days_kwh_data[6 * day + 4 : 6 * day + 6]

        h = int(s, 16)
        y = int(c, 16)
        i_val = int(f, 16)

        usage = float(f"{h}.{y}{i_val}")
        daily_usage.append({"day": days - day, "usage": usage})
        monthly_usage += usage

    return {
        "monthly": monthly_usage,
        "daily": daily_usage,
    }
