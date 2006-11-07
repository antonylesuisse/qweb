<?include("pyphp.php");pyphp_run("test_app");?>
# vim:syntax=python:

import cgi, time

def test_app(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/html')])

	# php proxy
	php=environ['php']

	# calling a php function
	php.header("Content-Type: text/html")

	yield '''<html><head><title>Hello World!</title></head>
	<body><p>Hello World!</p>
	<br/>
	<form action="demo_wsgi2.php" method="GET">
	<input type="text" name="a" value="test value"/>
	<input type="submit" name="s" value="submit"/>
	</form>
	<br/>
	<br/>
	'''

	# printing from python
	print "Hello from python time is ", time.ctime(), "<br><br>"

	# access php $_GET array
	print "php._GET acessible as python dict:", php._GET ,"<br><br>"

	# use a php function
	print "php exlode ", php.explode("/","/file/path/example"), "<br><br>"

	# use the php function eval()
	php.eval("print_r(array());")

	# use php sessions
	if not "count" in php._SESSION:
		php._SESSION["count"]=1
	else:
		count=php._SESSION["count"]

	print "session: count,",count, "<br><br>"
	php._SESSION["count"]=count+1

	# use php mysql api
	print "Try to list mysql users this wont work if root has a mysql password<br><br>"

	php.mysql_connect(':/var/run/mysqld/mysqld.sock','root')
	php.mysql_select_db('mysql')

	q=php.mysql_query('select User from user LIMIT 0,10')

	while 1:
		r=php.mysql_fetch_assoc(q)
		if not r: break
		print r, '<br>'


