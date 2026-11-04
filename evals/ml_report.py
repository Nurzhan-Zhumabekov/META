"""Render the frozen ML version comparison, with targets kept separate."""
import argparse
import html
import json
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def render(comparison, profile_before, profile_after, training):
    rows = []
    names = {'copied_bio_avatar': 'Копия имени, bio и аватара', 'copied_bio_content': 'Скопированы bio и публикации',
             'money_request': 'Копия с просьбой перевести деньги', 'unrelated_names': 'Несвязанные профили',
             'common_name': 'Совпадает обычное имя', 'fan_disclosure': 'Фан-страница', 'parody_disclosure': 'Пародия',
             'blank_both': 'Два пустых скриншота', 'blank_original': 'Пустой оригинал', 'blank_suspect': 'Пустой проверяемый профиль',
             'blurred_evidence': 'Размытые изображения', 'prompt_injection_bio': 'Инструкция внутри bio',
             'different_avatar_same_bio': 'Скопировано bio, другой аватар', 'default_avatars': 'Стандартные аватары, разный контент',
             'same_avatar_only': 'Совпадает только аватар'}
    for index, row in enumerate(comparison['results'], 1):
        pair = row['pair_ml']
        signal = pair['risk_score']
        flag = signal is not None and signal >= pair['threshold']
        note = 'Нужна проверка копирования' if flag else 'Низкий сигнал копирования' if signal is not None else 'Недостаточно данных'
        if row['meta_image_evidence_insufficient']:
            note = 'Только явно введённый текст. Meta: недостаточно доказательств по изображениям.'
        pair_text = f'{signal:.1%}' if signal is not None else '—'
        rows.append(f'''<tbody class="case"><tr><td>{index:02}</td><td><strong>{esc(names.get(row['id'], row['id']))}</strong><small>{esc(row['id'])}</small></td>
<td>{row['v1_profile_risk']:.2%}</td><td>{row['v2_profile_ml']['risk_score']:.2%}</td><td><b class="{'high' if flag else 'low'}">{pair_text}</b></td><td>{esc(note)}</td></tr>
<tr><td colspan="6"><details><summary>Данные двух профилей, факторы и ограничения</summary><pre>{esc(json.dumps(row, ensure_ascii=False, indent=2))}</pre></details></td></tr></tbody>''')
    holdout = training['splits']['holdout']
    before = profile_before['clean_test']
    after = profile_after['same_v1_holdout']
    default = next(r for r in comparison['results'] if r['id'] == 'default_avatars')
    copy_ids = {'copied_bio_avatar', 'copied_bio_content', 'money_request', 'prompt_injection_bio', 'different_avatar_same_bio'}
    copy_scores = [r['pair_ml']['risk_score'] for r in comparison['results'] if r['id'] in copy_ids]
    cards = (f'<div class="cards"><div class="card"><span>Обычный профиль без аватара · спам-паттерны</span>'
             f'<b>{default["v1_profile_risk"]:.1%} → {default["v2_profile_ml"]["risk_score"]:.1%}</b>'
             f'<small>Парная модель: {default["pair_ml"]["risk_score"]:.1%} сигнала копирования</small></div>'
             f'<div class="card"><span>{len(copy_scores)} копий из предыдущего набора</span><b>{min(copy_scores):.1%}–{max(copy_scores):.1%}</b>'
             '<small>Сигнал копирования новой парной модели</small></div>'
             f'<div class="card"><span>Переключение наличия аватара</span><b>Влияние: 0</b><small>Подтверждено на {comparison["avatar_invariant_cases"]} входных профилях</small></div></div>')
    return '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ML v2 · Поиск копий профилей</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f7f8;color:#15281f;font:14px/1.6 Arial,sans-serif}body:before{content:"";display:block;height:5px;background:linear-gradient(90deg,#ffcf65,#e35194,#7851cf)}main{max-width:1420px;margin:auto;padding:36px}.eyebrow{letter-spacing:.15em;text-transform:uppercase;color:#728179;font-size:11px}h1{font-size:37px;line-height:1.15;margin:16px 0;letter-spacing:-1px}header p{color:#63766b;max-width:950px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:26px 0}.card{border:1px solid #dfe7e2;border-radius:12px;background:white;padding:20px}.card span,.card small{display:block;color:#75857c;font-size:12px}.card b{display:block;font-size:28px;letter-spacing:-.5px;margin:8px 0}.notice{padding:16px 20px;border:1px solid #d8e5dd;border-radius:12px;background:#edf4ef;margin:20px 0;color:#476151}.notice.warn{background:#fff7e9;border-color:#eddfc4;color:#766039}.table{overflow:auto;border:1px solid #dfe7e2;border-radius:12px;background:white}table{width:100%;border-collapse:collapse;text-align:left;font-size:12px;min-width:980px}th{padding:16px 14px;background:#f9fbfa;color:#75857c;font-size:11px}td{padding:15px 14px;vertical-align:top}td small{display:block;color:#829087;margin-top:5px}tbody tr:last-child td{padding-top:0;border-bottom:1px solid #eaf0ec}summary{cursor:pointer;color:#6b8073;font-size:11px}.high{color:#7a5311;background:#fff3d8;padding:5px 9px;border-radius:6px}.low{color:#1b7048;background:#e8f6ed;padding:5px 9px;border-radius:6px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f7f4;border-radius:8px;padding:18px;max-height:500px;overflow:auto;font:11px/1.65 Consolas,monospace}input[type=search]{font:inherit;padding:10px 14px;margin:0 0 18px;border:1px solid #d4e0d8;border-radius:8px;background:white;min-width:300px}.methods{margin:24px 0;padding:22px;background:white;border:1px solid #dfe7e2;border-radius:12px}.methods h2{font-size:17px;margin-top:0}.methods p{color:#63766b}a{color:#21744e}@media(max-width:700px){main{padding:24px 16px}h1{font-size:29px}.cards{grid-template-columns:1fr}.card b{font-size:25px}}
</style></head><body><main><header><div class="eyebrow">Instagram feature concept · ML improvement</div><h1>Копирование — по двум профилям.<br>Аватар не влияет на риск.</h1><p>Новая парная ML-модель сравнивает имя, bio и ник. Историческая модель паттернов спама переобучена без признака наличия фото профиля. Показатели решают разные задачи и показаны отдельно.</p></header>
''' + cards + '''
<div class="notice"><b>Обучение парной модели — синтетическое.</b> Это проверка поведения прототипа, а не доказанная точность на реальных аккаунтах. Оценка копирования не является вероятностью мошенничества. Каждая жалоба остаётся <code>under_review</code> до решения человека.</div>
<input id="search" type="search" placeholder="Найти сценарий…" aria-label="Поиск сценария"><div class="table"><table><thead><tr><th>#</th><th>Сценарий</th><th>Спам-паттерны v1</th><th>Спам-паттерны v2</th><th>Копирование · новая ML</th><th>Интерпретация</th></tr></thead>''' + ''.join(rows) + f'''</table></div>
<div class="notice warn"><b>Пустые и размытые изображения:</b> парная модель читает отдельно введённые имя и bio, а не текст со скриншота. Поэтому она может найти сходство в этих явно заданных текстах даже при пустом изображении. Это не отменяет рекомендацию Meta «недостаточно доказательств».</div>
<section class="methods"><h2>Что измерено</h2><p>Парная модель: {training['splits']['train']['n']:,} учебных пар, {training['splits']['validation']['n']} валидационных и {holdout['n']} отложенных синтетических пар. Семейства аккаунтов между выборками не пересекаются. На отложенной части: обнаружены {holdout['positives'] - holdout['false_negatives']} из {holdout['positives']} заданных копий, ложных срабатываний {holdout['false_positives']} из {holdout['n'] - holdout['positives']} отрицательных случаев при пороге {holdout['operating_threshold']:.0%}.</p>
<p>Выборки созданы общим генератором. Для {holdout['feature_vectors_also_in_train']} отложенных пар в обучении встречаются одинаковые векторы признаков, хотя сами аккаунты разные. Это ограничивает силу результата. Исходные 15 сценариев в обучение не включались.</p>
<p>Компромисс на старом fake/spam-наборе ({after['n']} профилей): accuracy {before['accuracy']:.2%} → {after['accuracy']:.2%}; ложные срабатывания {before['confusion_matrix_tn_fp_fn_tp'][0][1]} → {after['confusion_matrix_tn_fp_fn_tp'][0][1]}, пропуски {before['confusion_matrix_tn_fp_fn_tp'][1][0]} → {after['confusion_matrix_tn_fp_fn_tp'][1][0]}. Общая точность старой задачи не улучшилась. Устранена зависимость от аватара; копирование оценивается отдельной моделью.</p>
<p>Таблица использует замороженные входные данные предыдущего прогона. Ответы Meta повторно использованы для проверки интеграции; новых вызовов Meta при сравнении ML не было. Рабочая база жалоб сохранена.</p>
<p>Методика разделения и проверки экспорта: <a href="https://scikit-learn.org/stable/modules/cross_validation.html">scikit-learn: cross-validation</a>. Артефакты: <code>outputs/ml/v2/</code> и <code>outputs/evals/ml-v2-20261103/</code>.</p></section>
</main><script>document.getElementById('search').addEventListener('input',event=>{{const q=event.target.value.toLowerCase();document.querySelectorAll('tbody.case').forEach(row=>row.hidden=!row.textContent.toLowerCase().includes(q))}});</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = args.root
    read = lambda path: json.loads((root / path).read_text(encoding='utf-8'))
    report = render(read('outputs/evals/ml-v2-20261103/results.json'), read('outputs/ml/v1/training-report.json'),
                    read('outputs/ml/v2/training-report.json'), read('outputs/ml/v2/pair-training-report.json'))
    output = args.output or root / 'web/public/ml-improvement-report.html'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding='utf-8')
    print(str(output.resolve()))


if __name__ == '__main__':
    main()
