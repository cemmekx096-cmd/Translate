## Konfigurasi bahasa - TAMBAHAN BARU UNTUK MULTI-LANGUAGE
define config.language = None
define gui.language = "english"
define config.translate_clean_stores = ["gui", "config"]

## Daftar bahasa yang tersedia
define config.languages = {
    None: "English",
    "id": "Bahasa Indonesia"
}

## Persistent data untuk menyimpan pilihan bahasa
default persistent.language = None













define config.name = _("")

define config.layers = [ 'master', 'transient', 'screens', 'overlay', 'buttonlayer']




define gui.show_name = True




define config.version = "       Chapter 2 v0.9.9.1 EP20(VN)"





define gui.about = _p("""
""")






define build.name = "AnnaExcitingAffectionCH2VN"







define config.has_sound = True
define config.has_music = True
define config.has_voice = True













define config.main_menu_music = "audio/Me2.mp3"










define config.enter_transition = dissolve
define config.exit_transition = dissolve

define config.end_splash_transition = Dissolve(1)



define config.intra_transition = dissolve




define config.after_load_transition = dissolve




define config.end_game_transition = dissolve
















define config.window = "auto"
define config.window_title = "Anna: Exciting Affection Chapter 2 (VN)"



define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)







default preferences.text_cps = 0





default preferences.afm_time = 15
















define config.save_directory = "AnnaExcitingAffectionVNstyle-1627980905"






define config.window_icon = "gui/window_icon.png"






init python:
    ## Fungsi untuk mengubah bahasa - TAMBAHAN BARU
    def change_game_language(lang):
        persistent.language = lang
        if lang == "id":
            renpy.change_language("id")
        else:
            renpy.change_language(None)
        renpy.restart_interaction()
    
    # Mengatur bahasa saat game dimulai berdasarkan persistent data
    def setup_language():
        if persistent.language == "id":
            renpy.change_language("id")
        elif persistent.language is None or persistent.language == "en":
            renpy.change_language(None)
    
    # Jalankan setup bahasa saat game dimulai
    setup_language()




















    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)



    build.classify("game/**.rpy", "scripts")
    build.classify("game/**.rpyc", "scripts")


    build.classify("game/**.jpg", "images")
    build.classify("game/**.png", "images")

    build.archive("scripts", "all")
    build.archive("images", "all")







    build.documentation('*.html')
    build.documentation('*.txt')
    build.directory_name = "AEAC2VN"
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc