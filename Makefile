
%.PHONY: all
all: src/alang/langs/a_parser.py

src/alang/langs/a_parser.py: src/alang/langs/a.y src/alang/langs/py.skel Makefile
	@rm -f parser.py
	/opt/homebrew/opt/bison/bin/bison -S src/alang/langs/py.skel src/alang/langs/a.y -o a_parser.py
	@grep -v '^\s*#' a_parser.py > $@
	@rm -f a_parser.py

