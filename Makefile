
PREFIX ?= /usr
LOCAL_PREFIX ?= /usr/local
DESTDIR ?=

OPLY_DIR := $(DESTDIR)$(LOCAL_PREFIX)/Oply
BIN_DIR  := $(DESTDIR)$(LOCAL_PREFIX)/bin
APP_DIR  := $(DESTDIR)$(PREFIX)/share/applications

INSTALL := install
PYTHON  := /usr/bin/env python3

.PHONY: install uninstall

install:
	$(INSTALL) -d "$(OPLY_DIR)" "$(OPLY_DIR)/icons" "$(OPLY_DIR)/bin" "$(BIN_DIR)" "$(APP_DIR)"
	$(INSTALL) -m 0755 oply/Oply.py "$(OPLY_DIR)/Oply.py"
	$(INSTALL) -m 0755 oply/Oply-Video.py "$(OPLY_DIR)/Oply-Video.py"
	$(INSTALL) -m 0755 oply/Oply-Convert "$(OPLY_DIR)/Oply-Convert"
	$(INSTALL) -m 0755 oply/gksu "$(OPLY_DIR)/gksu"
	$(INSTALL) -m 0644 oply/icons/oply.svg "$(OPLY_DIR)/icons/oply.svg"
	$(INSTALL) -m 0644 oply/icons/gksu.svg "$(OPLY_DIR)/icons/gksu.svg"

	$(INSTALL) -m 0644 desktop/Oply.desktop "$(APP_DIR)/Oply.desktop"
	$(INSTALL) -m 0644 desktop/Oply-video.desktop "$(APP_DIR)/Oply-video.desktop"
	$(INSTALL) -m 0644 desktop/Oply-Convert.desktop "$(APP_DIR)/Oply-Convert.desktop"

	$(INSTALL) -m 0755 tools/oply_status.py "$(BIN_DIR)/oply_status.py"

	# CLI launchers
	printf '%s\n' '#!/bin/sh' 'exec $(PYTHON) "$(LOCAL_PREFIX)/Oply/Oply.py" "$$@"' > "$(BIN_DIR)/oply"
	chmod 0755 "$(BIN_DIR)/oply"
	printf '%s\n' '#!/bin/sh' 'exec $(PYTHON) "$(LOCAL_PREFIX)/Oply/Oply-Video.py" "$$@"' > "$(BIN_DIR)/oply-video"
	chmod 0755 "$(BIN_DIR)/oply-video"
	printf '%s\n' '#!/bin/sh' 'exec $(PYTHON) "$(LOCAL_PREFIX)/Oply/Oply-Convert" "$$@"' > "$(BIN_DIR)/oply-convert"
	chmod 0755 "$(BIN_DIR)/oply-convert"

uninstall:
	rm -f "$(APP_DIR)/Oply.desktop" "$(APP_DIR)/Oply-video.desktop" "$(APP_DIR)/Oply-Convert.desktop"
	rm -f "$(BIN_DIR)/oply_status.py" "$(BIN_DIR)/oply" "$(BIN_DIR)/oply-video" "$(BIN_DIR)/oply-convert"
	rm -rf "$(OPLY_DIR)"
