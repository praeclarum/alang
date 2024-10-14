from typing import Optional

def open_writer(out: str, language: Optional[str] = None, options: Optional["CodeOptions"] = None): # type: ignore
    from alang.langs import get_language
    lang = get_language(language)
    return lang.open_writer(out, options)

if __name__ == "__main__":
    pass
