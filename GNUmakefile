JFLAGS=-g
JFLAGSVERB=-verbose -J-Djavac.pipe.output=true
JCC=javac -d .
JDOC=javadoc
JDOCFLAGS=-version -author # -package
JDOCIMAGES=/usr/local/jdk1.1.6/docs/api/images

ALLPKGS = $(shell find . -type d | grep -v CVS | grep -v "^./harpoon" | grep -v "^./doc" | sed -e "s|^[.]/*||")
ALLSOURCE = $(foreach dir, $(ALLPKGS), $(wildcard $(dir)/*.java))

all:	java

java:	$(ALLSOURCE)
#	${JCC} ${JFLAGS} `javamake.sh */*.java`
#	${JCC} ${JFLAGS} ${JFLAGSVERB} `javamake.sh $(ALLSOURCE)` | \
#		egrep -v '^\[[lc]'
	${JCC} ${JFLAGS} ${JFLAGSVERB} $(ALLSOURCE) | \
		egrep -v '^\[[lc]'
	touch java

cvs-add:
	-for dir in $(filter-out Test,$(ALLPKGS)); do \
		(cd $$dir; cvs add *.java 2>/dev/null); \
	done
cvs-commit: cvs-add
	cvs commit
commit: cvs-commit # convenient abbreviation

doc:	doc/TIMESTAMP

doc/TIMESTAMP:	$(ALLSOURCE)
	make doc-clean
	mkdir doc
	cd doc; ln -s .. harpoon
	cd doc; ${JDOC} ${JDOCFLAGS} -d . \
		$(foreach dir, $(filter-out Test,$(ALLPKGS)), \
			  harpoon.$(subst /,.,$(dir)))
	$(RM) doc/harpoon
	munge doc | \
	  sed -e 's/<cananian@/\&lt;cananian@/g' \
	      -e 's/princeton.edu>/princeton.edu\&gt;/g' \
	      -e 's/<dd> "The,/<dd> /g' > doc-tmp
	unmunge doc-tmp; $(RM) doc-tmp
	cd doc; ln -s $(JDOCIMAGES) images
	cd doc; ln -s packages.html index.html
	cd doc; ln -s index.html API_users_guide.html
	date '+%-d-%b-%Y at %r %Z.' > doc/TIMESTAMP
	chmod a+rx doc doc/*

doc-install: doc/TIMESTAMP
	ssh miris.lcs.mit.edu /bin/rm -rf public_html/Projects/Harpoon/doc
	scp -r doc miris.lcs.mit.edu:public_html/Projects/Harpoon

doc-clean:
	-${RM} -r doc

wc:
	@wc -l $(ALLSOURCE)
	@echo Top Five:
	@wc -l $(ALLSOURCE) | sort -n | tail -6 | head -5

clean:
	-${RM} java
	-${RM} -r harpoon

polish: clean
	-${RM} *~ [A-Z][a-z]*/*.java~

wipe:	clean doc-clean

backup:
	$(RM) ../harpoon-backup.tar.gz
	cd ..; tar czf harpoon-backup.tar.gz CVSROOT
	scp ../harpoon-backup.tar.gz \
		miris.lcs.mit.edu:public_html/Projects/Harpoon
	$(RM) ../harpoon-backup.tar.gz
