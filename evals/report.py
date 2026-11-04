"""Standalone, escaped HTML report containing only synthetic evaluation inputs."""
import argparse
import base64
import html
import json
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def pretty(value):
    return esc(json.dumps(value, ensure_ascii=False, indent=2))


def render_report(runs):
    panels, buttons = [], []
    for index, (label, run, directory) in enumerate(runs):
        total = run['total']
        cards = ''.join(f'<div class="metric"><span>{esc(title)}</span><strong>{run.get(key, 0)} / {total}</strong></div>'
                        for title, key in [('Все проверки', 'passed'), ('Meta: ожидаемый ответ', 'meta_passed'),
                                           ('ML: корректный результат', 'ml_contract_passed'), ('Ожидание модератора', 'human_review_passed')])
        rows = []
        for number, row in enumerate(run['results'], 1):
            analysis, ml = row.get('analysis', {}), row.get('profile_ml', {})
            risk, similarity = ml.get('risk_score'), analysis.get('similarity_score')
            risk_text = f'{risk:.1%}' if risk is not None else '—'
            similarity_text = f'{similarity:.1%}' if similarity is not None else '—'
            passed = row['passed']
            inputs = []
            for kind, title in [('original', 'Заявленный оригинал'), ('suspect', 'Проверяемый профиль')]:
                path = Path(directory) / 'cases' / row['id'] / f'{kind}.png'
                if path.is_file():
                    data = base64.b64encode(path.read_bytes()).decode('ascii')
                    inputs.append(f'<figure><img loading="lazy" src="data:image/png;base64,{data}" alt="{title}"><figcaption>{title}</figcaption></figure>')
            summary = analysis.get('summary', row.get('error', 'Нет ответа Meta'))
            evidence = ''.join(f'<li>{esc(x)}</li>' for x in analysis.get('evidence', []))
            differences = ''.join(f'<li>{esc(x)}</li>' for x in analysis.get('differences', []))
            limitations = ''.join(f'<li>{esc(x)}</li>' for x in analysis.get('limitations', []))
            rows.append(f'''<tbody class="case" data-pass="{str(passed).lower()}">
<tr><td class="number">{number:02}</td><td><strong>{esc(row['id'])}</strong><small>{esc(row['description'])}</small></td>
<td><code>{esc(analysis.get('recommendation', row.get('error', '—')))}</code><small>Сходство контента: {similarity_text}</small></td>
<td class="risk">{risk_text}<small>{esc(ml.get('risk_band', ''))}</small></td>
<td><code>{esc(row.get('status', '—'))}</code></td><td>{row['latency_seconds']:.2f} c</td>
<td><span class="badge {'ok' if passed else 'fail'}">{'Пройден' if passed else 'Ошибка'}</span></td></tr>
<tr class="detail-row"><td colspan="7"><details><summary>Ответ Meta, ожидания, ML и тестовые изображения</summary>
<div class="detail"><div><p class="answer">{esc(summary)}</p><p><b>Ожидалось:</b> {esc(', '.join(row['expected']))}</p>
<h3>Наблюдения Meta</h3><ul>{evidence}</ul><h3>Различия</h3><ul>{differences}</ul><h3>Ограничения</h3><ul>{limitations}</ul>
<details><summary>Полный результат JSON и явные данные ML</summary><pre>{pretty(row)}</pre></details></div>
<div class="inputs">{''.join(inputs)}</div></div></details></td></tr></tbody>''')
        tokens = run.get('tokens', {})
        default = next((r for r in run['results'] if r['id'] == 'default_avatars'), None)
        default_risk = default.get('profile_ml', {}).get('risk_score') if default else None
        risk_note = ''
        if default_risk is not None:
            default_recommendation = default.get('analysis', {}).get('recommendation', '—')
            risk_note = (f'<br><b>Наблюдаемое ограничение:</b> стандартный аватар получил {default_risk:.1%} риска ML '
                         f'при рекомендации Meta <code>{esc(default_recommendation)}</code>. '
                         '«Пройден» для ML означает корректное выполнение, а не правильную классификацию имперсонации. '
                         'Веса модели на этих примерах не подбирались.')
        buttons.append(f'<button type="button" data-tab="run-{index}" aria-pressed="{str(index == 0).lower()}">{esc(label)}</button>')
        panels.append(f'''<section id="run-{index}" class="run" {'hidden' if index else ''}>
<div class="metrics">{cards}</div><p class="meta">{esc(run.get('model', ''))} · {esc(run.get('prompt_version', ''))} · {esc(run.get('created_at', ''))}</p>
<div class="stats"><span>Среднее время <b>{esc(run.get('latency_mean_seconds', '—'))} c</b></span>
<span>Токены <b>{tokens.get('prompt_tokens', 0):,} вход / {tokens.get('completion_tokens', 0):,} выход</b></span>
<span>Оценка стоимости успешных ответов <b>${run.get('estimated_successful_response_cost_usd', 0):.4f}</b></span></div>
<div class="notice"><b>Исправлено перед прогоном:</b> в сценариях «только аватар» и «стандартные аватары» генератор ошибочно копировал всю сетку публикаций. Ожидаемые рекомендации сохранены.
{risk_note}</div>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Сценарий</th><th>Meta AI</th><th>ML риск</th><th>Статус жалобы</th><th>Время</th><th>Итог</th></tr></thead>{''.join(rows)}</table></div>
<details class="provenance"><summary>Воспроизводимость и контроль изменений</summary><pre>{pretty({k: v for k, v in run.items() if k != 'results'})}</pre></details></section>''')
    return '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meta AI + ML · Проверка 15 сценариев</title><style>
:root{font-family:Inter,Arial,sans-serif;color:#17211d;background:#f6f7f8;font-synthesis:none}*{box-sizing:border-box}body{margin:0}button,input{font:inherit}button{cursor:pointer}
.stripe{height:5px;background:linear-gradient(90deg,#ffc857,#ed5488,#9054dd)}main{max-width:1550px;margin:auto;padding:48px 40px}.eyebrow{letter-spacing:.13em;font-size:12px;font-weight:700;color:#68756e;text-transform:uppercase}h1{font-size:40px;letter-spacing:-1.5px;margin:14px 0}header>p{max-width:900px;color:#5c6962;line-height:1.65}.notice{background:#eef3f0;border:1px solid #d5e3da;border-radius:14px;padding:18px 22px;line-height:1.6;margin:26px 0}.notice b{color:#136947}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin:28px 0}.tabs{display:flex;gap:7px}.tabs button{padding:10px 16px;border:1px solid #dce3df;border-radius:9px;background:white;color:#54625a}.tabs button[aria-pressed=true]{background:#172d23;color:white;border-color:#172d23}.toolbar input[type=search]{padding:11px 14px;border:1px solid #dce3df;border-radius:9px;min-width:260px;background:white}.toolbar label{display:flex;gap:8px;font-size:14px;color:#54625a}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.metric{background:white;border:1px solid #e1e7e3;padding:23px;border-radius:14px;display:flex;flex-direction:column;gap:14px}.metric span{font-size:13px;color:#68756e}.metric strong{font-size:31px;letter-spacing:-1px}.meta{font-size:13px;color:#79847e;margin:20px 0}.stats{display:flex;gap:28px;flex-wrap:wrap;font-size:13px;color:#68756e;margin:18px 0 28px}.stats b{color:#263a30;margin-left:5px}.table-wrap{background:white;border:1px solid #e1e7e3;border-radius:15px;overflow:auto}table{border-collapse:collapse;width:100%;text-align:left;font-size:13px}th{font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:#7a877f;background:#fafcfb;padding:17px 15px;white-space:nowrap}td{padding:18px 15px;vertical-align:top}td small{display:block;color:#7a877f;font-size:12px;margin-top:8px;max-width:280px;line-height:1.5}code{font-size:12px;font-family:ui-monospace,Consolas,monospace}.number{color:#98a29c}.risk{font-size:19px;white-space:nowrap;font-weight:600}.badge{display:inline-block;padding:6px 9px;font-size:11px;font-weight:700;border-radius:6px;white-space:nowrap}.ok{color:#187548;background:#e9f5ee}.fail{color:#a73535;background:#ffeded}.detail-row td{padding-top:0;border-bottom:1px solid #edf0ee}summary{cursor:pointer;color:#5e7066;font-size:12px;line-height:1.6}details[open]>summary{color:#15704b}.detail{padding:22px 0;display:grid;grid-template-columns:1fr 1fr;gap:32px}.answer{font-size:15px;line-height:1.7}h3{font-size:12px;margin-top:22px}li{line-height:1.7;margin:5px 0}ul{padding-left:20px;color:#4b6054}.inputs{display:flex;gap:12px;align-items:flex-start}figure{margin:0;min-width:0;flex:1}figure img{width:100%;max-width:250px;border:1px solid #e1e7e3;border-radius:8px}figcaption{font-size:11px;color:#7a877f;margin-top:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:11px/1.7 ui-monospace,Consolas,monospace;background:#f4f7f5;border-radius:9px;padding:16px;max-height:550px;overflow:auto}.provenance{margin:24px 0}footer{font-size:12px;color:#7a877f;line-height:1.8;margin-top:30px}a{color:#136947}[hidden]{display:none!important}@media(max-width:850px){main{padding:28px 16px}h1{font-size:30px}.metrics{grid-template-columns:repeat(2,1fr)}.detail{grid-template-columns:1fr}.stats{gap:12px}.toolbar input[type=search]{min-width:200px}table{min-width:1000px}}
</style></head><body><div class="stripe"></div><main><header><div class="eyebrow">Instagram feature concept · Evaluation lab</div>
<h1>15 сценариев. Meta AI + ML.</h1><p>Реальные ответы Muse Spark и независимая локальная модель. Каждый случай прошёл через тот же серверный процесс подачи жалобы, который использует приложение.</p></header>
<div class="notice"><b>Это синтетические тесты, не точность на реальных аккаунтах.</b> Проверяем ожидаемую рекомендацию Meta, корректность результата ML и сохранение статуса <code>under_review</code>. ML оценивает признаки fake/spam по явным данным профиля, а не вероятность имперсонации. Подтверждение остаётся за человеком. Рабочая база жалоб не изменялась.</div>
<div class="toolbar"><div class="tabs">''' + ''.join(buttons) + '''</div><input id="search" type="search" aria-label="Поиск сценария" placeholder="Найти сценарий или ответ…"><label><input id="fail-only" type="checkbox">Только ошибки</label></div>''' + ''.join(panels) + '''
<footer>Проверены также пустые и размытые изображения, фан-страницы, пародия и инструкции внутри bio. Раскройте строку для полного ответа и входных данных.<br>Стоимость — оценка по успешным ответам без скидки за кэш; не включает неизвестный расход неудачных попыток. <a href="https://dev.meta.ai/docs/pricing-rate-limits" target="_blank" rel="noreferrer">Официальные тарифы Meta</a>. Все изображения вымышленные, отчёт не содержит ключей API.</footer></main>
<script>const search=document.getElementById('search'),fail=document.getElementById('fail-only');function filter(){const query=search.value.toLowerCase();document.querySelectorAll('tbody.case').forEach(row=>{row.hidden=(!row.textContent.toLowerCase().includes(query))||(fail.checked&&row.dataset.pass==='true')})}search.addEventListener('input',filter);fail.addEventListener('change',filter);document.querySelectorAll('[data-tab]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.run').forEach(panel=>panel.hidden=panel.id!==button.dataset.tab);document.querySelectorAll('[data-tab]').forEach(tab=>tab.setAttribute('aria-pressed',String(tab===button)));filter()}));</script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    runs = [(path.parent.name, json.loads(path.read_text(encoding='utf-8')), path.parent) for path in args.runs]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(runs), encoding='utf-8')
    print(str(args.output.resolve()))


if __name__ == '__main__':
    main()
