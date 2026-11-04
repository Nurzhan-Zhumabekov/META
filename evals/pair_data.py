"""Procedural training pairs; all fictional, never the original 15 eval cases.

Labels encode intended synthetic text-reuse scenarios, not verified real fraud.
Identity, vocabulary and random seeds are separated before fitting any weights.
"""
import random

from src.profile_ml import ProfileFacts

VOCABULARY = {
    'train': (['Maren', 'Tobias', 'Elise', 'Soren', 'Freya', 'Jonas'],
              ['Lisbon', 'Oslo', 'Tallinn', 'Bergen'], ['ceramics', 'weddings', 'woodwork', 'textiles']),
    'validation': (['Nadia', 'Karim', 'Olwen', 'Bruno'],
                   ['Lima', 'Rabat', 'Turin'], ['bicycles', 'calligraphy', 'gardens']),
    'holdout': (['Erlan', 'Mira', 'Жанна', 'Айдар'],
                ['Алматы', 'Тбилиси', 'Bristol'], ['портреты', 'иллюстрации', 'leatherwork']),
}


def dataset(split, groups):
    names, cities, topics = VOCABULARY[split]
    rng = random.Random({'train': 914, 'validation': 2718, 'holdout': 6083}[split])
    pairs = []
    for identity in range(groups):
        name, city, topic = rng.choice(names), rng.choice(cities), rng.choice(topics)
        handle = f'{split[:2]}_{identity}_craft'
        contact = f'hello@{split}-atelier-{identity}.example'
        description = f'{topic.title()} commissions in {city}. Custom designs by {name}. Contact {contact}'
        original = ProfileFacts(handle=handle, display_name=f'{name} Atelier', bio=description,
                                has_profile_picture=bool(rng.getrandbits(1)), has_external_url=True,
                                is_private=False, num_posts=rng.randint(10, 500),
                                num_followers=rng.randint(100, 30000), num_following=rng.randint(10, 1000))
        other_bio = f'Weekend running and local recipes. Family journal {rng.randint(10, 99)}'
        # Identity families are never shared between split files.
        variants = [
            ('exact', 1, f'{handle}_new', original.display_name, description),
            ('added_text', 1, f'{handle}.help', original.display_name, description + '\nMessage this new account for orders'),
            ('renamed', 1, f'{handle}_official', original.display_name + ' Official', description),
            ('edited_bio', 1, f'{handle}_shop', original.display_name, f'{topic.title()} commissions in {city}. Custom designs. Contact {contact}'),
            ('different_handle', 1, f'gallery_{identity}_x', original.display_name, description),
            ('unrelated', 0, f'runner_{identity}', 'Weekend Journal', other_bio),
            ('common_name', 0, f'recipes_{identity}', original.display_name, other_bio),
            ('no_avatar', 0, f'local_{identity}', 'Local Kitchen', other_bio),
            ('fan', 0, f'{handle}_fans', original.display_name, 'Unofficial fan page. Not the original creator. ' + description),
            ('parody', 0, f'{handle}_fun', original.display_name, 'PARODY account, not the real author. ' + description),
            ('nick_only', 0, f'{handle}_help', 'Unrelated Journal', other_bio),
            ('contact_only', 0, f'contacts_{identity}', 'Community Directory', f'Public directory of makers: {contact}'),
            ('generic', 0, f'{handle}_life', original.display_name, 'Photography travel life'),
        ]
        for kind, label, candidate_handle, candidate_name, bio in variants:
            owner = original
            if kind == 'generic':
                owner = owner.model_copy(update={'bio': 'Photography travel life'})
            candidate = owner.model_copy(update={'handle': candidate_handle[:30], 'display_name': candidate_name,
                'bio': bio, 'has_profile_picture': False if kind == 'no_avatar' else bool(rng.getrandbits(1)),
                'num_posts': rng.randint(0, 500), 'num_followers': rng.randint(0, 30000)})
            pairs.append({'group': f'{split}-{identity}', 'kind': kind, 'label': label,
                          'original': owner.model_dump(), 'suspect': candidate.model_dump()})
    return pairs
