"""Tests for the ROS-free red detection used by color_detector."""

import cv2
import numpy as np
import pytest
from serabot_sensors.color_detection import (
    annotate, ColorParams, detect_red, horizontal_offset, red_mask)

WIDTH, HEIGHT = 640, 480

# HSV (OpenCV ranges) of surfaces measured in the greenhouse world.
TOMATO = (0, 255, 150)
BED_BROWN = (14, 140, 87)
LEAF_GREEN = (53, 200, 120)
FLOOR_GREY = (0, 0, 180)


def scene(background=FLOOR_GREY) -> np.ndarray:
    """BGR image filled with one HSV colour."""
    hsv = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
    hsv[:] = background
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def paint(bgr: np.ndarray, hsv_color, x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    """Fill the box [x0, x1) x [y0, y1) with an HSV colour."""
    patch = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
    patch[:] = hsv_color
    bgr[y0:y1, x0:x1] = cv2.cvtColor(patch, cv2.COLOR_HSV2BGR)
    return bgr


@pytest.fixture
def params() -> ColorParams:
    return ColorParams()


def test_no_red_no_target(params):
    img = paint(scene(), LEAF_GREEN, 0, 0, WIDTH, 200)
    detection, mask = detect_red(img, params)
    assert detection is None
    assert mask.sum() == 0


def test_brown_bed_is_not_red(params):
    img = paint(scene(), BED_BROWN, 0, 240, WIDTH, HEIGHT)
    detection, _ = detect_red(img, params)
    assert detection is None


def test_target_on_left_has_negative_offset(params):
    img = paint(scene(), TOMATO, 40, 200, 120, 260)
    detection, _ = detect_red(img, params)
    assert detection is not None
    assert detection.offset < -0.5
    assert detection.center_x == pytest.approx(79.5, abs=0.5)


def test_target_on_right_has_positive_offset(params):
    img = paint(scene(), TOMATO, 520, 200, 600, 260)
    detection, _ = detect_red(img, params)
    assert detection is not None
    assert detection.offset > 0.5


def test_centered_target_has_zero_offset(params):
    img = paint(scene(), TOMATO, 300, 220, 340, 260)
    detection, _ = detect_red(img, params)
    assert detection is not None
    assert detection.offset == pytest.approx(0.0, abs=0.01)


def test_area_ratio_and_box(params):
    img = paint(scene(), TOMATO, 100, 100, 164, 148)  # 64 x 48 px = 1 % of the image
    detection, _ = detect_red(img, params)
    assert detection is not None
    assert detection.area_ratio == pytest.approx(0.01, rel=0.01)
    assert (detection.x, detection.y, detection.width, detection.height) == (100, 100, 64, 48)


def test_largest_blob_wins(params):
    img = scene()
    paint(img, TOMATO, 20, 20, 40, 40)        # small, left
    paint(img, TOMATO, 500, 300, 580, 380)    # large, right
    detection, _ = detect_red(img, params)
    assert detection is not None
    assert detection.offset > 0.0


def test_hue_wraps_around(params):
    img = paint(scene(), (175, 230, 150), 300, 200, 360, 260)
    detection, _ = detect_red(img, params)
    assert detection is not None


def test_dark_or_pale_red_is_rejected(params):
    img = scene()
    paint(img, (0, 255, params.value_min - 10), 50, 50, 150, 150)       # too dark
    paint(img, (0, params.saturation_min - 20, 200), 300, 50, 400, 150)  # too pale
    detection, _ = detect_red(img, params)
    assert detection is None


def test_tiny_blob_is_ignored(params):
    img = paint(scene(), TOMATO, 300, 200, 305, 205)  # 25 px << 0.05 % of the image
    detection, _ = detect_red(img, params)
    assert detection is None


def test_closing_merges_a_truss(params):
    img = scene()
    for x in (200, 214, 228):  # three tomatoes 2 px apart
        paint(img, TOMATO, x, 200, x + 12, 212)
    detection, mask = detect_red(img, params)
    assert detection is not None
    assert (detection.x, detection.width) == (200, 40)
    assert red_mask(img, ColorParams(morph_kernel=1)).sum() < mask.sum()


def test_horizontal_offset_range():
    assert horizontal_offset(0, WIDTH) == -1.0
    assert horizontal_offset(WIDTH / 2, WIDTH) == 0.0
    assert horizontal_offset(WIDTH, WIDTH) == 1.0
    assert horizontal_offset(WIDTH + 50, WIDTH) == 1.0


def test_annotate_keeps_input_and_shape(params):
    img = paint(scene(), TOMATO, 100, 100, 200, 200)
    original = img.copy()
    detection, mask = detect_red(img, params)
    out = annotate(img, mask, detection)
    assert out.shape == img.shape
    assert np.array_equal(img, original)
    assert not np.array_equal(out, img)
    assert annotate(img, mask, None).shape == img.shape
