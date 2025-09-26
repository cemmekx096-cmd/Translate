## File options.rpy untuk Ren'Py 8.0.3 dengan dukungan multi-bahasa

define config.name = _("Anna: Exciting Affection Chapter 2")

define config.layers = ['master', 'transient', 'screens', 'overlay', 'buttonlayer']

define gui.show_name = True

define config.version = "Chapter 2 v0.9.9.1 EP20(VN)"

define gui.about = _p("""
Game Anna: Exciting Affection Chapter 2 (Visual Novel)
""")

define build.name = "AnnaExcitingAffectionCH2VN"

## Audio
define config.has_sound = True
define config.has_music = True  
define config.has_voice = True

define config.main_menu_music = "audio/Me2.mp3"

## Transisi
define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.end_splash_transition = Dissolve(1)
define config.intra_transition = dissolve
define config.after_load_transition = dissolve
define config.end_game_transition = dissolve

## Window
define config.window = "auto"
define config.window_title = "Anna: Exciting Affection Chapter 2 (VN)"
define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)

## Text preferences
default preferences.text_cps = 0
default preferences.afm_time = 15

## Save directory
define config.save_directory = "AnnaExcitingAffectionVNstyle-1627980905"

## Window icon
define config.window_icon = "gui/window_icon.png"

## Konfigurasi bahasa untuk Ren'Py 8.0.3
define config.translate_clean_stores = ["gui"]

## Bahasa yang tersedia (jangan definisikan gui.language)
## Ren'Py akan otomatis menggunakan bahasa default (None/English)

init python:
    ## Fungsi untuk mengubah bahasa
    def set_language(lang):
        if lang is None:
            renpy.change_language(None)
        else:
            renpy.change_language(lang)
        
        # Simpan pengaturan bahasa
        renpy.save_persistent() 
        
        # Restart interface untuk menerapkan perubahan
        renpy.restart_interaction()
        
        # Refresh layar
        renpy.full_restart()

    ## Fungsi untuk mendapatkan bahasa saat ini
    def get_current_language():
        return renpy.get_language() or "english"

    ## Build configuration
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

## Persistent language setting
default persistent.language = None

## Set bahasa saat startup jika sudah tersimpan
init python:
    if persistent.language:
        renpy.change_language(persistent.language)

## Label untuk inisialisasi bahasa
label after_load:
    if persistent.language:
        $ renpy.change_language(persistent.language)
    return

## Screen language selector (opsional - bisa ditambahkan ke preferences)
screen language_selection():
    modal True
    
    frame:
        style_prefix "confirm"
        
        vbox:
            spacing 30
            
            label _("Select Language") style "confirm_prompt"
            
            hbox:
                spacing 100
                
                textbutton _("English"):
                    action [
                        SetVariable("persistent.language", None),
                        Function(set_language, None)
                    ]
                    
                textbutton _("Bahasa Indonesia"):
                    action [
                        SetVariable("persistent.language", "id"), 
                        Function(set_language, "id")
                    ]