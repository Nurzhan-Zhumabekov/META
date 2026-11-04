import numpy as np
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
