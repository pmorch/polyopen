ECHO=@

default:
	@echo No default target - see Makefile
	exit 1

tidy:
	@echo Tidying code
	$(ECHO) hatch run python-tidy:black .
	$(ECHO) hatch run python-tidy:isort .
	$(ECHO) find src -name '*.py' | \
		hatch run python-tidy:xargs hatch run autoflake --in-place --remove-unused-variables