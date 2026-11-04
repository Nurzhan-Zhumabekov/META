"""Optional video-authoring tool: synthesize the authored English scenes with edge-tts 7.3.1."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path


async def synthesize(work: Path):
    import edge_tts
    scenes = json.loads((work / 'scenes.json').read_text(encoding='utf-8'))
    audio = work / 'audio'
    audio.mkdir(parents=True, exist_ok=True)
    for index, scene in enumerate(scenes, 1):
        text = scene['voiceover']
        digest = hashlib.sha256(text.encode()).hexdigest()
        stem = audio / f'{index:02d}'
        signature = stem.with_suffix('.sha256')
        if signature.exists() and signature.read_text() == digest and stem.with_suffix('.mp3').exists() and stem.with_suffix('.srt').exists():
            print(f'Voice scene {index}/{len(scenes)} already prepared', flush=True)
            continue
        for attempt in range(3):
            submaker = edge_tts.SubMaker()
            communicate = edge_tts.Communicate(text, 'en-US-AndrewNeural', boundary='SentenceBoundary')
            try:
                with stem.with_suffix('.mp3').open('wb') as output:
                    async for chunk in communicate.stream():
                        if chunk['type'] == 'audio':
                            output.write(chunk['data'])
                        elif chunk['type'] == 'SentenceBoundary':
                            submaker.feed(chunk)
                break
            except (edge_tts.exceptions.NoAudioReceived, ConnectionError, TimeoutError):
                if attempt == 2:
                    raise
                print(f'Retrying voice scene {index} ({attempt + 1}/2)', flush=True)
                await asyncio.sleep(attempt + 1)
        if not submaker.cues:
            raise RuntimeError(f'Missing timing metadata for voice scene {index}')
        stem.with_suffix('.srt').write_text(submaker.get_srt(), encoding='utf-8')
        signature.write_text(digest)
        print(f'Prepared voice scene {index}/{len(scenes)}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'outputs/demo-video-20261105')
    args = parser.parse_args()
    asyncio.run(synthesize(args.work_dir.resolve()))
