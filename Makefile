devserver:
	~/google_appengine/dev_appserver.py --use_sqlite --debug --address=0.0.0.0 .
devserverclear:
	~/google_appengine/dev_appserver.py --use_sqlite --debug --clear_datastore .
deploy:
	~/google_appengine/appcfg.py update .
