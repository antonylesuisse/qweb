<?include("pyphp.php");pyphp_run("mywsgiapp");?>
# vim:syntax=python:

def mywsgiapp(environ, start_response):
	start_response('200 OK', [('Content-type','text/plain')])

	# access the php api via environ['php']
	ver = environ['php'].phpversion()

	return ['Hello world! via (php %s) \n'%ver]


