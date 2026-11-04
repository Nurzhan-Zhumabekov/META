"""Real CPU inference. Torch MUST load before Paddle on this Windows runtime."""
from functools import lru_cache
import numpy as np


@lru_cache(maxsize=1)
def ocr_engine():
    # Loading Paddle first caused WinError 127 when torch loaded shm.dll.
    from imagededup.methods import PHash
    from paddleocr import PaddleOCR
    PHash(verbose=False)
    # Explicit model names avoid PaddleOCR 3.7 ignoring lang='ru' after a
    # detector name is supplied and silently choosing the Latin/CJK v6 model.
    return PaddleOCR(text_detection_model_name='PP-OCRv5_mobile_det',
        text_recognition_model_name='cyrillic_PP-OCRv5_mobile_rec',
        use_doc_orientation_classify=False, use_doc_unwarping=False,
        use_textline_orientation=False, device='cpu', enable_mkldnn=False, cpu_threads=4)


def read_text(image):
    result = list(ocr_engine().predict(np.array(image.convert('RGB'))))[0]
    return [{'text': text[:1000], 'confidence': float(score), 'box': box.tolist()}
            for text, score, box in zip(result['rec_texts'], result['rec_scores'], result['rec_boxes'])][:512]
