from colorthief import ColorThief


def extract(image_path: str) -> dict:
    """Extract dominant color palette from the product image."""
    try:
        ct = ColorThief(image_path)
        dominant = ct.get_color(quality=1)
        palette = ct.get_palette(color_count=5, quality=1)

        def rgb_to_hex(rgb):
            return "#{:02x}{:02x}{:02x}".format(*rgb)

        return {
            "dominant": rgb_to_hex(dominant),
            "palette": [rgb_to_hex(c) for c in palette],
        }
    except Exception as e:
        return {
            "dominant": "#000000",
            "palette": [],
            "error": str(e),
        }
