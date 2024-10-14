# from alang.langs.language import Language, get_language as get_language_x

def get_language(lang_name: str) -> "Language": # type: ignore
    import alang.langs.html_dev
    import alang.langs.a
    import alang.langs.c
    import alang.langs.glsl
    import alang.langs.js
    import alang.langs.metal
    import alang.langs.wgsl
    import alang.langs.language
    return alang.langs.language.get_language(lang_name)
