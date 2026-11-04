"""Explicit moderator decisions and expiring report-scoped appeal capabilities."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from . import pipeline, storage


def now():
    return datetime.now(timezone.utc)


def public_claim(row):
    return {key: value for key, value in row.items() if key not in {'history', 'appeal_access', 'appeals'}}


def reviewer_claim(row):
    return {key: value for key, value in row.items() if key != 'appeal_access'}


def find(rows, identifier):
    for row in rows:
        if row['id'] == identifier:
            return row
    raise HTTPException(404, 'Report not found')


def reason_text(value):
    if not isinstance(value, str) or not 10 <= len(value.strip()) <= 2000:
        raise HTTPException(422, 'Explain the decision in 10 to 2000 characters.')
    return value.strip()


def event(row, kind, reason, actor, **details):
    row['version'] = row.get('version', 0) + 1
    row.setdefault('history', []).append({'kind': kind, 'reason': reason, 'actor': actor,
                                        'at': now().isoformat(), 'version': row['version'], **details})


def check_version(row, expected):
    if type(expected) is not int or expected != row.get('version', 0):
        raise HTTPException(409, 'This report changed. Refresh it before making a decision.')


def decide(identifier, status, reason, expected):
    if status not in {'confirmed', 'rejected'}:
        raise HTTPException(400, 'Choose confirmation or dismissal.')
    def update(rows):
        row = find(rows, identifier)
        explanation = reason_text(reason)
        check_version(row, expected)
        if row['status'] != 'under_review':
            raise HTTPException(409, 'This report already has a decision. Use the appeal review process.')
        previous = row['status']
        row['status'] = status
        event(row, 'moderator_decision', explanation, 'Moderator', from_status=previous, to_status=status)
        return reviewer_claim(row)
    return storage.mutate(pipeline.active_db(), update)


def issue_access(identifier):
    token = secrets.token_urlsafe(32)
    expires = (now() + timedelta(days=7)).isoformat()
    def update(rows):
        row = find(rows, identifier)
        if row['status'] != 'confirmed':
            raise HTTPException(409, 'Appeal access is available for confirmed reports.')
        row['appeal_access'] = {'token_sha256': hashlib.sha256(token.encode()).hexdigest(), 'expires_at': expires}
        event(row, 'appeal_access_issued', 'Report-scoped appeal access issued for seven days.', 'Moderator')
        return {'token': token, 'expires_at': expires, 'version': row['version']}
    return storage.mutate(pipeline.active_db(), update)


def authorized(rows, token):
    if not isinstance(token, str) or not 32 <= len(token) <= 128:
        raise HTTPException(401, 'Invalid or expired appeal access.')
    digest = hashlib.sha256(token.encode()).hexdigest()
    for row in rows:
        access = row.get('appeal_access', {})
        if access.get('token_sha256') and secrets.compare_digest(access['token_sha256'], digest):
            if datetime.fromisoformat(access['expires_at']) > now():
                return row
    raise HTTPException(401, 'Invalid or expired appeal access.')


def appeal_detail(token):
    row = authorized(pipeline._load(), token)
    # Neither raw analysis, other reports nor reviewer evidence is disclosed.
    return {'claim': {key: row.get(key) for key in ['id', 'suspect_handle', 'status', 'version']},
            'decisions': [e for e in row.get('history', []) if e['kind'] in {'moderator_decision', 'appeal_resolved'}],
            'appeals': row.get('appeals', [])}


def submit_appeal(token, reason):
    explanation = reason_text(reason)
    def update(rows):
        row = authorized(rows, token)
        if row['status'] != 'confirmed' or any(a['status'] == 'pending' for a in row.get('appeals', [])):
            raise HTTPException(409, 'This report cannot accept another pending appeal.')
        appeal = {'id': secrets.token_hex(8), 'reason': explanation, 'status': 'pending', 'created_at': now().isoformat()}
        row.setdefault('appeals', []).append(appeal)
        event(row, 'appeal_submitted', explanation, 'Appeal access holder')
        return appeal
    return storage.mutate(pipeline.active_db(), update)


def pending_appeals():
    return [{'claim': reviewer_claim(row), 'appeal': appeal} for row in pipeline._load()
            for appeal in row.get('appeals', []) if appeal['status'] == 'pending']


def resolve(identifier, outcome, reason, expected):
    explanation = reason_text(reason)
    if outcome not in {'uphold', 'overturn'}:
        raise HTTPException(422, 'Choose uphold or overturn.')
    def update(rows):
        for row in rows:
            for appeal in row.get('appeals', []):
                if appeal['id'] != identifier:
                    continue
                check_version(row, expected)
                if appeal['status'] != 'pending' or row['status'] != 'confirmed':
                    raise HTTPException(409, 'This appeal already has a decision.')
                previous = row['status']
                if outcome == 'overturn':
                    row['status'] = 'rejected'
                appeal.update(status=outcome, resolved_at=now().isoformat(), resolution_reason=explanation)
                event(row, 'appeal_resolved', explanation, 'Moderator', appeal_id=identifier,
                      outcome=outcome, from_status=previous, to_status=row['status'])
                return reviewer_claim(row)
        raise HTTPException(404, 'Appeal not found')
    return storage.mutate(pipeline.active_db(), update)
