from language import Language, register_language

class ALang(Language):
    def __init__(self):
        super().__init__("alang")
        self.set_file_extension(".a")

    def get_run_command(self, file_path):
        return ["python3", file_path]

a_lang = ALang("alang")
register_language(a_lang)

