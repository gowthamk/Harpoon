SUBDIRS = api

info_TEXINFOS = hacking.texinfo vmintegration.texinfo

%.dvi : %.texinfo
	texi2dvi $<

%.ps : %.dvi
	dvips -o $@ $<

docs: hacking.ps vmintegration.ps
