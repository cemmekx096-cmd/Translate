# Mod System - mod_system.rpy
# File ini menampilkan tombol "mod" di pojok atas dan menu bahasa
# Compatible with Ren'Py 8.0.3

# Definisi variabel untuk menyimpan bahasa yang dipilih
default persistent.selected_language = "english"

# Style untuk tombol mod
style mod_button:
    background None
    hover_background "#333333"
    padding (10, 5)

style mod_button_text:
    size 20
    color "#ffffff"
    hover_color "#ffff00"

# Style untuk menu mod
style mod_menu_frame:
    background "#000000"
    padding (20, 20)
    xalign 0.5
    yalign 0.5

style mod_menu_text:
    color "#ffffff"
    size 24
    text_align 0.5

style mod_menu_button:
    background "#333333"
    hover_background "#555555"
    padding (15, 10)
    margin (5, 5)

style mod_menu_button_text:
    color "#ffffff"
    hover_color "#ffff00"
    size 20
    text_align 0.5

# Screen untuk menampilkan tombol mod di pojok atas
screen mod_overlay():
    # Tombol mod di pojok kanan atas
    textbutton "mod":
        style "mod_button"
        text_style "mod_button_text"
        xalign 1.0
        yalign 0.0
        xoffset -10
        yoffset 10
        action Show("mod_menu")

# Screen untuk menu mod dengan background hitam
screen mod_menu():
    # Background hitam transparan
    add "#000000"
    
    # Frame utama menu
    frame:
        style "mod_menu_frame"
        has vbox
        spacing 20
        
        # Judul menu
        text "MOD MENU" style "mod_menu_text" size 30
        
        null height 20
        
        # Bagian pemilihan bahasa
        text "Pilih Bahasa / Select Language:" style "mod_menu_text"
        
        null height 10
        
        # Tombol bahasa Inggris
        textbutton "English (Original)":
            style "mod_menu_button"
            text_style "mod_menu_button_text"
            action [
                SetVariable("persistent.selected_language", "english"),
                Function(set_language, "english"),
                Hide("mod_menu")
            ]
        
        # Tombol bahasa Indonesia
        textbutton "Bahasa Indonesia":
            style "mod_menu_button"
            text_style "mod_menu_button_text"
            action [
                SetVariable("persistent.selected_language", "indonesia"),
                Function(set_language, "indonesia"),
                Hide("mod_menu")
            ]
        
        null height 30
        
        # Tombol kembali
        textbutton "Tutup / Close":
            style "mod_menu_button"
            text_style "mod_menu_button_text"
            action Hide("mod_menu")

# Fungsi untuk mengatur bahasa
init python:
    def set_language(lang):
        if lang == "indonesia":
            # Mengaktifkan terjemahan Indonesia dari folder tl/id
            renpy.change_language("id")
        else:
            # Kembali ke bahasa asli (Inggris)
            renpy.change_language(None)

# Label untuk inisialisasi mod
label start_mod_system:
    # Menampilkan overlay mod di semua screen
    $ renpy.show_screen("mod_overlay")
    return

# Auto-load overlay mod saat game dimulai
label after_load:
    $ renpy.show_screen("mod_overlay")
    return

# Pastikan overlay mod muncul saat game dimulai
label start:
    # Tampilkan overlay mod
    call start_mod_system
    
    # Lanjutkan ke script game utama Anda
    # jump main_story  # Uncomment dan ganti dengan label utama game Anda
    
    return

# Contoh implementasi untuk game utama (opsional)
label main_story:
    "Ini adalah contoh teks game."
    "Tombol 'mod' akan selalu terlihat di pojok kanan atas."
    "Klik untuk mengakses menu bahasa!"
    return