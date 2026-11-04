import io
import numpy as np
from pathlib import Path
import pytest
from PIL import Image, ImageDraw

from evidence_tools.photos import compare_photos, find_post_regions


def screenshot(photo, *, avatar_only=False):
    image = Image.new('RGB', (500, 600), 'white')
    ImageDraw.Draw(image).ellipse((25, 25, 125, 125), fill='red')
    if not avatar_only:
        image.paste(photo.resize((200, 260)), (30, 270))
    return image


def photo(seed):
    rng = np.random.default_rng(seed)
    # Structured, different textures rather than near-uniform noise.
    data = np.zeros((260, 200, 3), dtype='uint8')
    for _ in range(30):
        x,y = rng.integers(0,140),rng.integers(0,200)
        data[y:y+60,x:x+60] = rng.integers(20,220,size=3)
    return Image.fromarray(data)


def test_identical_post_photo_is_matched_with_real_imagededup():
    result = compare_photos(screenshot(photo(1)), screenshot(photo(1)))
    assert result['count'] == 1
    assert result['matches'][0]['phash_distance'] == 0


def test_shared_avatar_is_not_reported_as_a_copied_post():
    assert compare_photos(screenshot(photo(1), avatar_only=True), screenshot(photo(1), avatar_only=True))['count'] == 0


def test_unrelated_photos_do_not_match():
    assert compare_photos(screenshot(photo(1)), screenshot(photo(8)))['count'] == 0


def test_uniform_and_dark_images_abstain():
    assert find_post_regions(Image.new('RGB', (500, 600), 'black')) == []
    assert find_post_regions(Image.new('RGB', (500, 600), 'white')) == []


def test_window_border_does_not_hide_post_regions_inside_it():
    image = screenshot(photo(1))
    ImageDraw.Draw(image).rectangle((0, 0, 499, 599), outline='#dddddd', width=1)
    assert compare_photos(image, image)['count'] == 1


def test_compressed_one_pixel_gutter_keeps_two_posts_separate():
    image = Image.new('RGB', (500,600), 'white')
    image.paste(photo(1).resize((200,260)), (30,270))
    image.paste(photo(8).resize((200,260)), (231,270))
    ImageDraw.Draw(image).line((230,270,230,529), fill=(236,235,239), width=1)
    assert compare_photos(image,image)['count'] == 2


@pytest.mark.parametrize('scale,quality', [(1, None), (0.75, 80), (1.2, 75)])
def test_recorded_four_column_profiles_detect_shared_stock_photo(scale, quality):
    fixtures = Path(__file__).parent / 'fixtures'
    original = Image.open(fixtures / 'original-four-column.png').convert('RGB')
    ordinary = Image.open(fixtures / 'ordinary-four-column.png').convert('RGB')
    def resized(image):
        image = image.resize((round(image.width * scale), round(image.height * scale)))
        if quality is not None:
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=quality)
            buffer.seek(0)
            image = Image.open(buffer).convert('RGB')
        return image
    original, ordinary = resized(original), resized(ordinary)
    # The lake photograph is fully visible in both screenshots, in different
    # columns. A darkened gutter and the floating Messages control previously
    # merged cells and returned zero. Photo reuse alone is not impersonation.
    result = compare_photos(original, ordinary)
    assert result['count'] >= 1
    full_row = [box for box in find_post_regions(ordinary) if box[1] < 520 * scale and box[3] > 740 * scale]
    assert len(full_row) == 4
    assert all(170 * scale <= box[2] - box[0] <= 190 * scale for box in full_row)


def test_regular_grid_recovers_one_obscured_gutter_without_matching_controls():
    image = Image.new('RGB', (1200, 900), 'white')
    for row in range(2):
        for col in range(4):
            image.paste(photo(row * 4 + col + 1).resize((200, 260)), (100 + col * 201, 450 + row * 261))
    draw = ImageDraw.Draw(image)
    draw.line((300, 590, 300, 690), fill='#6c757d', width=1)
    draw.rounded_rectangle((800, 820, 1130, 880), radius=25, fill='#f5f5f5', outline='#dddddd', width=2)
    result = compare_photos(image, image)
    first_row = [box for box in find_post_regions(image) if 445 <= box[1] <= 455]
    assert len(first_row) == 4
    assert all(190 <= box[2] - box[0] <= 210 for box in first_row)
    assert result['count'] >= 4


def test_recorded_faint_neutral_gutters_keep_four_copied_photos_separate():
    fixtures = Path(__file__).parent / 'fixtures'
    original = Image.open(fixtures / 'original-faint-gutters.png').convert('RGB')
    copied = Image.open(fixtures / 'copy-faint-gutters.png').convert('RGB')
    # Subpixel borders fall below the strict near-white gutter threshold.
    result = compare_photos(original, copied)
    assert result['count'] >= 4


def test_faint_gutter_recovery_does_not_match_unrelated_regular_grids():
    def grid(offset):
        image = Image.new('RGB', (1100, 900), 'white')
        draw = ImageDraw.Draw(image)
        for col in range(4):
            image.paste(photo(offset + col).resize((180, 240)), (100 + col*181, 400))
            if col < 3:
                draw.line((280 + col*181, 400, 280 + col*181, 639), fill=(205,205,205))
        return image
    result = compare_photos(grid(1), grid(20))
    assert len(result['original_boxes']) >= 4
    assert len(result['suspect_boxes']) >= 4
    assert result['count'] == 0


def test_geometric_matching_recovers_a_rotated_cropped_photo():
    import random
    from PIL import ImageOps
    def textured(seed):
        rng = random.Random(seed)
        im = Image.new('RGB', (600,600), '#e0d7bb'); draw = ImageDraw.Draw(im)
        for i in range(180):
            x,y=rng.randrange(20,560),rng.randrange(20,560)
            draw.rectangle((x,y,x+rng.randrange(5,35),y+rng.randrange(5,35)), fill=tuple(rng.randrange(30,220) for _ in range(3)))
            draw.text((x,y),str(i),fill='black')
        return im
    source=textured(713)
    copy=source.crop((70,55,530,535)).rotate(11,resample=Image.Resampling.BICUBIC)
    def grid(im, seed):
        out=Image.new('RGB',(900,900),'white')
        for i,p in enumerate([im,textured(seed),textured(seed+1),textured(seed+2),textured(seed+3),textured(seed+4)]):
            out.paste(ImageOps.fit(p,(240,240)),(40+(i%3)*243,330+(i//3)*243))
        return out
    result=compare_photos(grid(source,100),grid(copy,200))
    assert any(m.get('verification')=='orb_geometry' and m.get('geometric_inliers',0)>=12 for m in result['matches'])


def test_sift_geometry_supports_structure_and_rejects_unrelated_textures():
    from evidence_tools.photos import _local_features, _geometry
    first = _local_features(np.array(photo(27)), kind='sift')
    same = _local_features(np.array(photo(27)), kind='sift')
    unrelated = _local_features(np.array(photo(91)), kind='sift')
    assert _geometry(first,same)['verification'] == 'sift_geometry'
    assert _geometry(first,unrelated) is None
