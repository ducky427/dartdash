
all: package

package:
	tar --exclude='.DS_Store' -cvzf dart.tgz dart.docset