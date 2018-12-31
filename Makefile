PREFIX = /usr/local

.PHONY: install
install:
	mkdir -p $(DESTDIR)$(PREFIX)/bin
	cp twelite.py $(DESTDIR)$(PREFIX)/bin/twelite.py
	cp twelite.service /etc/systemd/system/twelite.service
	systemctl daemon-reload
	systemctl restart twelite
