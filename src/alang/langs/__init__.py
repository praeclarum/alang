from langs.language import Language, get_language as get_language_x

def get_language(lang_name: str) -> Language:
    import langs.a
    import langs.c
    import langs.glsl
    import alang.langs.html_dev
    import langs.js
    import langs.metal
    import langs.wgsl
    return get_language_x(lang_name)
