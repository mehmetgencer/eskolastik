devserver:
	~/google_appengine/dev_appserver.py  .
	#~/google_appengine/dev_appserver.py --use_sqlite --debug --address=0.0.0.0 .
devserverclear:
	~/google_appengine/dev_appserver.py --use_sqlite --debug --clear_datastore .
deploy:
	~/google_appengine/appcfg.py update .
docs:
	~/.cabal/bin/pandoc -s --toc -o static/help/help.html static/help/help.md
