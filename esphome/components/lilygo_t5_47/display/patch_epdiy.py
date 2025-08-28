#!/usr/bin/env python3
"""
PlatformIO post-build script to patch epdiy library files
Replaces rom/miniz.h includes with miniz.h for ESP-IDF 5.x compatibility
"""

Import("env")
import os
import glob

def patch_epdiy_files():
    """Patch epdiy library files to replace rom/miniz.h with miniz.h"""
    
    print("Patching epdiy library for ESP-IDF 5.x compatibility...")
    
    # Get the library dependencies directory
    libdeps_dir = env.get("PROJECT_LIBDEPS_DIR")
    if not libdeps_dir:
        print("Warning: Could not find libdeps directory")
        return
    
    # Find all epdiy-related directories
    epdiy_patterns = [
        os.path.join(libdeps_dir, "*/epdiy/**/*.c"),
        os.path.join(libdeps_dir, "*/epdiy/**/*.h"),
    ]
    
    files_patched = 0
    
    for pattern in epdiy_patterns:
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file contains problematic includes or I2C driver issues
                    needs_patch = False
                    new_content = content
                    
                    # Fix rom/miniz.h includes
                    if 'rom/miniz.h' in content:
                        new_content = new_content.replace('#include "rom/miniz.h"', '#include "miniz.h"')
                        new_content = new_content.replace('#include <rom/miniz.h>', '#include <miniz.h>')
                        needs_patch = True
                    
                    # Fix I2C driver conflicts - replace old driver includes with new ones
                    if '#include "driver/i2c.h"' in content:
                        # Replace old I2C driver include with new one
                        new_content = new_content.replace('#include "driver/i2c.h"', '#include "driver/i2c_master.h"')
                        needs_patch = True
                    
                    # Also check for old I2C function calls and update them
                    if 'i2c_driver_install' in content or 'i2c_config_t' in content:
                        # Replace old I2C API calls with new ones
                        new_content = new_content.replace('i2c_driver_install', 'i2c_new_master_bus')
                        new_content = new_content.replace('i2c_config_t', 'i2c_master_bus_config_t')
                        new_content = new_content.replace('i2c_master_start', 'i2c_master_bus_reset')
                        needs_patch = True
                    
                    if needs_patch:
                        # Write the patched content back
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"  Patched: {file_path}")
                        files_patched += 1
                        
                except Exception as e:
                    print(f"  Error patching {file_path}: {e}")
    
    if files_patched > 0:
        print(f"Successfully patched {files_patched} files")
    else:
        print("No files needed patching")

# Execute the patching function
patch_epdiy_files()