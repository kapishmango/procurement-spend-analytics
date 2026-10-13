"""Practice project 1: conservative supplier normalisation."""
import re
import unicodedata
from collections import defaultdict


def normalise_name(value):
    value = unicodedata.normalize('NFKC', value).casefold()
    value = re.sub(r'[^a-z0-9 ]', ' ', value)
    value = re.sub(r'\b(private|pvt|limited|ltd)\b', ' ', value)
    return ' '.join(value.split())


def normalise_suppliers(records):
    """Registration IDs anchor identity; name-only matches require review."""
    registrations = sorted({r['registration_id'] for r in records if r.get('registration_id')})
    canonical = {reg: f'S{index:02d}' for index, reg in enumerate(registrations, 1)}
    name_ids = defaultdict(set)
    for row in records:
        if row.get('registration_id'):
            name_ids[normalise_name(row['supplier_name'])].add(canonical[row['registration_id']])
    mapped = []
    for row in records:
        key = normalise_name(row['supplier_name'])
        identity = canonical.get(row.get('registration_id'))
        candidates = sorted(name_ids.get(key, set()))
        mapped.append({**row, 'normalised_name': key, 'canonical_supplier_id': identity,
                       'match_status': 'registration_id_match' if identity else 'manual_review',
                       'candidate_supplier_ids': [] if identity else candidates,
                       'review_reason': '' if identity else 'Missing registration ID; name similarity alone is insufficient.'})
    return mapped
