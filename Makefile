
all: package

package:
	echo 'VACUUM ANALYZE;' | sqlite3 dart.docset/Contents/Resources/docSet.dsidx
	tar --exclude='.DS_Store' -cvzf dart.tgz dart.docset