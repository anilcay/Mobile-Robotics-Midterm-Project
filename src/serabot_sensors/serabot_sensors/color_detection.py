"""Red (ripe produce) detection on camera images, independent of ROS.

The colour_detector node converts each /camera/image_raw message to a BGR array,
calls `detect_red` and publishes the result. Contract (docs/INTERFACES.md 2.5):
the target's horizontal offset is in [-1, 1] with left negative, and its size is
the fraction of the image area it covers, in [0, 1].

Red wraps around the OpenCV hue circle (0..179), so the mask is the union of
two hue bands. Default thresholds come from frames of the greenhouse world:
tomatoes are H 0, S 245-255, V 101-228; the brown plant beds are H 13-15,
S ~140 (see docs/modules/sensor-camera.md).
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np

BOX_COLOR = (0, 255, 0)       # BGR, green box around the target
CENTER_COLOR = (255, 255, 0)  # BGR, image centre line
MASK_TINT = (255, 0, 255)     # BGR, other red pixels are tinted magenta


@dataclass
class ColorParams:
    """Detection thresholds; each field is also a ROS parameter of the node."""

    hue_low_max: int = 8           # red band 1: 0 .. hue_low_max
    hue_high_min: int = 170        # red band 2: hue_high_min .. 179
    saturation_min: int = 120
    value_min: int = 60
    morph_kernel: int = 5          # px; closing merges a truss of tomatoes into one blob
    min_area_ratio: float = 0.0005  # blobs smaller than this fraction are ignored


@dataclass(frozen=True)
class Detection:
    """Largest red blob in an image."""

    x: int              # bounding box, pixels
    y: int
    width: int
    height: int
    center_x: float     # blob centroid, pixels
    center_y: float
    area_ratio: float   # blob pixels / image pixels, [0, 1]
    offset: float       # horizontal offset of the centroid, [-1, 1], left negative


def red_mask(bgr: np.ndarray, p: ColorParams) -> np.ndarray:
    """Binary mask (uint8, 0/255) of red pixels, closed with a square kernel."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    low = cv2.inRange(hsv, (0, p.saturation_min, p.value_min),
                      (p.hue_low_max, 255, 255))
    high = cv2.inRange(hsv, (p.hue_high_min, p.saturation_min, p.value_min),
                       (179, 255, 255))
    mask = cv2.bitwise_or(low, high)
    if p.morph_kernel > 1:
        kernel = np.ones((p.morph_kernel, p.morph_kernel), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def horizontal_offset(center_x: float, width: int) -> float:
    """Map a pixel column to [-1, 1]: -1 left edge, 0 centre, +1 right edge."""
    half = width / 2.0
    return max(-1.0, min(1.0, (center_x - half) / half))


def largest_blob(mask: np.ndarray, p: ColorParams) -> Optional[Detection]:
    """Largest connected component of the mask, or None if it is too small."""
    count, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if count <= 1:  # label 0 is the background
        return None
    label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    height, width = mask.shape[:2]
    area_ratio = float(stats[label, cv2.CC_STAT_AREA]) / float(width * height)
    if area_ratio < p.min_area_ratio:
        return None
    cx, cy = (float(c) for c in centroids[label])
    return Detection(
        x=int(stats[label, cv2.CC_STAT_LEFT]),
        y=int(stats[label, cv2.CC_STAT_TOP]),
        width=int(stats[label, cv2.CC_STAT_WIDTH]),
        height=int(stats[label, cv2.CC_STAT_HEIGHT]),
        center_x=cx,
        center_y=cy,
        area_ratio=area_ratio,
        offset=horizontal_offset(cx, width),
    )


def detect_red(bgr: np.ndarray, p: ColorParams) -> Tuple[Optional[Detection], np.ndarray]:
    """Detect the largest red blob; returns the detection (or None) and the mask."""
    mask = red_mask(bgr, p)
    return largest_blob(mask, p), mask


def annotate(bgr: np.ndarray, mask: np.ndarray,
             detection: Optional[Detection]) -> np.ndarray:
    """Copy of the image with red pixels tinted, the target boxed and a status line."""
    out = bgr.copy()
    tinted = mask > 0
    out[tinted] = (0.5 * out[tinted] + 0.5 * np.array(MASK_TINT)).astype(np.uint8)
    height, width = out.shape[:2]
    cv2.line(out, (width // 2, 0), (width // 2, height - 1), CENTER_COLOR, 1)
    if detection is None:
        text = 'no target'
    else:
        d = detection
        cv2.rectangle(out, (d.x, d.y), (d.x + d.width - 1, d.y + d.height - 1), BOX_COLOR, 2)
        cv2.drawMarker(out, (int(round(d.center_x)), int(round(d.center_y))), BOX_COLOR,
                       cv2.MARKER_CROSS, 16, 2)
        text = f'target offset {d.offset:+.2f}  area {d.area_ratio * 100:.2f}%'
    cv2.putText(out, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4,
                cv2.LINE_AA)
    cv2.putText(out, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
                cv2.LINE_AA)
    return out
