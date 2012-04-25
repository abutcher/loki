NAME := Django-loki
VERSION := $(word 2,$(shell grep Version *.spec))
SDIST := $(NAME)-$(VERSION)
SOURCES := $(shell echo ~/rpmbuild/SOURCES)
TMPDIR := $(shell mktemp -d)
TARGET := $(TMPDIR)/$(SDIST)
RESULT := $(TARGET).tar.gz
SPEC := $(NAME).spec

clean:
	rm -fR out_src/*

version:
	@echo $(VERSION)

sdist:
	mkdir -p $(TARGET)
	cp -r . $(TARGET)
	tar -C $(TMPDIR) -czf $(RESULT) $(SDIST)
	mv $(RESULT) $(CURDIR)

rpm: sdist
	mkdir -p $(SOURCES)
	mv $(SDIST).tar.gz $(SOURCES)
	rpmbuild-md5 -bs $(SPEC)
