from langs.language import get_language as get_language_x

def get_language(lang_name: str):
    import langs.a
    import langs.c
    import langs.wgsl
    return get_language_x(lang_name)
