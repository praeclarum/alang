from language import Language, register_language

class ALanguage(Language):
    def __init__(self):
        super().__init__("alang")
        self.set_file_extension(".a")

    def get_run_command(self, file_path):
        return ["python3", file_path]

a_lang = ALanguage("alang")
register_language(a_lang)

