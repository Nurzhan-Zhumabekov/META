"""Render an edited 180-second English demo from authentic browser captures.

No browser state is fabricated. Screen crops are editorial framing of the actual
fictional run. Requires Pillow and ffmpeg/ffprobe; narration files are generated
separately and retained with their timing subtitles.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import textwrap
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'outputs/demo-video-20261104'
CAPTURES = WORK / 'captures'
FRAMES = WORK / 'frames'
AUDIO = WORK / 'audio'
OUTPUT = WORK / 'MirrorCheck_Demo_EN_3min.mp4'
SIZE = (1920, 1080)
PURPLE = '#5051ff'
INK = '#161823'
MUTED = '#687080'
BG = '#f7f7fa'
FONT_ROOT = Path('C:/Windows/Fonts')

STAGES = [
    ('The problem', 'A copied profile can look convincing.', 'Collect the evidence. Make it reviewable.', 'Unofficial feature concept'),
    ('Original and copy', 'Same content. Different username.', 'Two fictional accounts. Shared name, biography, avatar and post images.', 'aigerim.k → aigerim.k.demo'),
    ('Submit a report', 'Start from the profile.', 'Attach both screenshots. Review the extracted data before submitting.', 'PaddleOCR · Editable fields'),
    ('Redact locally', 'Hide contacts before Meta AI.', 'Opaque masks cover the detected email and phone lines in the actual provider images.', '2 contact regions masked'),
    ('Meta visual evidence', 'A real model response.', 'Meta Muse Spark reports reuse, differences and limitations. Ownership remains unproven.', 'muse-spark-1.3 · needs_review'),
    ('Independent ML', 'Separate signals. Visible limits.', 'Text reuse, image similarity and spam patterns answer different questions.', 'Signals, not identity probabilities'),
    ('Await a decision', 'The report stays under review.', 'The profile model excludes avatar presence. Pair ML uses synthetic training data.', 'No automatic confirmation'),
    ('Moderator review', 'A deliberate decision.', 'The reviewer inspects processed evidence and explicitly confirms this fictional case.', 'Case 1b96686f · Operator demonstration'),
    ('Profile warning', 'The warning persists.', 'The server saves the moderator decision. Reloading retains the profile label.', 'Impersonation confirmed'),
    ('Next steps', 'Review suspected copies with evidence.', 'Next: consented evaluation, ownership evidence and production hardening.', 'A working local prototype'),
]

# Each tuple is (start, end, stage index, frame mode, source capture, crop).
SHOTS = [
    (0, 6, 0, 'intro', None, None),
    (6, 12, 0, 'compare', None, None),
    (12, 20, 1, 'single', '01-original.png', (128, 12, 865, 780)),
    (20, 28, 1, 'single', '02-copy-before.png', (128, 12, 865, 780)),
    (28, 34, 2, 'single', '03-report-reason.png', (0, 220, 1016, 651)),
    (34, 40, 2, 'single', '04-upload-form.png', (205, 70, 815, 680)),
    (40, 45, 2, 'single', '05-ocr-processing.png', (205, 180, 815, 780)),
    (45, 48, 2, 'single', '08-reviewed-fields.png', (224, 24, 786, 460)),
    (48, 50, 2, 'single', '08-reviewed-fields.png', (224, 420, 786, 832)),
    (50, 59, 3, 'single', '07-redaction-details.png', (234, 24, 766, 412)),
    (59, 72, 3, 'redacted', None, None),
    (72, 77, 4, 'single', '09-meta-processing.png', (205, 180, 815, 650)),
    (77, 82, 4, 'single', '10-report-received.png', (205, 0, 815, 500)),
    (82, 96, 4, 'single', '14-moderator-analysis.png', (120, 130, 938, 600)),
    (96, 106, 5, 'single', '14-moderator-analysis.png', (120, 232, 938, 600)),
    (106, 116, 5, 'single', '07-redaction-details.png', (234, 24, 766, 412)),
    (116, 124, 6, 'single', '12-profile-under-review.png', (142, 25, 864, 445)),
    (124, 134, 6, 'single', '14-moderator-analysis.png', (120, 230, 938, 510)),
    (134, 140, 7, 'single', '13-moderator-evidence.png', (102, 184, 957, 715)),
    (140, 148, 7, 'single', '15-confirm-action.png', (103, 170, 957, 464)),
    (148, 152, 7, 'single', '16-decision-saved.png', (102, 42, 957, 254)),
    (152, 160, 8, 'single', '18-label-after-reload.png', (140, 20, 865, 362)),
    (160, 170, 8, 'single', '18-label-after-reload.png', (315, 34, 772, 301)),
    (170, 180, 9, 'end', None, None),
]


def run(args):
    subprocess.run([str(x) for x in args], check=True)


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_ROOT / ('segoeuib.ttf' if bold else 'segoeui.ttf')), size)


def wrapped(draw, xy, text, typeface, width, fill=INK, gap=10):
    x, y = xy
    current = ''
    lines = []
    for word in text.split():
        candidate = (current + ' ' + word).strip()
        if current and draw.textlength(candidate, font=typeface) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    for line in lines:
        draw.text((x, y), line, font=typeface, fill=fill)
        y += typeface.size + gap
    return y


def paste_crop(canvas, name, crop, box):
    path = CAPTURES / name
    with Image.open(path) as raw:
        shot = raw.convert('RGB')
        if crop:
            assert 0 <= crop[0] < crop[2] <= shot.width and 0 <= crop[1] < crop[3] <= shot.height, (name, crop, shot.size)
            shot = shot.crop(crop)
        fitted = ImageOps.contain(shot, (box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
        x = box[0] + (box[2] - box[0] - fitted.width) // 2
        y = box[1] + (box[3] - box[1] - fitted.height) // 2
        canvas.paste(fitted, (x, y))


def shell(stage, start):
    image = Image.new('RGB', SIZE, BG)
    d = ImageDraw.Draw(image)
    d.text((54, 25), 'MirrorCheck', font=font(37, True), fill=INK)
    d.text((56, 73), 'AI-ASSISTED IMPERSONATION REVIEW', font=font(17, True), fill=MUTED)
    label = 'Fictional accounts  ·  Real Meta API  ·  Edited for time'
    d.text((1858 - d.textlength(label, font=font(22)), 35), label, font=font(22), fill=MUTED)
    d.line((54, 115, 1866, 115), fill='#dedee7', width=2)
    d.rounded_rectangle((44, 950, 1876, 1064), radius=22, fill='#161923')
    d.rectangle((56, 932, 1864, 935), fill='#dedee7')
    d.rectangle((56, 932, 56 + round(1808 * start / 180), 935), fill=PURPLE)
    d.text((56, 144), f'{stage + 1:02d} / 10', font=font(21, True), fill=PURPLE)
    return image, d


def draw_single(start, end, stage, name, crop):
    image, d = shell(stage, start)
    label, headline, body, fact = STAGES[stage]
    d.text((56, 188), label.upper(), font=font(19, True), fill=MUTED)
    y = wrapped(d, (52, 238), headline, font(50, True), 440, gap=8)
    wrapped(d, (56, y + 26), body, font(25), 422, fill=MUTED, gap=11)
    d.rounded_rectangle((56, 754, 478, 888), radius=18, fill='#ececfc')
    wrapped(d, (76, 775), fact, font(23, True), 380, fill='#3636a9', gap=8)
    d.text((76, 853), 'EDITORIAL CONTEXT', font=font(14, True), fill='#7777a3')
    d.rounded_rectangle((526, 142, 1870, 910), radius=24, fill='white', outline='#e0e0e9', width=2)
    paste_crop(image, name, crop, (548, 158, 1848, 892))
    return image


def draw_compare(start, intro=False):
    image, d = shell(0 if intro else 1, start)
    d.text((54, 184), 'A convincing copy. A reviewable trail.', font=font(50, True), fill=INK)
    for x, label, filename in [(58, 'ORIGINAL PROFILE', '01-original.png'), (982, 'SUSPECTED COPY', '02-copy-before.png')]:
        d.text((x + 18, 272), label, font=font(21, True), fill=PURPLE if x == 58 else MUTED)
        d.rounded_rectangle((x, 318, x + 878, 910), radius=22, fill='white', outline='#e0e0e9', width=2)
        paste_crop(image, filename, (135, 20, 865, 580), (x + 14, 326, x + 864, 900))
    return image


def draw_intro():
    image, d = shell(0, 0)
    d.text((54, 178), 'MirrorCheck', font=font(86, True), fill=INK)
    wrapped(d, (58, 310), 'Turn suspected profile copies into evidence a reviewer can inspect.', font(49, True), 895, gap=12)
    wrapped(d, (60, 535), 'Meta Muse Spark + Local ML + Contact redaction + Moderator review', font(29), 800, fill=MUTED, gap=18)
    d.rounded_rectangle((1070, 173, 1868, 885), radius=25, fill='white', outline='#e0e0e9', width=2)
    paste_crop(image, '02-copy-before.png', (145, 20, 860, 660), (1090, 190, 1850, 866))
    d.text((61, 803), 'UNOFFICIAL INSTAGRAM-STYLE WEB PROTOTYPE', font=font(20, True), fill=PURPLE)
    d.text((61, 844), 'A new fictional report, recorded in the working app.', font=font(24), fill=MUTED)
    return image


def draw_redacted():
    image, d = shell(3, 59)
    d.text((56, 184), 'What Meta receives', font=font(52, True), fill=INK)
    d.text((58, 255), 'Processed JPEGs · detected contacts masked locally · identical stored reviewer evidence', font=font(26), fill=MUTED)
    for x, label, side in [(58, 'ORIGINAL', 'original'), (982, 'REPORTED PROFILE', 'suspect')]:
        d.text((x + 18, 320), label, font=font(21, True), fill=PURPLE)
        d.rounded_rectangle((x, 368, x + 878, 904), radius=20, fill='white', outline='#dedee7', width=2)
        with Image.open(WORK / f'preview-{side}.jpg') as raw:
            shot = raw.convert('RGB').crop((140, 20, 865, 450))
            fitted = ImageOps.contain(shot, (850, 508), Image.Resampling.LANCZOS)
            image.paste(fitted, (x + (878 - fitted.width) // 2, 380 + (508 - fitted.height) // 2))
    return image


def draw_end():
    image, d = shell(9, 170)
    d.text((54, 184), 'MirrorCheck', font=font(76, True), fill=INK)
    wrapped(d, (58, 307), 'Evidence for review.\nA moderator in control.', font(48, True), 880, gap=12)
    wrapped(d, (61, 505), 'Next: consented real-world evaluation, verified ownership evidence and production hardening.', font(28), 840, fill=MUTED, gap=13)
    d.text((61, 750), 'github.com/Nurzhan-Zhumabekov/META', font=font(28, True), fill=PURPLE)
    d.text((61, 807), 'English narration synthesized with Microsoft Andrew.', font=font(20), fill=MUTED)
    d.text((61, 843), 'Real UI captures · Fictional case 1b96686f', font=font(22), fill=MUTED)
    d.rounded_rectangle((1035, 218, 1868, 835), radius=24, fill='white', outline='#e0e0e9', width=2)
    paste_crop(image, '18-label-after-reload.png', (315, 34, 772, 301), (1059, 242, 1843, 811))
    return image


def seconds(value):
    h, m, s = value.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def stamp(value, ass=False):
    if ass:
        ticks = round(value * 100)
        return f'{ticks // 360000:01d}:{ticks // 6000 % 60:02d}:{ticks // 100 % 60:02d}.{ticks % 100:02d}'
    ticks = round(value * 1000)
    return f'{ticks // 3600000:02d}:{ticks // 60000 % 60:02d}:{ticks // 1000 % 60:02d},{ticks % 1000:03d}'


def subtitle_parts(text, count):
    tokens = text.split()
    return [' '.join(tokens[round(len(tokens) * i / count):round(len(tokens) * (i + 1) / count)]) for i in range(count)]


def assemble_audio(scenes):
    all_cues, segments, timings = [], [], []
    for i, scene in enumerate(scenes, 1):
        source = AUDIO / f'{i:02d}.mp3'
        duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(source)], text=True))
        slot = scene['end'] - scene['start']
        speed = max(1, duration / (slot - .6))
        assert speed <= 1.18, (i, duration, slot)
        target = AUDIO / f'{i:02d}-timed.wav'
        # Count samples rather than trimming against decoder timestamps: MP3
        # timestamp offsets otherwise shorten every slot despite added silence.
        samples = slot * 48000
        filters = (f'atempo={speed:.8f},aresample=48000,asetpts=PTS-STARTPTS,'
                   f'adelay=delays=300:all=1,apad=whole_len={samples},'
                   f'atrim=end_sample={samples},asetpts=N/SR/TB')
        run(['ffmpeg', '-y', '-v', 'error', '-i', source, '-af', filters, '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', target])
        with wave.open(str(target), 'rb') as pcm:
            assert pcm.getnframes() == samples and pcm.getframerate() == 48000
        segments.append(target)
        raw_srt = source.with_suffix('.srt').read_text(encoding='utf-8-sig')
        spoken_parts = []
        for block in re.split(r'\n\s*\n', raw_srt.strip()):
            lines = block.splitlines()
            left, right = lines[1].split(' --> ')
            text = ' '.join(lines[2:])
            spoken_parts.append(text)
            count = max(1, math.ceil(len(text) / 124), math.ceil((seconds(right) - seconds(left)) / 7))
            while True:
                parts = subtitle_parts(text, count)
                if all(len(textwrap.wrap(part, width=66, break_long_words=False, break_on_hyphens=False)) <= 2 for part in parts):
                    break
                count += 1
            for n, part in enumerate(parts):
                start = seconds(left) + (seconds(right) - seconds(left)) * n / count
                end = seconds(left) + (seconds(right) - seconds(left)) * (n + 1) / count
                all_cues.append({'start': scene['start'] + .3 + start / speed,
                                 'end': min(scene['end'] - .1, scene['start'] + .3 + end / speed),
                                 'text': part})
        assert re.sub(r'\s+', ' ', ' '.join(spoken_parts)).strip() == re.sub(r'\s+', ' ', scene['voiceover']).strip(), f'Narration mismatch in scene {i}'
        timings.append({'scene': i, 'start': scene['start'], 'end': scene['end'], 'source_seconds': duration, 'tempo': speed})

    merged = AUDIO / 'narration-180s.wav'
    with wave.open(str(merged), 'wb') as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(48000)
        for segment in segments:
            with wave.open(str(segment), 'rb') as source:
                output.writeframes(source.readframes(source.getnframes()))
    with wave.open(str(merged), 'rb') as source:
        assert source.getnframes() / source.getframerate() == 180

    srt = '\n\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i, c in enumerate(all_cues, 1))
    (WORK / 'MirrorCheck_Demo_EN_3min.srt').write_text(srt + '\n', encoding='utf-8')
    ass = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,34,&H00FFFFFF,&H00FFFFFF,&H00161923,&H00161923,0,0,0,0,100,100,0,0,1,1,0,2,110,110,29,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for cue in all_cues:
        display_text = cue['text'].replace('Paddle O C R', 'PaddleOCR')
        text = r'\N'.join(textwrap.wrap(display_text, width=66, break_long_words=False, break_on_hyphens=False))
        ass += f"Dialogue: 0,{stamp(cue['start'], True)},{stamp(cue['end'], True)},Default,,0,0,0,,{text}\n"
    (WORK / 'captions.ass').write_text(ass, encoding='utf-8')
    (WORK / 'audio-timing.json').write_text(json.dumps(timings, indent=2), encoding='utf-8')
    return merged, all_cues


def main():
    FRAMES.mkdir(exist_ok=True)
    scenes = json.loads((WORK / 'scenes.json').read_text(encoding='utf-8'))
    facts = json.loads((WORK / 'run-facts.json').read_text(encoding='utf-8'))
    assert facts['meta']['cached'] is False and facts['status_after_moderation'] == 'confirmed'
    assert facts['preview_provider_stored_bytes_equal'] and facts['matched_regions'] == 4
    for filename, digest in facts['captures_sha256'].items():
        assert hashlib.sha256((CAPTURES / filename).read_bytes()).hexdigest() == digest
    assert SHOTS[0][0] == 0 and SHOTS[-1][1] == 180
    assert all(a[1] == b[0] for a, b in zip(SHOTS, SHOTS[1:]))

    concat = ['ffconcat version 1.0']
    for i, (start, end, stage, mode, name, crop) in enumerate(SHOTS):
        if mode == 'intro':
            frame = draw_intro()
        elif mode == 'compare':
            frame = draw_compare(start)
        elif mode == 'redacted':
            frame = draw_redacted()
        elif mode == 'end':
            frame = draw_end()
        else:
            frame = draw_single(start, end, stage, name, crop)
        target = FRAMES / f'{i:02d}.png'
        frame.save(target)
        concat.extend([f"file 'frames/{target.name}'", f'duration {end - start}'])
        print(f'Prepared video shot {i + 1}/{len(SHOTS)}: {start}–{end}', flush=True)
    concat.append(f"file 'frames/{len(SHOTS) - 1:02d}.png'")
    (WORK / 'frames.ffconcat').write_text('\n'.join(concat) + '\n', encoding='utf-8')
    narration, captions = assemble_audio(scenes)
    # Relative filter paths avoid Windows drive-colon parsing inside libass.
    args = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-f', 'concat', '-safe', '0',
            '-i', 'frames.ffconcat', '-i', 'audio/narration-180s.wav', '-t', '180',
            '-vf', 'fps=30,ass=captions.ass,fade=t=in:st=0:d=0.25,fade=t=out:st=179.5:d=0.5',
            '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart',
            '-metadata', 'title=MirrorCheck — AI-Assisted Impersonation Review',
            '-metadata', 'comment=Edited authentic local browser captures; fictional accounts; real Meta API; synthetic English narration.',
            OUTPUT.name]
    subprocess.run(args, cwd=WORK, check=True)
    print(json.dumps({'output': str(OUTPUT), 'bytes': OUTPUT.stat().st_size, 'shots': len(SHOTS), 'caption_cues': len(captions)}), flush=True)


if __name__ == '__main__':
    main()
