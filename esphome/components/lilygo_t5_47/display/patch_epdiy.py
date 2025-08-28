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
                    
                    # Fix I2C driver conflicts - revert to legacy driver API
                    if 'i2c_master_bus_config_t' in content:
                        # Revert back to legacy I2C driver types
                        new_content = new_content.replace('i2c_master_bus_config_t', 'i2c_config_t')
                        needs_patch = True
                    
                    if 'i2c_new_master_bus' in content:
                        # Replace new I2C function calls with legacy ones
                        new_content = new_content.replace('i2c_new_master_bus', 'i2c_driver_install')
                        needs_patch = True
                    
                    # Clean up the broken function call that our previous patch may have created
                    if 'ESP_ERROR_CHECK(i2c_driver_install(EPDIY_I2C_PORT, I2C_MODE_MASTER, 0, 0, 0));' in content:
                        new_content = new_content.replace(
                            'ESP_ERROR_CHECK(i2c_driver_install(EPDIY_I2C_PORT, I2C_MODE_MASTER, 0, 0, 0));',
                            'ESP_ERROR_CHECK(i2c_driver_install(EPDIY_I2C_PORT, I2C_MODE_MASTER, 0, 0, 0));'
                        )
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