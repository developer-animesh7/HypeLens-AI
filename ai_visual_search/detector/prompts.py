"""
Optimized GroundingDINO prompts for fashion detection.
Strategy: Multi-phrase descriptive prompts with color, style, and gender cues.
"""

# OPTIMIZED FASHION PROMPT - Multi-phrase descriptive strategy
# GroundingDINO needs visual context (color + style + gender), not just single words
FASHION_PROMPT = (
    "men shirt . long sleeve shirt . full sleeve shirt . button shirt . cotton shirt . "
    "brown shirt . collar shirt . casual shirt . beige shirt . formal shirt . "
    "pants . black pants . formal pants . men's trousers . dark pants . cargo pants . "
    "watch . wrist watch . men's watch . analog watch . bracelet watch . "
    "sunglasses . eyeglasses . men's sunglasses . black sunglasses . "
    "shoes . men's shoes . loafers . casual shoes . brown shoes . "
    "jacket . blazer . coat . "
    "bag . backpack . handbag"
)

# Detection thresholds optimized for clothing with subtle edges
BOX_THRESHOLD = 0.18  # Lower for detecting clothes with wrinkles/low contrast
TEXT_THRESHOLD = 0.18  # Lower for better clothing detection
MAX_DETECTIONS = 25
