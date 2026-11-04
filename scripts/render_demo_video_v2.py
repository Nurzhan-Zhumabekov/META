"""Render the refreshed 180s demo from current authentic captures and a landing motion clip."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
import render_demo_video as audio_helpers

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'outputs/demo-video-20261105'
CAPTURES = WORK / 'captures'
FRAMES = WORK / 'frames'
OUTPUT = WORK / 'MirrorCheck_Demo_EN_3min.mp4'
SIZE = (1920, 1080)
PAPER, INK, MUTED, GREEN = '#f8f7f4', '#202823', '#646c5d', '#337652'

STAGES = [
    ('A clearer signal.', 'A familiar feed. A more thoughtful review.', 'Moving gallery · New landing page'),
    ('Original and copy.', 'A new fictional copied profile. Shared content, different username.', 'aigerim.k → aigerim.k.showcase'),
    ('Start with evidence.', 'Report the account. Upload both screenshots and review the extracted fields.', 'PaddleOCR · Reporter review'),
    ('Redact before sending.', 'Detected contact lines are masked in the exact images prepared for Meta AI.', 'Local Presidio masking'),
    ('Separate signals.', 'Meta visual evidence, text reuse and spam patterns stay distinct.', 'Real uncached Meta API response'),
    ('A human decision.', 'A moderator examines processed evidence and explicitly confirms this fictional case.', 'No automatic profile warning'),
    ('The decision persists.', 'The warning remains after reloading the profile.', 'Saved moderator confirmation'),
    ('Dismissal matters too.', 'An earlier report about an ordinary profile was dismissed. No warning remains.', 'Earlier fictional rejected case'),
    ('Clear limits.', 'Synthetic pair-model training. Real-account validation is still needed.', 'Signals do not establish ownership'),
    ('A second look.', 'Explore the prototype, both outcomes and the source code.', 'MirrorCheck · Human review at the heart'),
]

# Editorial crops only; the source browser state is never fabricated.
SHOTS = [
    (12,18,0,'01-landing',None),
    (18,26,1,'02-original',(120,12,950,880)),
    (26,34,1,'03-copy-before',(120,12,950,880)),
    (34,40,2,'04-report-reason',(0,240,985,650)),
    (40,46,2,'05-upload',(190,60,815,770)),
    (46,51,2,'07-ocr-redaction',(205,180,805,850)),
    (51,58,2,'08-reviewed-fields',(210,80,805,850)),
    (58,68,3,'08-reviewed-fields',(220,0,790,420)),
    (68,78,3,'09-meta-processing',(180,200,815,710)),
    (78,84,4,'10-report-received',(185,90,815,650)),
    (84,94,4,'11-analysis',(195,50,815,850)),
    (94,102,4,'14-moderator-analysis',(100,100,950,820)),
    (102,110,5,'12-under-review',(120,15,950,560)),
    (110,118,5,'13-moderator-evidence',(100,155,950,800)),
    (118,124,5,'15-moderator-action',(100,380,950,705)),
    (124,130,6,'16-decision-saved',(90,15,950,380)),
    (130,142,6,'17-label-after-reload',(120,20,950,520)),
    (142,150,7,'18-rejected-case',(0,0,985,800)),
    (150,160,7,'19-normal-no-label',(120,20,950,570)),
    (160,172,8,'14-moderator-analysis',(100,100,950,820)),
    (172,180,9,'01-landing',None),
]


def font(size, bold=False, serif=False):
    name = 'georgiai.ttf' if serif else ('segoeuib.ttf' if bold else 'segoeui.ttf')
    return ImageFont.truetype(str(Path('C:/Windows/Fonts') / name), size)


def wrapped(draw, xy, text, typeface, width, fill=INK, gap=9):
    x,y = xy
    line = ''
    for word in text.split():
        proposal = (line+' '+word).strip()
        if line and draw.textlength(proposal,font=typeface)>width:
            draw.text((x,y),line,font=typeface,fill=fill)
            y += typeface.size+gap
            line = word
        else:
            line = proposal
    if line:
        draw.text((x,y),line,font=typeface,fill=fill)
        y += typeface.size+gap
    return y


def frame(stage, start, source, crop=None):
    image = Image.new('RGB',SIZE,PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((54,24),'mirrorcheck.',font=font(35,True),fill=INK)
    draw.text((54,70),'A SECOND LOOK. A HUMAN DECISION.',font=font(14),fill=MUTED)
    tag='Fictional profiles  ·  Recorded interface  ·  Edited for time'
    draw.text((1865-draw.textlength(tag,font=font(18)),36),tag,font=font(18),fill=MUTED)
    draw.line((54,108,1866,108),fill='#dedfd6',width=2)
    draw.text((56,156),f'{stage+1:02d} / 10',font=font(19,True),fill=GREEN)
    headline, body, fact = STAGES[stage]
    y=wrapped(draw,(54,224),headline,font(51,serif=True),350,gap=7)
    wrapped(draw,(57,y+26),body,font(24),345,fill=MUTED,gap=11)
    draw.rounded_rectangle((54,744,405,890),radius=12,fill='#eaf0e2')
    wrapped(draw,(75,767),fact,font(20,True),309,fill='#42543a',gap=9)
    draw.text((75,860),'EDITORIAL CONTEXT',font=font(12),fill='#646c5d')
    box=(445,137,1872,914)
    draw.rounded_rectangle(box,radius=18,fill='white',outline='#dfe1d8',width=2)
    with Image.open(source) as raw:
        shot=raw.convert('RGB')
        if crop:
            if not(0<=crop[0]<crop[2]<=shot.width and 0<=crop[1]<crop[3]<=shot.height):
                raise ValueError(f'Crop exceeds source {source.name}: {shot.size}')
            shot=shot.crop(crop)
        fitted=ImageOps.contain(shot,(1395,745),Image.Resampling.LANCZOS)
        image.paste(fitted,(box[0]+(1427-fitted.width)//2,box[1]+(777-fitted.height)//2))
    draw.rectangle((56,931,1864,934),fill='#dcdfd4')
    draw.rectangle((56,931,56+round(1808*start/180),934),fill=GREEN)
    draw.rounded_rectangle((44,950,1876,1064),radius=15,fill=INK)
    return image


def ffmpeg(*args):
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*map(str,args)],cwd=WORK,check=True)


def main():
    FRAMES.mkdir(exist_ok=True)
    facts=json.loads((WORK/'run-facts.json').read_text(encoding='utf-8'))
    if facts['meta']['cached'] is not False or facts['status_after_moderation']!='confirmed':
        raise ValueError('A real uncached confirmed browser case is required')
    for name,digest in facts['captures_sha256'].items():
        if hashlib.sha256((CAPTURES/name).read_bytes()).hexdigest()!=digest:
            raise ValueError(f'Capture changed: {name}')
    scenes=json.loads((WORK/'scenes.json').read_text(encoding='utf-8'))
    audio_helpers.WORK=WORK
    audio_helpers.AUDIO=WORK/'audio'
    narration,captions=audio_helpers.assemble_audio(scenes)
    ass=WORK/'captions.ass'
    ass.write_text(ass.read_text().replace('M L','ML'),encoding='utf-8')
    srt=WORK/'MirrorCheck_Demo_EN_3min.srt'
    srt.write_text(srt.read_text(encoding='utf-8').replace('Paddle O C R','PaddleOCR').replace('M L','ML'),encoding='utf-8')

    recording=json.loads((WORK/'motion/recording.json').read_text())
    if not recording['transformsChanged'] or len(recording['frames'])<12:
        raise ValueError('A genuine moving landing capture is required')
    motion_concat=['ffconcat version 1.0']
    for i,item in enumerate(recording['frames']):
        target=FRAMES/f'motion-{i:05d}.png'
        frame(0,item['at'],WORK/'motion'/item['file']).save(target)
        end=recording['frames'][i+1]['at'] if i+1<len(recording['frames']) else recording['duration']
        motion_concat.extend([f"file 'frames/{target.name}'",f"duration {max(.001,end-item['at']):.6f}"])
    motion_concat.append(f"file 'frames/motion-{len(recording['frames'])-1:05d}.png'")
    (WORK/'motion.ffconcat').write_text('\n'.join(motion_concat)+'\n')
    ffmpeg('-f','concat','-safe','0','-i','motion.ffconcat','-t','12','-vf','fps=30','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','landing-motion.mp4')

    stills=['ffconcat version 1.0']
    for i,(start,end,stage,name,crop) in enumerate(SHOTS):
        target=FRAMES/f'still-{i:02d}.png'
        frame(stage,start,CAPTURES/f'{name}.png',crop).save(target)
        stills.extend([f"file 'frames/{target.name}'",f'duration {end-start}'])
        print(f'Prepared updated shot {i+1}/{len(SHOTS)}',flush=True)
    stills.append(f"file 'frames/still-{len(SHOTS)-1:02d}.png'")
    (WORK/'stills.ffconcat').write_text('\n'.join(stills)+'\n')
    encode(narration)
    print(json.dumps({'output':str(OUTPUT),'bytes':OUTPUT.stat().st_size,'caption_cues':len(captions)}),flush=True)


def encode(narration):
    # Keep the captured motion and static evidence in one final encode.
    filters = '[0:v]fps=30,setpts=PTS-STARTPTS[m];[1:v]fps=30,trim=duration=168,setpts=PTS-STARTPTS[s];[m][s]concat=n=2:v=1:a=0,ass=captions.ass,fade=t=in:st=0:d=0.25,fade=t=out:st=179.5:d=0.5[v]'
    ffmpeg('-i','landing-motion.mp4','-f','concat','-safe','0','-i','stills.ffconcat','-i',narration,'-t','180','-filter_complex',filters,'-map','[v]','-map','2:a',
           '-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
           '-metadata','title=MirrorCheck — A clearer signal',
           '-metadata','comment=Updated authentic UI captures; genuine moving landing clip; fictional profiles; real Meta API; human decisions; synthesized English narration.',OUTPUT)


if __name__=='__main__':
    main()
