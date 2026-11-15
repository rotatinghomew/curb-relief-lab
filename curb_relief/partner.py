from datetime import datetime


def parse_time(value):
    return datetime.fromisoformat(value)


import math
from datetime import timedelta


def operate(path, payload, release):
    if path != '/v1/quote':
        raise LookupError('报价接口不存在')
    trip = next(row for row in release['tables']['trips'] if row['trip_id'] == payload['trip_id'])
    policy = next(row for row in release['tables']['policies'] if row['policy_id'] == payload['policy_id'])
    if trip['left'] is None:
        raise ValueError('行程尚未结束')
    start, end = parse_time(trip['entered']), parse_time(trip['left'])
    duration = (end-start).total_seconds()/60
    if payload['free_available'] and duration <= policy['grace_minutes']:
        return {'cents': 0, 'parts': [], 'consumes_quota': True, 'evidence': trip['trip_id'] + ':' + policy['policy_id']}
    deduction = bool(policy['deduct_grace'] and payload['free_available'])
    charged_start = min(end, start+timedelta(minutes=policy['grace_minutes'])) if deduction else start
    parts = []
    cursor = charged_start
    while cursor < end:
        night = cursor.hour >= 18 or cursor.hour < 8
        boundary = cursor.replace(hour=8 if cursor.hour<8 else 18 if cursor.hour<18 else 8, minute=0, second=0)
        if cursor.hour >= 18:
            boundary += timedelta(days=1)
        finish = min(end, boundary)
        amount = math.ceil((finish-cursor).total_seconds()/900)*policy['unit_cents']
        if night:
            amount = min(amount, policy['night_cap_cents'])
        parts.append({'start':cursor.isoformat(),'end':finish.isoformat(),'night':night,'cents':amount})
        cursor = finish
    return {'cents':sum(part['cents'] for part in parts),'parts':parts,'consumes_quota':deduction and duration>0,'evidence':trip['trip_id']+':'+policy['policy_id']}
