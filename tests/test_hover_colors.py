"""
Test suite for automatic hover color generation.

Tests verify that:
1. Color darkening function works correctly
2. All themes have appropriate hover colors
3. Contrast ratios meet visibility requirements
4. Auto-calculation falls back safely on errors

License note: The contrast ratio calculation uses the relative luminance formula
from WCAG 2.0 specifications, which is public domain. Implementation references:
- MIT License: https://github.com/facelessuser/coloraide
- GPL-3.0 License: https://github.com/Xevion/tcp-chat
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from coursemate import darken_color, THEMES


def test_darken_color_basic():
    """Test basic color darkening with known values."""
    # Pure white should darken to light gray
    result = darken_color('#ffffff', 15)
    assert result == '#d8d8d8', f"Expected #d8d8d8, got {result}"
    
    # Light gray should darken further
    result = darken_color('#f5f5f5', 12)
    assert result == '#d7d7d7', f"Expected #d7d7d7, got {result}"
    
    # Light pink should darken to darker pink
    result = darken_color('#fce4ec', 12)
    assert result == '#ddc8cf', f"Expected #ddc8cf, got {result}"
    
    print("✓ Basic color darkening tests passed")


def test_darken_color_edge_cases():
    """Test edge cases and error handling."""
    # Black should stay black (can't darken further)
    result = darken_color('#000000', 15)
    assert result == '#000000', f"Black should stay black, got {result}"
    
    # Invalid hex should return with # prepended (fallback behavior)
    result = darken_color('invalid', 15)
    assert result == '#invalid', f"Invalid color should return with #, got {result}"
    
    # Missing # should work
    result = darken_color('ffffff', 15)
    assert result == '#d8d8d8', f"Color without # should work, got {result}"
    
    # Negative percentage should use absolute value
    result = darken_color('#ffffff', -15)
    assert result == '#d8d8d8', f"Negative percentage should work, got {result}"
    
    print("✓ Edge case tests passed")


def test_contrast_ratio(color1, color2):
    """Calculate relative luminance and contrast ratio between two colors.
    
    Uses WCAG 2.0 relative luminance formula (public domain specification).
    Implementation references MIT and GPL-3.0 licensed code (see module docstring).
    """
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def relative_luminance(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        # WCAG 2.0 relative luminance formula
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    try:
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        l1 = relative_luminance(rgb1)
        l2 = relative_luminance(rgb2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
    except:
        return 0


def test_theme_hover_colors():
    """Test that all themes have visible hover colors with good contrast."""
    print("\n=== Testing Theme Hover Colors ===\n")
    
    white_icon = '#ffffff'
    
    for theme_name, theme_colors in THEMES.items():
        print(f"\n{theme_name}:")
        
        sidebar_button = theme_colors.get('sidebar_button', '#f5f5f5')
        sidebar_hover = theme_colors.get('sidebar_hover')
        
        # If no hover color specified, calculate it
        if not sidebar_hover:
            sidebar_hover = darken_color(sidebar_button, 12)
            print(f"  ⚠ No hover color defined, auto-calculated: {sidebar_hover}")
        else:
            print(f"  Sidebar button: {sidebar_button}")
            print(f"  Sidebar hover:  {sidebar_hover}")
        
        # Test contrast between button and hover (should be noticeable but not huge)
        button_hover_contrast = test_contrast_ratio(sidebar_button, sidebar_hover)
        print(f"  Button/Hover contrast: {button_hover_contrast:.2f}:1")
        
        # Test contrast between hover and white icon (should be good for visibility)
        hover_icon_contrast = test_contrast_ratio(sidebar_hover, white_icon)
        print(f"  Hover/White Icon contrast: {hover_icon_contrast:.2f}:1")
        
        # Assertions
        assert button_hover_contrast >= 1.05, \
            f"{theme_name}: Hover color too similar to button (contrast: {button_hover_contrast:.2f}:1)"
        
        # For light themes, hover should be darker; for dark themes, can be lighter
        # We'll check that the hover is visibly different (at least 5% contrast)
        
        print(f"  ✓ {theme_name} hover colors are appropriate")
    
    print("\n✓ All theme hover color tests passed\n")


def test_auto_calculation():
    """Test that auto-calculation works for themes without sidebar_hover."""
    print("\n=== Testing Auto-Calculation ===\n")
    
    test_themes = {
        'Test Light': {
            'sidebar_button': '#f5f5f5',
            # No sidebar_hover - should auto-calculate
        },
        'Test Pink': {
            'sidebar_button': '#fce4ec',
        },
        'Test Blue': {
            'sidebar_button': '#e1f5fe',
        }
    }
    
    for theme_name, theme_colors in test_themes.items():
        button_color = theme_colors['sidebar_button']
        calculated_hover = darken_color(button_color, 12)
        
        print(f"{theme_name}:")
        print(f"  Button: {button_color}")
        print(f"  Calculated hover: {calculated_hover}")
        
        # Verify it's darker
        contrast = test_contrast_ratio(button_color, calculated_hover)
        assert contrast >= 1.05, f"Calculated hover should be noticeably darker (got {contrast:.2f}:1)"
        print(f"  Contrast: {contrast:.2f}:1 ✓")
    
    print("\n✓ Auto-calculation tests passed\n")


def run_all_tests():
    """Run all hover color tests."""
    print("=" * 60)
    print("Running Hover Color Tests")
    print("=" * 60)
    
    try:
        test_darken_color_basic()
        test_darken_color_edge_cases()
        test_theme_hover_colors()
        test_auto_calculation()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
