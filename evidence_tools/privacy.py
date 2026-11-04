"""Actual Presidio contact/financial-PII analysis; no raw values in summaries."""
from functools import lru_cache


@lru_cache(maxsize=1)
def engine():
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_analyzer.predefined_recognizers import PhoneRecognizer
    provider = NlpEngineProvider(nlp_configuration={'nlp_engine_name': 'spacy',
        'models': [{'lang_code': 'en', 'model_name': 'en_core_web_sm'}]})
    analyzer = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=['en'])
    analyzer.registry.add_recognizer(PhoneRecognizer(supported_regions=['US', 'KZ', 'RU']))
    return analyzer


def analyze(text):
    from presidio_anonymizer import AnonymizerEngine
    entities = ['EMAIL_ADDRESS', 'PHONE_NUMBER', 'CREDIT_CARD', 'IBAN_CODE', 'IP_ADDRESS']
    # Presidio PhoneRecognizer emits 0.4 for a libphonenumber-validated match
    # without an English context keyword. Keep its documented operating score,
    # rather than dropping valid numbers in Russian/mixed-language screenshots.
    raw = engine().analyze(text=text, language='en', entities=entities, score_threshold=0)
    results = [r for r in raw if r.score >= (0.4 if r.entity_type == 'PHONE_NUMBER' else 0.5)]
    # The analyzer can return overlapping recognizers of the same entity.
    unique = {(r.entity_type, r.start, r.end): r for r in results}
    findings = list(unique.values())
    return {'provider': 'presidio', 'scope': 'contacts_and_financial_identifiers',
            'findings': [{'entity_type': r.entity_type, 'start': r.start, 'end': r.end, 'confidence': float(r.score)} for r in findings],
            'masked_text': AnonymizerEngine().anonymize(text=text, analyzer_results=findings).text,
            'limitations': ['Checks cover contact and financial identifiers, not every kind of personal data.',
                            'Results depend on OCR quality. No warnings does not guarantee that no personal data remains.']}
