#/usr/bin/python

def testapp(environ, start_response):
	start_response('200 OK',[('Content-type','text/plain')])
	php=environ['php']

	if 'PHP_AUTH_USER' not in php._SERVER:
		php.header('WWW-Authenticate: Basic realm="My Realm"')
		php.header('HTTP/1.0 401 Unauthorized')
		print 'Text to send if user hits Cancel button';
		php.exit()
	else:
		print "<p>Hello '%s'.</p>"%(php._SERVER['PHP_AUTH_USER'],)
		print "<p>You entered '%s' as your password.</p>"%(php._SERVER['PHP_AUTH_PW'])

	return ['done\n']

