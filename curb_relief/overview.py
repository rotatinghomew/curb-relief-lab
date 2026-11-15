from datetime import datetime


def parse_time(value):
    return datetime.fromisoformat(value)


def summarize(release):
    tables = release["tables"]
    cutoff = release["cutoff"]
    trips = tables['trips']
    closed = [row for row in trips if row['left'] is not None]
    minutes = [max(0, (parse_time(row['left']) - parse_time(row['entered'])).total_seconds() / 60) for row in closed]
    return {'observed_trips': len(trips), 'closed_trips': len(closed), 'open_trips': len(trips)-len(closed), 'closed_minutes': sum(minutes), 'vehicles': len({row['vehicle_id'] for row in trips})}
