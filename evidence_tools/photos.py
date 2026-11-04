"""Post-photo regions and conservative one-to-one matches using imagededup."""
import numpy as np


def _regular_intervals(intervals):
    """Recover integer-width merged cells only with two agreeing references."""
    if len(intervals) < 3:
        return intervals
    typical = float(np.median([right-left for left,right in intervals]))
    if sum(abs(right-left-typical) <= max(3, typical*0.06) for left,right in intervals) < 2:
        return intervals
    regular = []
    for left,right in intervals:
        span = right-left
        count = round((span+1)/(typical+1))
        if 2 <= count <= 4 and abs(span-(count*typical+count-1)) <= max(3, span*0.06):
            stride = (span+1)/count
            regular.extend((left+round(i*stride), left+round((i+1)*stride)-1) for i in range(count))
        else:
            regular.append((left,right))
    return regular


def find_post_regions(image):
    import cv2
    rgb = np.array(image.convert('RGB'))
    height, width = rgb.shape[:2]
    # White/light profile layouts only. Uniform dark screenshots must abstain.
    mask = (np.min(rgb, axis=2) < 240).astype('uint8') * 255
    raw_contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    grids, cells = [], []
    def segments(values, length, threshold=0.86):
        indices = np.flatnonzero(values > threshold)
        groups = []
        for index in indices:
            if groups and index == groups[-1][-1] + 1:
                groups[-1].append(int(index))
            else:
                groups.append([int(index)])
        # Wide whitespace is a grid boundary too. Ignoring it lets floating
        # controls extend the final photo crop into the empty side panel.
        cuts = [(g[0],g[-1]+1) for g in groups]
        points, previous = [], 0
        for start,end in cuts:
            if start-previous >= 64:
                points.append((previous,start))
            previous=end
        if length-previous >= 64:
            points.append((previous,length))
        return points
    # JPEG-like screenshot ringing can make gutters almost white rather than
    # exactly white, merging an entire grid into a single irregular contour.
    for contour in sorted(raw_contours,key=cv2.contourArea,reverse=True):
        x,y,w,h = cv2.boundingRect(contour)
        if y < height*0.25 or w < width*0.35 or h < height*0.12 or w*h > width*height*0.7:
            continue
        if any(x>=g[0]-2 and y>=g[1]-2 and x+w<=g[2]+2 and y+h<=g[3]+2 for g in grids):
            continue
        patch = rgb[y:y+h,x:x+w].astype(float)
        bright = (patch.min(axis=2)>220) & (patch.max(axis=2)-patch.min(axis=2)<35)
        xs,ys = segments(bright.mean(axis=0),w),segments(bright.mean(axis=1),h)
        if len(xs) < 3:
            # Downscaled JPEGs can weaken a 1px gutter. Accept the additional
            # boundaries only when their widths support a regular grid; hash,
            # difference-hash and pixel-correlation match thresholds stay fixed.
            candidate = segments(bright.mean(axis=0),w,threshold=0.8)
            regular = _regular_intervals(candidate)
            if len(candidate) >= 3 and len(regular) > len(candidate):
                xs = candidate
        if len(xs) < 3:
            # Subpixel-rendered gutters can be neutral gray rather than white.
            # Only adopt them when at least three recovered cells agree in
            # width. This changes region extraction, never match thresholds.
            for level in (210, 190):
                neutral = (patch.min(axis=2)>level) & (patch.max(axis=2)-patch.min(axis=2)<45)
                candidate = _regular_intervals(segments(neutral.mean(axis=0),w,threshold=0.75))
                widths = [right-left for left,right in candidate]
                if len(widths) >= 3 and min(widths) >= max(widths)*0.88:
                    xs = candidate
                    break
        if len(xs)*len(ys) < 2:
            continue
        xs = _regular_intervals(xs)
        grids.append([x,y,x+w,y+h])
        for y0,y1 in ys:
            for x0,x1 in xs:
                crop=patch[y0:y1,x0:x1]
                if 0.45 <= (x1-x0)/(y1-y0) <= 2.1 and crop.std()>18 and bright[y0:y1,x0:x1].mean()<0.75:
                    cells.append([x+x0,y+y0,x+x1,y+y1])
    # Screenshot compression can connect adjacent photos across a nominally
    # white 1–3px gutter; remove those thin bridges and window borders first.
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), dtype='uint8'))
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if any(x>=g[0]-2 and y>=g[1]-2 and x+w<=g[2]+2 and y+h<=g[3]+2 for g in grids):
            continue
        if min(w, h) < 64 or area < width * height * 0.008 or area > width * height * 0.7:
            continue
        if not 0.45 <= w / h <= 2.1 or cv2.contourArea(contour) / area < 0.86:
            continue
        if float(mask[y:y+h, x:x+w].mean()/255) < 0.65:
            continue
        crop = rgb[y:y+h, x:x+w]
        if float(np.std(crop.astype(float))) < 18:
            continue
        boxes.append([x, y, x+w, y+h])
    # Cap work and exclude small controls above the main post grid when larger
    # rectangles are present. Circular avatars/highlights fail rectangularity.
    boxes.extend(cells)
    # A merged pair can be too narrow to qualify as a whole grid contour.
    # Use the other cells on the same row as references in that case.
    rows = []
    for box in boxes:
        row = next((row for row in rows if abs(row[0][1]-box[1]) <= 3 and abs(row[0][3]-box[3]) <= 3), None)
        if row is None:
            rows.append([box])
        else:
            row.append(box)
    boxes = []
    for row in rows:
        intervals = _regular_intervals([(box[0],box[2]) for box in row])
        if len(intervals) == len(row):
            boxes.extend(row)
        else:
            boxes.extend([left,row[0][1],right,row[0][3]] for left,right in intervals)
    outer = []
    for box in sorted(boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]), reverse=True):
        if not any(box[0] >= b[0]-2 and box[1] >= b[1]-2 and box[2] <= b[2]+2 and box[3] <= b[3]+2 for b in outer):
            outer.append(box)
    outer.sort(key=lambda b: (b[1], b[0]))
    return outer[:24]


def _local_features(array, kind='orb'):
    import cv2
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    scale = min(1., 320/max(gray.shape))
    if scale < 1:
        gray = cv2.resize(gray, None, fx=scale, fy=scale)
    detector = cv2.SIFT_create(nfeatures=700) if kind == 'sift' else cv2.ORB_create(nfeatures=700, edgeThreshold=15, fastThreshold=10)
    keypoints, descriptors = detector.detectAndCompute(gray, None)
    return keypoints, descriptors, gray.shape


def _geometry(first, second):
    import cv2
    key_a, desc_a, shape_a = first
    key_b, desc_b, shape_b = second
    if desc_a is None or desc_b is None or min(len(key_a),len(key_b)) < 12:
        return None
    is_sift = desc_a.dtype != np.uint8
    matcher = cv2.FlannBasedMatcher({'algorithm':1,'trees':4},{'checks':48}) if is_sift else cv2.BFMatcher(cv2.NORM_HAMMING)
    maximum_distance = 250 if is_sift else 64
    forward = matcher.knnMatch(desc_a, desc_b, k=2)
    reverse = matcher.knnMatch(desc_b, desc_a, k=2)
    backward = {(a.queryIdx,a.trainIdx) for pair in reverse if len(pair)==2 for a,b in [pair]
                if a.distance < .75*b.distance and a.distance <= maximum_distance}
    good = [a for pair in forward if len(pair)==2 for a,b in [pair]
            if a.distance < .75*b.distance and a.distance <= maximum_distance and (a.trainIdx,a.queryIdx) in backward]
    if len(good) < 12:
        return None
    source = np.float32([key_a[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    target = np.float32([key_b[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    cv2.setRNGSeed(0)
    matrix, mask = cv2.findHomography(source,target,cv2.RANSAC,3.)
    if matrix is None or mask is None or not np.isfinite(matrix).all():
        return None
    inliers = mask.ravel().astype(bool)
    count, ratio = int(inliers.sum()), float(inliers.mean())
    if count < 12 or ratio < .5:
        return None
    for points, shape in [(source[inliers],shape_a),(target[inliers],shape_b)]:
        coverage = cv2.contourArea(cv2.convexHull(points)) / (shape[0]*shape[1])
        if coverage < .08:
            return None
    h,w = shape_a
    corners = np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2)
    projected = cv2.perspectiveTransform(corners,matrix)
    area = cv2.contourArea(projected) / (shape_b[0]*shape_b[1])
    if not cv2.isContourConvex(projected) or not .15 <= area <= 12 or np.max(np.abs(projected)) > 10*max(shape_b):
        return None
    return {'verification':'sift_geometry' if is_sift else 'orb_geometry','geometric_inliers':count,'geometric_ratio':round(ratio,4)}


def compare_photos(original, suspect):
    from imagededup.methods import PHash, DHash
    phash, dhash = PHash(verbose=False), DHash(verbose=False)
    image_boxes = [find_post_regions(original), find_post_regions(suspect)]
    descriptors = []
    for image, boxes in zip([original, suspect], image_boxes):
        entries = []
        for box in boxes:
            crop = image.crop(box).convert('RGB')
            array = np.array(crop)
            entries.append((phash.encode_image(image_array=array), dhash.encode_image(image_array=array),
                            np.array(crop.resize((24, 24))).astype(float).reshape(-1), array))
        descriptors.append(entries)
    candidates = []
    geometry_cache = {}
    def features(side, index, kind='orb'):
        if (side,index,kind) not in geometry_cache:
            geometry_cache[(side,index,kind)] = _local_features(descriptors[side][index][3],kind)
        return geometry_cache[(side,index,kind)]
    for i, (a, ad, pixels_a, _) in enumerate(descriptors[0]):
        for j, (b, bd, pixels_b, _) in enumerate(descriptors[1]):
            distance = (int(a, 16) ^ int(b, 16)).bit_count()
            dhash_distance = (int(ad, 16) ^ int(bd, 16)).bit_count()
            centered_a, centered_b = pixels_a - pixels_a.mean(), pixels_b - pixels_b.mean()
            denominator = np.linalg.norm(centered_a) * np.linalg.norm(centered_b)
            correlation = float(centered_a @ centered_b / denominator) if denominator else 0
            if distance <= 8 and dhash_distance <= 12 and correlation >= 0.88:
                candidates.append((0,distance,-correlation,i,j,dhash_distance,distance,{'verification':'perceptual_hash'}))
            elif distance <= 32:
                verified = _geometry(features(0,i),features(1,j))
                if not verified:
                    verified = _geometry(features(0,i,'sift'),features(1,j,'sift'))
                if verified:
                    candidates.append((1,-verified['geometric_inliers'],-correlation,i,j,dhash_distance,distance,verified))
    used_original, used_suspect, matches = set(), set(), []
    for _, _, negative_corr, i, j, dd, distance, verified in sorted(candidates, key=lambda entry:entry[:7]):
        if i in used_original or j in used_suspect:
            continue
        used_original.add(i); used_suspect.add(j)
        matches.append({'original_index': i, 'suspect_index': j, 'phash_distance': distance,
                        'dhash_distance': dd, 'pixel_correlation': round(-negative_corr, 4), **verified})
    def normalized(boxes, image):
        return [[round(x/image.width, 6), round(y/image.height, 6), round(x2/image.width, 6), round(y2/image.height, 6)] for x,y,x2,y2 in boxes]
    return {'provider': 'imagededup', 'method': 'PHash+DHash+pixel-correlation; ORB/SIFT geometry fallback',
            'original_boxes': normalized(image_boxes[0], original), 'suspect_boxes': normalized(image_boxes[1], suspect),
            'matches': matches, 'count': len(matches),
            'limitations': ['A matching photo does not prove ownership or impersonation.',
                            'Automatic regions target a light interface with a rectangular photo grid; check the highlighted regions.',
                            'Heavy cropping, borders and complex editing may hide a match.',
                            'Local feature geometry can flag shared visual detail; it does not establish who owns an image.']}
