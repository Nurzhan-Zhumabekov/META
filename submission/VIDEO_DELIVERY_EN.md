# Refreshed three-minute English demo

Watch in the running app: [MirrorCheck video player](http://localhost:8090/demo-video.html).
The [landing page](http://localhost:8090/demo-guide.html) also links to the video.

Download the [MP4 from the source release](https://github.com/Nurzhan-Zhumabekov/META/raw/refs/heads/main/web/public/MirrorCheck_Demo_EN_3min.mp4).
[English SRT captions](https://github.com/Nurzhan-Zhumabekov/META/raw/refs/heads/main/web/public/MirrorCheck_Demo_EN_3min.srt),
[recorded narration](VOICEOVER_RECORDED_EN.txt), [current scenes](VIDEO_SCENES_RECORDED_EN.json)
and [verification facts](VIDEO_VERIFICATION_EN.json) describe this refreshed export.

The video is exactly **03:00**, **1920 × 1080**, **30 fps**, H.264 with AAC stereo
audio. English narration is synthesized using Microsoft Andrew. Captions are
burned into the video, with a separate SRT for reuse. The player uses the new
landing page's paper, ink and muted green palette.

| Time | Demonstration |
| --- | --- |
| 00:00–00:18 | New landing page, including 12 seconds of genuine moving gallery capture |
| 00:18–00:34 | The original and a fresh fictional copied profile |
| 00:34–00:58 | Report, screenshots, editable PaddleOCR fields and reporter review |
| 00:58–01:18 | Two contact masks and the exact processed previews before Meta AI |
| 01:18–01:42 | Real Meta response, separate text ML, spam ML and four photo-region matches |
| 01:42–02:04 | Under-review status, processed evidence and explicit moderator confirmation |
| 02:04–02:22 | Saved decision and profile warning after reload |
| 02:22–02:40 | An earlier dismissed report and an ordinary profile without a warning |
| 02:40–03:00 | Model limitations and the closing view of MirrorCheck |

This is an edited presentation of authentic browser captures, with waiting time
condensed. The first 12 seconds use 159 timestamped screenshots from an actual
moving landing capture; the remaining material uses edited browser stills. It
is not a continuous realtime recording. The operator demonstrates reporter and
moderator on fictional accounts.

The fresh positive case is `aigerim.k.showcase`, claim `9a26d2b2`. The uncached
Meta Muse Spark response reports 90% visual similarity and recommends human
review. The UI separately displays 85.3% combined reuse, 72.1% text-reuse ML and
94.5% profile spam-pattern ML. Four image regions match and two contact regions
are masked. The preview images match the stored evidence and recorded provider
image hashes byte for byte. These values are signals, not accuracy measurements
or proof of ownership.

The earlier negative case, `99a356a9` for `aruzhan.jpg`, remains rejected. The video
revisits that saved case and the current profile without a warning; it does not
claim a new Meta request for the negative example. All 12 pre-existing report
records and all 18 pre-existing evidence files were preserved unchanged.

Verification includes complete video/audio decoding, 5,400 frames, exact
duration, sentence timing alignment, visual review of the edited frames, audio
level measurement and a scan for known local credentials. The previous export's
speech-recognition result is not reused for this version. Audio measures
−16.13 LUFS integrated with −1.41 dBTP true peak.

Optional authoring uses `scripts/synthesize_demo_voice.py` with edge-tts 7.3.1,
then `scripts/render_demo_video_v2.py` with Pillow and ffmpeg/ffprobe. The authoring
directory contains private capture manifests and baseline records and is ignored
by Git. Rendering requires those genuine captured inputs; it does not create or
change reports. The original `DEMO_VIDEO_SCRIPT_EN.md` and its 15 stills retain
the earlier archive-profile plan; use the current scene manifest above for this
finished video.

The [November 5 submission packet](https://github.com/Nurzhan-Zhumabekov/META/blob/main/releases/submission-kit-20261105.zip)
contains the current delivery documents and the earlier supporting material.
No final hackathon form was submitted. The form's accepted video hosts and field
restrictions still need checking before submission; a source-repository MP4 URL
may require uploading to an accepted video host.
