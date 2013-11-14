
all: package

package:
	python dartdoc2set.py
	echo 'VACUUM ANALYZE;' | sqlite3 dart.docset/Contents/Resources/docSet.dsidx
	tar --exclude='.DS_Store' -cvzf dart.tgz dart.docset

download:
	curl -O http://storage.googleapis.com/dart-archive/channels/stable/release/latest/api-docs/dart-api-docs.zip
	unzip dart-api-docs.zip
	rm -r dart.docset/Contents/Resources/Documents/
	mv api_docs/ dart.docset/Contents/Resources/
	mv dart.docset/Contents/Resources/api_docs/ dart.docset/Contents/Resources/Documents/
	touch dart.docset/Contents/Resources/Documents/.keep
