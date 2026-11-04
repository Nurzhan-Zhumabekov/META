# Finished three-minute English demo

Watch in the running local app: http://localhost:8090/demo-video.html

Download the source release's video: [MP4](https://github.com/Nurzhan-Zhumabekov/META/raw/refs/heads/main/web/public/MirrorCheck_Demo_EN_3min.mp4).
English [SRT captions](https://github.com/Nurzhan-Zhumabekov/META/raw/refs/heads/main/web/public/MirrorCheck_Demo_EN_3min.srt) and the
[recorded narration](VOICEOVER_RECORDED_EN.txt) are supplied separately.

The export is exactly **03:00**, **1920 × 1080**, **30 fps**, H.264 video and
AAC stereo audio. English narration is synthesized using Microsoft Andrew.
Captions are also burned into the video, so no separate subtitle setup is needed.

| Time | Demonstration |
| --- | --- |
| 00:00–00:28 | The original and a new fictional copy |
| 00:28–00:50 | Report, screenshot upload and editable PaddleOCR fields |
| 00:50–01:12 | Local Presidio masking before Meta receives images |
| 01:12–01:56 | Real Meta Muse Spark response, independent ML and image-region matches |
| 01:56–02:14 | Under-review state and model limitations |
| 02:14–02:32 | Explicit moderator confirmation and saved decision |
| 02:32–03:00 | Profile warning after reload and next steps |

This is an edited demonstration using actual new browser captures, with waiting
time condensed. It is not a continuous realtime screen recording. The operator
plays reporter and moderator for fictional `aigerim.k.demo`, claim `1b96686f`.
The Meta response is real and uncached; the scores are evidence signals, not
accuracy measurements or proof of ownership. Two contact regions were masked and
four matching image regions were found. Earlier report records are unchanged.

The original submission script and its 15 stills document the earlier
`aigerim.k.archive` run. The finished video uses the newer case above; follow
`VOICEOVER_RECORDED_EN.txt` and `VIDEO_VERIFICATION_EN.json` for its exact facts.

Verification includes full decoding of video and audio, 5,400 video frames,
caption/narration alignment, an automated English speech-content check and a scan
for known local credentials. No final hackathon form was submitted. The actual
form's accepted video hosts and field restrictions still need checking; a source
repository MP4 URL may need to be uploaded to an accepted video host.
