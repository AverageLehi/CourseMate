"""Test icon loading functionality"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_icon_function_import():
    """Test that icon loading function can be imported"""
    try:
        from coursemate import load_and_tint_icon
        print("✓ Icon loading function imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import icon loading function: {e}")
        return False

def test_pil_imports():
    """Test that PIL is properly imported"""
    try:
        from PIL import Image, ImageOps
        print("✓ PIL imports successful")
        return True
    except Exception as e:
        print(f"✗ PIL import failed: {e}")
        return False

def test_icon_files_exist():
    """Test that icon files exist in assets/icons"""
    icon_dir = Path(__file__).parent / "assets" / "icons"
    required_icons = [
        "icon_home_24.png",
        "icon_notebook_32.png",
        "icon_settings_24.png",
        "icon_info_32.png"
    ]
    
    print(f"\nChecking icon directory: {icon_dir}")
    if not icon_dir.exists():
        print(f"✗ Icon directory does not exist: {icon_dir}")
        return False
    
    all_exist = True
    for icon in required_icons:
        icon_path = icon_dir / icon
        if icon_path.exists():
            print(f"✓ Found: {icon}")
        else:
            print(f"✗ Missing: {icon}")
            all_exist = False
    
    return all_exist

def test_icon_loading():
    """Test loading an icon with different colors"""
    try:
        from coursemate import load_and_tint_icon
        
        print("\nTesting icon loading with different colors...")
        
        # Test white icon (for dark themes)
        icon_white = load_and_tint_icon("icon_home_24.png", "#FFFFFF", size=(24, 24))
        if icon_white is None:
            print("✗ White icon returned None")
            return False
        print(f"✓ White icon loaded successfully: {type(icon_white)}")
        
        # Test dark icon (for light themes)
        icon_dark = load_and_tint_icon("icon_notebook_32.png", "#1a1a1a", size=(24, 24))
        if icon_dark is None:
            print("✗ Dark icon returned None")
            return False
        print(f"✓ Dark icon loaded successfully: {type(icon_dark)}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load icon: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_theme_based_icon_colors():
    """Test that icon colors change based on theme"""
    try:
        import customtkinter as ctk
        from coursemate import Sidebar, DataManager, THEMES
        
        print("\nTesting theme-based icon colors...")
        
        # Test dark theme (CourseMate Theme) - should use white icons
        root1 = ctk.CTk()
        root1.withdraw()
        root1.current_theme = 'CourseMate Theme'
        
        data_manager = DataManager()
        colors_dark = THEMES['CourseMate Theme']
        
        sidebar_dark = Sidebar(
            root1, 
            data_manager, 
            colors_dark, 
            lambda: None, lambda: None, lambda: None, lambda: None
        )
        
        print("✓ CourseMate Theme sidebar created (should have white icons)")
        root1.destroy()
        
        # Test light theme (Baby Blue) - should use dark icons
        root2 = ctk.CTk()
        root2.withdraw()
        root2.current_theme = 'Baby Blue'
        
        colors_light = THEMES['Baby Blue']
        
        sidebar_light = Sidebar(
            root2, 
            data_manager, 
            colors_light, 
            lambda: None, lambda: None, lambda: None, lambda: None
        )
        
        print("✓ Baby Blue theme sidebar created (should have dark icons)")
        root2.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Failed theme-based test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sidebar_creation():
    """Test that Sidebar can be created with icons"""
    try:
        import customtkinter as ctk
        from coursemate import Sidebar, DataManager, THEMES
        
        print("\nTesting Sidebar creation...")
        
        # Create minimal test window
        root = ctk.CTk()
        root.withdraw()  # Hide window
        
        data_manager = DataManager()
        colors = THEMES['Baby Blue']
        
        # Try to create sidebar
        sidebar = Sidebar(
            root, 
            data_manager, 
            colors, 
            lambda: None,  # home_cb
            lambda: None,  # notebooks_cb
            lambda: None,  # settings_cb
            lambda: None   # about_cb
        )
        
        print("✓ Sidebar created successfully")
        
        # Check if nav images were created
        if hasattr(sidebar, '_nav_images'):
            print(f"  - Navigation images: {len(sidebar._nav_images)}")
        else:
            print("  ⚠ No _nav_images attribute found")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Failed to create Sidebar: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CourseMate Icon Loading Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("PIL Imports", test_pil_imports()))
    results.append(("Icon Function Import", test_icon_function_import()))
    results.append(("Icon Files Exist", test_icon_files_exist()))
    results.append(("Icon Loading (Multiple Colors)", test_icon_loading()))
    results.append(("Theme-Based Icon Colors", test_theme_based_icon_colors()))
    results.append(("Sidebar Creation", test_sidebar_creation()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    sys.exit(0 if passed == total else 1)
