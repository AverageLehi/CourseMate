"""Test icon loading functionality"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_icon_manager_import():
    """Test that IconManager can be imported"""
    try:
        from coursemate import IconManager, _icon_manager
        print("✓ IconManager imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import IconManager: {e}")
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
    """Test loading an icon with IconManager"""
    try:
        from coursemate import _icon_manager
        
        print("\nTesting icon loading...")
        icon = _icon_manager.load_icon("icon_home_24.png", "#000000", size=(20, 20))
        
        if icon is None:
            print("✗ Icon loaded but returned None")
            return False
        
        print(f"✓ Icon loaded successfully: {type(icon)}")
        print(f"  - PIL cache size: {len(_icon_manager._pil_cache)}")
        print(f"  - CTk cache size: {len(_icon_manager._ctk_cache)}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to load icon: {e}")
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
    results.append(("IconManager Import", test_icon_manager_import()))
    results.append(("Icon Files Exist", test_icon_files_exist()))
    results.append(("Icon Loading", test_icon_loading()))
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
