import os
import sys

def replace_text_in_file(file_path, search_text, replace_text):
    """
    Fungsi untuk mencari dan mengganti teks dalam file
    
    Args:
        file_path (str): Path ke file target
        search_text (str): Teks yang dicari
        replace_text (str): Teks pengganti
    
    Returns:
        tuple: (jumlah_perubahan, output_file_path)
    """
    
    # Validasi file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' tidak ditemukan!")
        return 0, None
    
    # Ambil nama file dan ekstensi
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    name, ext = os.path.splitext(file_name)
    
    # Buat nama file output
    output_file = os.path.join(file_dir, f"{name}_edit{ext}")
    
    try:
        # Baca file dengan encoding yang aman
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"Error: Tidak bisa membaca file '{file_path}' dengan encoding yang didukung!")
            return 0, None
        
        print(f"File berhasil dibaca dengan encoding: {used_encoding}")
        print(f"Ukuran file: {len(content)} karakter")
        
        # Hitung jumlah kemunculan teks target sebelum penggantian
        count_before = content.count(search_text)
        print(f"Ditemukan '{search_text}': {count_before} kali")
        
        if count_before == 0:
            print(f"Teks '{search_text}' tidak ditemukan dalam file!")
            return 0, None
        
        # Lakukan penggantian teks
        new_content = content.replace(search_text, replace_text)
        
        # Verifikasi penggantian berhasil
        count_after = new_content.count(search_text)
        count_replaced = new_content.count(replace_text)
        
        print(f"Proses penggantian:")
        print(f"  - '{search_text}' tersisa: {count_after}")
        print(f"  - '{replace_text}' sekarang ada: {count_replaced}")
        print(f"  - Total yang diganti: {count_before - count_after}")
        
        # Tulis ke file baru
        with open(output_file, 'w', encoding=used_encoding) as f:
            f.write(new_content)
        
        print(f"File baru berhasil dibuat: {output_file}")
        print(f"Ukuran file baru: {len(new_content)} karakter")
        
        # Verifikasi integritas file
        if len(content) - len(new_content) == (count_before * (len(search_text) - len(replace_text))):
            print("✓ Integritas file terjaga - hanya teks target yang berubah")
        else:
            print("⚠ Warning: Ada perubahan ukuran yang tidak terduga")
        
        return count_before - count_after, output_file
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 0, None

# ===========================================
# KONFIGURASI MULTI TARGET - EDIT BAGIAN INI
# ===========================================

# Opsi 1: Multi file dengan replacement yang sama
MULTI_FILES = [
    "file1.rpy",
    "file2.rpy", 
    "x-common_id_restored.rpy"
]
SEARCH_TEXT = "translate english"
REPLACE_TEXT = "translate id"

# Opsi 2: Auto scan semua file .rpy
AUTO_SCAN_CONFIG = {
    "file_extension": ".rpy",  # Ekstensi file yang dicari
    "search": "translate english",
    "replace": "translate id",
    "include_subdirectories": True,  # Scan subfolder juga
    "exclude_folders": ["backup", "temp", "__pycache__"],  # Folder yang diabaikan
    "min_file_size": 0,  # Ukuran minimum file (bytes)
    "max_file_size": 10485760  # Ukuran maksimum file (10MB)
}

# Opsi 3: Multiple replacements dalam satu file
SINGLE_FILE_MULTI_REPLACE = {
    "file": "x-common_id_restored.rpy",
    "replacements": [
        {"search": "translate english", "replace": "translate id"},
        {"search": "old_function", "replace": "new_function"},
        {"search": "version 1.0", "replace": "version 2.0"}
    ]
}

# ===========================================

def process_multi_files_same_replacement():
    """Proses multiple files dengan replacement yang sama"""
    print("=== MODE: MULTI FILES - SAME REPLACEMENT ===\n")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    total_changes = 0
    processed_files = []
    
    for filename in MULTI_FILES:
        file_path = os.path.join(script_dir, filename)
        
        print(f"\n📁 Processing: {filename}")
        print("-" * 40)
        
        changes, output_file = replace_text_in_file(file_path, SEARCH_TEXT, REPLACE_TEXT)
        
        if changes > 0:
            total_changes += changes
            processed_files.append((filename, changes, output_file))
        
        print("-" * 40)
    
    print(f"\n🎯 RINGKASAN PROSES:")
    print(f"Total files diproses: {len(MULTI_FILES)}")
    print(f"Files berhasil diubah: {len(processed_files)}")
    print(f"Total perubahan: {total_changes}")
    
    if processed_files:
        print(f"\n📋 DETAIL FILES:")
        for filename, changes, output in processed_files:
            print(f"  ✓ {filename}: {changes} perubahan → {os.path.basename(output)}")

def scan_and_process_files():
    """Auto scan dan proses semua file dengan ekstensi tertentu"""
    print("=== MODE: AUTO SCAN & PROCESS ===\n")
    
    config = AUTO_SCAN_CONFIG
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"🔍 Scanning untuk file: *{config['file_extension']}")
    print(f"📁 Direktori: {script_dir}")
    print(f"📂 Include subdirectories: {config['include_subdirectories']}")
    print(f"🚫 Exclude folders: {config['exclude_folders']}")
    print(f"🔍 Search: '{config['search']}'")
    print(f"🔄 Replace: '{config['replace']}'")
    print("-" * 60)
    
    # Cari semua file yang sesuai
    found_files = []
    
    if config['include_subdirectories']:
        # Scan rekursif
        for root, dirs, files in os.walk(script_dir):
            # Hapus folder yang dikecualikan dari pencarian
            dirs[:] = [d for d in dirs if d not in config['exclude_folders']]
            
            for file in files:
                if file.endswith(config['file_extension']):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, script_dir)
                    
                    # Cek ukuran file
                    try:
                        file_size = os.path.getsize(file_path)
                        if config['min_file_size'] <= file_size <= config['max_file_size']:
                            found_files.append((file_path, relative_path, file_size))
                    except OSError:
                        continue
    else:
        # Scan hanya di direktori script
        for file in os.listdir(script_dir):
            if file.endswith(config['file_extension']):
                file_path = os.path.join(script_dir, file)
                if os.path.isfile(file_path):
                    try:
                        file_size = os.path.getsize(file_path)
                        if config['min_file_size'] <= file_size <= config['max_file_size']:
                            found_files.append((file_path, file, file_size))
                    except OSError:
                        continue
    
    print(f"📊 HASIL SCANNING:")
    print(f"Total file ditemukan: {len(found_files)}")
    
    if not found_files:
        print(f"❌ Tidak ada file *{config['file_extension']} yang ditemukan!")
        return
    
    # Tampilkan daftar file
    print(f"\n📋 DAFTAR FILE:")
    for i, (file_path, relative_path, file_size) in enumerate(found_files, 1):
        size_kb = file_size / 1024
        print(f"  {i}. {relative_path} ({size_kb:.1f} KB)")
    
    # Konfirmasi proses
    print(f"\n⚠️  AKAN MEMPROSES {len(found_files)} FILES:")
    print(f"   Search: '{config['search']}'")
    print(f"   Replace: '{config['replace']}'")
    
    try:
        confirm = input("\nLanjutkan? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', 'ya']:
            print("❌ Proses dibatalkan")
            return
    except KeyboardInterrupt:
        print("\n❌ Proses dibatalkan")
        return
    
    print("\n" + "="*60)
    print("🚀 MEMULAI PROSES...")
    print("="*60)
    
    # Proses semua file
    total_changes = 0
    processed_files = []
    failed_files = []
    
    for i, (file_path, relative_path, file_size) in enumerate(found_files, 1):
        print(f"\n📁 [{i}/{len(found_files)}] Processing: {relative_path}")
        print("-" * 50)
        
        try:
            changes, output_file = replace_text_in_file(file_path, config['search'], config['replace'])
            
            if changes > 0:
                total_changes += changes
                processed_files.append((relative_path, changes, output_file))
                print(f"✅ Berhasil: {changes} perubahan")
            else:
                print(f"⚪ Tidak ada perubahan")
                
        except Exception as e:
            failed_files.append((relative_path, str(e)))
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)
    
    # Ringkasan hasil
    print(f"\n🎯 RINGKASAN AUTO SCAN & PROCESS:")
    print("="*60)
    print(f"📊 Total files scanned: {len(found_files)}")
    print(f"✅ Files berhasil diproses: {len(processed_files)}")
    print(f"❌ Files gagal: {len(failed_files)}")
    print(f"🔄 Total perubahan: {total_changes}")
    
    if processed_files:
        print(f"\n📋 FILES YANG BERHASIL:")
        for relative_path, changes, output_file in processed_files:
            output_name = os.path.basename(output_file) if output_file else "N/A"
            print(f"  ✅ {relative_path}: {changes} perubahan → {output_name}")
    
    if failed_files:
        print(f"\n❌ FILES YANG GAGAL:")
        for relative_path, error in failed_files:
            print(f"  ❌ {relative_path}: {error}")
    
    # Opsi buka folder hasil
    if processed_files:
        try:
            open_folder = input(f"\n📂 Buka folder hasil? (y/n): ").strip().lower()
            if open_folder in ['y', 'yes', 'ya']:
                os.system(f'explorer "{script_dir}"' if os.name == 'nt' else f'open "{script_dir}"')
        except KeyboardInterrupt:
            pass

def process_single_file_multi_replace():
    """Proses satu file dengan multiple replacements"""
    print("=== MODE: SINGLE FILE - MULTI REPLACEMENTS ===\n")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, SINGLE_FILE_MULTI_REPLACE["file"])
    
    # Validasi file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{SINGLE_FILE_MULTI_REPLACE['file']}' tidak ditemukan!")
        return
    
    # Baca file sekali
    try:
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"Error: Tidak bisa membaca file!")
            return
        
        original_content = content
        total_changes = 0
        replacement_log = []
        
        print(f"📁 File: {SINGLE_FILE_MULTI_REPLACE['file']}")
        print(f"📊 Ukuran awal: {len(content)} karakter")
        print(f"🔧 Encoding: {used_encoding}")
        print(f"🔄 Replacements: {len(SINGLE_FILE_MULTI_REPLACE['replacements'])}")
        print("-" * 50)
        
        # Lakukan semua replacements secara berurutan
        for i, replacement in enumerate(SINGLE_FILE_MULTI_REPLACE["replacements"], 1):
            search = replacement["search"]
            replace = replacement["replace"]
            
            count_before = content.count(search)
            print(f"\n{i}. '{search}' → '{replace}'")
            print(f"   Ditemukan: {count_before} kali")
            
            if count_before > 0:
                content = content.replace(search, replace)
                count_after = content.count(search)
                changes = count_before - count_after
                total_changes += changes
                replacement_log.append((search, replace, changes))
                print(f"   ✓ Diganti: {changes} kali")
            else:
                print(f"   ⚠ Tidak ditemukan")
        
        # Simpan hasil
        if total_changes > 0:
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            name, ext = os.path.splitext(file_name)
            output_file = os.path.join(file_dir, f"{name}_multi_edit{ext}")
            
            with open(output_file, 'w', encoding=used_encoding) as f:
                f.write(content)
            
            print("-" * 50)
            print(f"🎯 RINGKASAN:")
            print(f"Total perubahan: {total_changes}")
            print(f"Ukuran akhir: {len(content)} karakter")
            print(f"File output: {output_file}")
            
            print(f"\n📋 LOG REPLACEMENTS:")
            for search, replace, changes in replacement_log:
                print(f"  ✓ '{search}' → '{replace}': {changes}x")
        else:
            print("\n❌ Tidak ada perubahan yang dibuat")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def show_multi_menu():
    """Menu untuk memilih mode multi processing"""
    print("\n" + "="*60)
    print("PILIH MODE MULTI PROCESSING:")
    print("="*60)
    print("1. 🔍 Auto Scan & Process")
    print("   └─ Scan otomatis semua file .rpy dan proses")
    print("2. 📁 Multi Files - Same Replacement")
    print("   └─ Beberapa file, replacement sama")
    print("3. 📄 Single File - Multi Replacements")
    print("   └─ Satu file, beberapa replacement")
    print("4. ⚙️  Lihat konfigurasi saat ini")
    print("5. 🚪 Kembali ke menu utama")
    print("="*60)
    return input("Pilih mode (1-5): ").strip()

def show_current_config():
    """Menampilkan konfigurasi yang sedang aktif"""
    print("\n" + "="*60)
    print("KONFIGURASI MULTI TARGET SAAT INI:")
    print("="*60)
    
    print("\n1. AUTO SCAN & PROCESS:")
    config = AUTO_SCAN_CONFIG
    print(f"   File extension: {config['file_extension']}")
    print(f"   Search: '{config['search']}'")
    print(f"   Replace: '{config['replace']}'")
    print(f"   Include subdirectories: {config['include_subdirectories']}")
    print(f"   Exclude folders: {config['exclude_folders']}")
    print(f"   File size range: {config['min_file_size']} - {config['max_file_size']} bytes")
    
    print("\n2. MULTI FILES (Same Replacement):")
    print(f"   Files: {MULTI_FILES}")
    print(f"   Search: '{SEARCH_TEXT}'")
    print(f"   Replace: '{REPLACE_TEXT}'")
    
    print("\n3. SINGLE FILE MULTI REPLACE:")
    print(f"   File: {SINGLE_FILE_MULTI_REPLACE['file']}")
    print(f"   Replacements:")
    for i, repl in enumerate(SINGLE_FILE_MULTI_REPLACE['replacements'], 1):
        print(f"     {i}. '{repl['search']}' → '{repl['replace']}'")

def main_multi():
    """Main function untuk multi processing"""
    print("🚀 SCRIPT MULTI TARGET TEXT REPLACEMENT")
    print("Mendukung multiple files dan multiple replacements")
    
    while True:
        choice = show_multi_menu()
        
        if choice == "1":
            scan_and_process_files()
            break
        elif choice == "2":
            process_multi_files_same_replacement()
            break
        elif choice == "3":
            process_single_file_multi_replace()
            break
        elif choice == "4":
            show_current_config()
        elif choice == "5":
            print("Kembali ke menu utama...")
            break
        else:
            print("❌ Pilihan tidak valid!")

# Fungsi utilitas lainnya (sama seperti script asli)
def get_supported_formats():
    """Menampilkan format file yang didukung"""
    formats = {
        'Text Files': ['.txt', '.log', '.md', '.rst', '.ini', '.cfg', '.conf'],
        'Code Files': ['.py', '.js', '.html', '.css', '.xml', '.json', '.yaml', '.yml'],
        'Data Files': ['.csv', '.tsv', '.sql', '.bat', '.sh'],
        'Config Files': ['.properties', '.env', '.gitignore', '.htaccess'],
        'Document Files': ['.rtf', '.tex', '.bib'],
        'Other Text': ['.sub', '.srt', '.vtt', '.m3u', '.pls']
    }
    
    print("FORMAT FILE YANG DIDUKUNG:")
    print("=" * 40)
    for category, extensions in formats.items():
        print(f"{category}:")
        print(f"  {', '.join(extensions)}")
    print("\n⚠ CATATAN:")
    print("- Semua file berbasis teks (text-based) didukung")
    print("- File binary (gambar, video, exe) TIDAK didukung")  
    print("- Encoding: UTF-8, UTF-8-BOM, Latin-1, CP1252")
    print("=" * 40)

def create_demo_files():
    """Membuat beberapa file demo untuk testing multi target"""
    
    # Demo file 1
    demo1 = """# Demo File 1
translate english "Hello World"
translate english "Welcome"
old_function()
version 1.0"""
    
    # Demo file 2  
    demo2 = """# Demo File 2
translate english "Good Morning"
translate english "Good Night"
another_old_function()
version 1.0"""
    
    # Demo file 3
    demo3 = """# Config Demo
debug=false
translate english "Error Message"
old_setting=true
version 1.0"""
    
    files = [
        ("demo1.rpy", demo1),
        ("demo2.rpy", demo2), 
        ("config_demo.ini", demo3)
    ]
    
    for filename, content in files:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ File demo '{filename}' berhasil dibuat")
    
    print("\n🎯 File demo siap untuk testing multi target!")

def show_main_menu():
    """Menu utama"""
    print("\n" + "="*60)
    print("MENU UTAMA:")
    print("="*60)
    print("1. 🎯 Multi Target Processing")
    print("2. 📋 Lihat format file yang didukung")
    print("3. 🧪 Buat file demo untuk testing")
    print("4. ⚙️  Lihat konfigurasi multi target")
    print("5. 🚪 Keluar")
    print("="*60)
    return input("Pilih menu (1-5): ").strip()

if __name__ == "__main__":
    print("🔥 ADVANCED MULTI TARGET TEXT REPLACEMENT SCRIPT")
    print("Mendukung berbagai mode multi processing")
    
    while True:
        choice = show_main_menu()
        
        if choice == "1":
            main_multi()
        elif choice == "2":
            get_supported_formats()
        elif choice == "3":
            create_demo_files()
        elif choice == "4":
            show_current_config()
        elif choice == "5":
            print("👋 Selesai. Terima kasih!")
            break
        else:
            print("❌ Pilihan tidak valid!")
            
        input("\nTekan Enter untuk melanjutkan...")