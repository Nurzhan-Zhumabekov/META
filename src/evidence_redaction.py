"""Burn local Presidio findings into pixels; encode the exact provider previews."""
import base64
import hashlib
import io
import math
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageOps

from .errors import ComparisonUnavailable

POLICY_VERSION = 'presidio-opaque-lines-v1'
ENTITIES = {'EMAIL_ADDRESS','PHONE_NUMBER','CREDIT_CARD','IBAN_CODE','IP_ADDRESS'}


def encode_image(image):
    normalized = ImageOps.exif_transpose(image).convert('RGB')
    normalized.thumbnail((1280,1280), Image.Resampling.LANCZOS)
    # A fresh canvas strips source metadata, including EXIF/XMP/comments.
    clean = Image.new('RGB', normalized.size)
    clean.paste(normalized)
    buffer = io.BytesIO()
    clean.save(buffer, 'JPEG', quality=85)
    return buffer.getvalue()


@dataclass(frozen=True)
class RedactedPair:
    raw: tuple[bytes, bytes]
    audit: dict

    @property
    def urls(self):
        return tuple('data:image/jpeg;base64,'+base64.b64encode(raw).decode('ascii') for raw in self.raw)


def redact_pair(original, suspect, inspection):
    encoded, details = [], {}
    try:
        for side, source in [('original',original),('suspect',suspect)]:
            privacy=inspection[side]['privacy']
            findings=privacy['findings']
            if privacy['provider']!='presidio' or type(privacy['count']) is not int or privacy['count']!=len(findings):
                raise ValueError('Invalid privacy report')
            image=ImageOps.exif_transpose(source).convert('RGB')
            image.thumbnail((1800,1800), Image.Resampling.LANCZOS)
            draw=ImageDraw.Draw(image)
            padding=max(4,math.ceil(max(image.size)*.006))
            for finding in findings:
                box=finding['box']
                if finding['entity_type'] not in ENTITIES or len(box)!=4:
                    raise ValueError('Invalid privacy region')
                if any(type(v) not in {int,float} or not math.isfinite(v) or not 0<=v<=1 for v in box):
                    raise ValueError('Invalid privacy coordinates')
                x,y,x2,y2=box
                if x>=x2 or y>=y2:
                    raise ValueError('Empty/reversed privacy region')
                pixels=(max(0,math.floor(x*image.width)-padding),max(0,math.floor(y*image.height)-padding),
                        min(image.width-1,math.ceil(x2*image.width)+padding),min(image.height-1,math.ceil(y2*image.height)+padding))
                draw.rectangle(pixels,fill=(12,14,18))
            raw=encode_image(image)
            encoded.append(raw)
            details[side]={'sha256':hashlib.sha256(raw).hexdigest(),'regions_masked':len(findings)}
    except (KeyError,TypeError,ValueError,OverflowError):
        raise ComparisonUnavailable('redaction_invalid','Personal data could not be safely redacted. No images were sent to Meta AI.',503) from None
    return RedactedPair(tuple(encoded),{'applied':True,'provider':'presidio','policy_version':POLICY_VERSION,
        'method':'opaque-line-masks','regions_masked':sum(i['regions_masked'] for i in details.values()),
        'images':details})
