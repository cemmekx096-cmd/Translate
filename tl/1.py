#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILE ORGANIZER - Pindahkan file ke folder grup_1-8
Otomatis buat folder dan pindahkan file sesuai grup
"""

import os
import shutil
from pathlib import Path

# Definisi grup file
FILE_GROUPS = {
    "grup_1": [
        "x-Episode_19.rpy",
        "x-bareventone.rpy", 
        "x-annasofficeevents.rpy",
        "x-barlogicgate.rpy",
        "x-bathroom.rpy",
        "x-bedroom.rpy"
    ],
    "grup_2": [
        "x-Episode_13.rpy",
        "x-Episode_17.rpy",
        "x-makecoffee.rpy",
        "x-taxmaneventone.rpy",
        "x-strangerevents.rpy"
    ],
    "grup_3": [
        "x-Episode_12.rpy",
        "x-Episode_18.rpy",
        "x-alfredevents.rpy",
        "x-alfredeventtwo.rpy",
        "x-annasofficeevents.rpy"
    ],
    "grup_4": [
        "x-Episode_15.rpy",
        "x-Episode_20.rpy",
        "x-episodeone.rpy",
        "x-jeremyhomeeventone.rpy",
        "x-jeremyeventtwo.rpy"
    ],
    "grup_5": [
        "x-Episode_16.rpy",
        "x-Episode_14.rpy",
        "x-Episode_10.rpy",
        "x-schmidteventtwo.rpy",
        "x-schmidteventthree.rpy"
    ],
    "grup_6": [
        "x-Episode_11.rpy",
        "x-Episode_9.5.rpy",
        "x-Episode_9.rpy",
        "x-annaofficeeventone.rpy",
        "x-annaofficeeventonea.rpy",
        "x-ashleyeventone.rpy",
        "x-dilaneventtwo.rpy"
    ],
    "grup_7": [
        "x-dilaneventone.rpy",
        "x-haroldevents.rpy",
        "x-hospitaleventone.rpy",
        "x-jeremyeventone.rpy",
        "x-jeremyeventtwo.rpy",
        "x-jeremyhomeeventone.rpy",
        "x-precinct.rpy",
        "x-carleventone.rpy"
    ],
    "grup_8": [
        "x-sergeyeventone.rpy",
        "x-taxmaneventone.rpy",
        "x-timothyeventtwo.rpy",
        "x-johnevents.rpy",
        "x-johneventthree.rpy",
        "x-earleventone.rpy",
        "x-earleventthree.rpy",
        "x-earleventtwo.rpy"
    ]
}

def create_folders():
    """Buat folder grup_1 sampai grup_8"""
    created_folders = []
    for grup_name in FILE_GROUPS.keys():
        if not os.path.exists(grup_name):
            os.makedirs(grup_name)
            created_folders.append(grup_name)
            print(f"📁 Created folder: {grup_name}")
        else:
            print(f"📁 Folder already exists: {grup_name}")
    return created_folders

def scan_current_directory():
    """Scan file .rpy di direktori saat ini"""
    current_dir = Path(".")
    rpy_files = list(current_dir.glob("*.rpy"))
    print(f"🔍 Found {len(rpy_files)} .rpy files in current directory")
    return [f.name for f in rpy_files]

def organize_files():
    """Pindahkan file ke folder grup yang sesuai"""
    # Buat folder terlebih dahulu
    created_folders = create_folders()
    
    # Scan file yang ada
    available_files = scan_current_directory()
    
    moved_files = []
    missing_files = []
    duplicate_files = []
    
    print(f"\n🚀 Starting file organization...")
    print("="*60)
    
    for grup_name, file_list in FILE_GROUPS.items():
        print(f"\n📂 Processing {grup_name.upper()}:")
        
        for filename in file_list:
            if filename in available_files:
                source_path = filename
                dest_path = os.path.join(grup_name, filename)
                
                # Cek apakah file sudah ada di tujuan
                if os.path.exists(dest_path):
                    print(f"   ⚠️  {filename} already exists in {grup_name}")
                    duplicate_files.append((filename, grup_name))
                    continue
                
                try:
                    shutil.move(source_path, dest_path)
                    moved_files.append((filename, grup_name))
                    print(f"   ✅ {filename} → {grup_name}/")
                except Exception as e:
                    print(f"   ❌ Failed to move {filename}: {e}")
            else:
                missing_files.append((filename, grup_name))
                print(f"   ⚠️  {filename} not found in current directory")
    
    # Summary
    print(f"\n" + "="*60)
    print("📊 ORGANIZATION SUMMARY")
    print("="*60)
    print(f"✅ Successfully moved: {len(moved_files)} files")
    print(f"⚠️  Missing files: {len(missing_files)} files")
    print(f"🔄 Duplicate files: {len(duplicate_files)} files")
    
    if moved_files:
        print(f"\n🎉 Successfully moved files:")
        for filename, grup in moved_files:
            print(f"   ✅ {filename} → {grup}/")
    
    if missing_files:
        print(f"\n⚠️ Missing files (not found in current directory):")
        for filename, grup in missing_files:
            print(f"   ❌ {filename} (should be in {grup})")
    
    if duplicate_files:
        print(f"\n🔄 Files that already exist in destination:")
        for filename, grup in duplicate_files:
            print(f"   ⚠️  {filename} (already in {grup})")
    
    # Tampilkan isi setiap folder
    print(f"\n📁 FOLDER CONTENTS:")
    print("="*60)
    for grup_name in FILE_GROUPS.keys():
        if os.path.exists(grup_name):
            files_in_folder = [f for f in os.listdir(grup_name) if f.endswith('.rpy')]
            print(f"{grup_name}: {len(files_in_folder)} files")
            for f in sorted(files_in_folder):
                print(f"   📄 {f}")
        else:
            print(f"{grup_name}: folder not found")
        print()

def verify_organization():
    """Verifikasi bahwa semua file sudah di tempat yang benar"""
    print(f"\n🔍 VERIFICATION:")
    print("="*60)
    
    all_good = True
    
    for grup_name, expected_files in FILE_GROUPS.items():
        if not os.path.exists(grup_name):
            print(f"❌ Folder {grup_name} does not exist!")
            all_good = False
            continue
            
        actual_files = [f for f in os.listdir(grup_name) if f.endswith('.rpy')]
        
        missing_in_folder = set(expected_files) - set(actual_files)
        extra_in_folder = set(actual_files) - set(expected_files)
        
        if missing_in_folder or extra_in_folder:
            print(f"⚠️  {grup_name}:")
            if missing_in_folder:
                print(f"   Missing: {list(missing_in_folder)}")
            if extra_in_folder:
                print(f"   Extra: {list(extra_in_folder)}")
            all_good = False
        else:
            print(f"✅ {grup_name}: OK ({len(actual_files)} files)")
    
    if all_good:
        print(f"\n🎉 All files are properly organized!")
    else:
        print(f"\n⚠️  Some issues found, please check above")

def main():
    print("="*60)
    print("📁 FILE ORGANIZER - GRUP 1-8")
    print("🎯 Organize .rpy files into grup_1 through grup_8 folders")
    print("="*60)
    
    try:
        organize_files()
        verify_organization()
        
        print(f"\n🏁 Organization completed!")
        print(f"📂 Files are now organized in grup_1 through grup_8 folders")
        print(f"🚀 Ready for batch translation!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")

if __name__ == "__main__":
    main()