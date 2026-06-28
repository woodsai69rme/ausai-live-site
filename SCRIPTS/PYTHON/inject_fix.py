"""
AUGGDASH26 Dashboard System - Fix Injector
This script injects the necessary JavaScript fixes into the existing index.html file
to restore dashboard functionality.
"""

import os
import re

def inject_javascript_fix():
    """Inject the JavaScript fix into the index.html file"""
    index_path = "C:/Users/karma/auggdash26/index.html"
    backup_path = "C:/Users/karma/auggdash26/index.html.backup"
    
    # Read the dashboard_fix.js content
    with open("C:/Users/karma/dashboard_fix.js", "r", encoding="utf-8") as js_file:
        js_content = js_file.read()
    
    # Create the script tag
    script_tag = f"""
<script>
// AUGGDASH26 Dashboard System - JavaScript Fix
// Injected to restore dashboard functionality
{js_content}
</script>
"""
    
    # Read the original index.html file
    with open(index_path, "r", encoding="utf-8") as index_file:
        original_content = index_file.read()
    
    # Create a backup
    with open(backup_path, "w", encoding="utf-8") as backup_file:
        backup_file.write(original_content)
    
    print(f"Backup created: {backup_path}")
    
    # Check if the script is already injected
    if "// AUGGDASH26 Dashboard System - JavaScript Fix" in original_content:
        print("JavaScript fix is already present in the index.html file.")
        return False
    
    # Find the closing </body> tag and insert the script before it
    if "</body>" in original_content:
        # Insert the script before the closing body tag
        fixed_content = original_content.replace("</body>", script_tag + "\n</body>")
    else:
        # If no body tag found, append to the end of the file
        fixed_content = original_content + script_tag
    
    # Write the fixed content back to the file
    with open(index_path, "w", encoding="utf-8") as index_file:
        index_file.write(fixed_content)
    
    print(f"JavaScript fix successfully injected into {index_path}")
    print("Dashboard functionality should now be restored.")
    return True

def verify_fix():
    """Verify that the fix was applied correctly"""
    index_path = "C:/Users/karma/auggdash26/index.html"
    
    with open(index_path, "r", encoding="utf-8") as index_file:
        content = index_file.read()
    
    # Check for required functions
    required_functions = [
        "openDashboard",
        "openFolder", 
        "searchDashboards",
        "toggleCategory"
    ]
    
    print("\nVerifying dashboard functionality:")
    all_present = True
    
    for func in required_functions:
        if f"function {func}" in content or f"window.{func}" in content:
            print(f"  [OK] {func} function found")
        else:
            print(f"  [MISSING] {func} function missing")
            all_present = False

    # Check for event handlers
    if "onclick=" in content:
        print("  [OK] onclick handlers found")
    else:
        print("  [WARNING] onclick handlers not found")

    # Check for search functionality
    if "searchDashboards" in content and "searchInput" in content:
        print("  [OK] Search functionality found")
    else:
        print("  [MISSING] Search functionality missing")

    if all_present:
        print("\n[SUCCESS] Dashboard system fix verification: PASSED")
        print("The dashboard should now be functional.")
    else:
        print("\n[ERROR] Dashboard system fix verification: FAILED")
        print("Some functionality may still be missing.")
    
    return all_present

if __name__ == "__main__":
    print("AUGGDASH26 Dashboard System - Fix Injector")
    print("="*50)
    
    # Inject the fix
    success = inject_javascript_fix()
    
    if success:
        print("\nFix injection completed successfully!")
        print("Verifying the fix...")
        verify_fix()
        
        print("\n" + "="*50)
        print("INSTRUCTIONS:")
        print("1. Open your browser and navigate to the index.html file")
        print("2. The dashboard categories should now be expandable")
        print("3. Search functionality should work")
        print("4. Dashboard links should be clickable")
        print("5. If issues persist, press F12 to open developer tools")
        print("   and check the Console tab for any error messages")
    else:
        print("\nFix was already present or failed to inject.")
        print("Verifying existing functionality...")
        verify_fix()