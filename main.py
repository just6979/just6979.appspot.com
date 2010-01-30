

import os
import sys
import time
import traceback
import wsgiref

import cgi
import Cookie

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import journal


class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.out.write(
                'Hello %s <a href="%s">Sign out</a><br>Is administrator: %s' % 
                (user.nickname(), users.create_logout_url("/"), users.is_current_user_admin())
            )
        else:
            self.redirect(users.create_login_url(self.request.uri))
#application = webapp.WSGIApplication([('/', MainPage)], debug=True)


base_dir = os.path.dirname(__file__)
template_dir = os.path.join(base_dir, 'templates')
content_dir = os.path.join(base_dir, 'content')

# datestamp for HTTP headers: LastModified, Expires
http_date_stamp = '%a, %d %b %Y %H:%M:%S GMT'
# datestamp for cookies
cookie_date_stamp = '%a, %d-%b-%Y %H:%M:%S GMT'

def application(environ, start_response):
	try:
		status, headers, output = page_handler(environ)
		start_response(status, headers)
		return output
	except:
		status = '200 OK'
		headers = []
		headers.append(('Content-Type', 'text/plain'))
		output = ['-!-ERROR-!-\n\n']
		output.append(traceback.format_exc())
		for name, val in headers:
			output.append('\n%s is %s\n' % (name, val))
		start_response(status, headers)
		return output

def redirect(referer, headers):
	status='302 Found'
	headers.append(('Location', referer))
	return status, headers, ''

def page_handler(environ):
	status = '200 OK'
	headers = []

	now = time.time()
	# set Date: header. helps caches syncronize (i think)
	headers.append(('Date', time.strftime(http_date_stamp, time.gmtime(now))))
	headers.append(('Expires', time.strftime(http_date_stamp, time.gmtime(now))))

	# save the referer for possible redirects
	referer = environ.get('HTTP_REFERER', '')

	# cookie time!
	cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE', ''))
	if not cookies.has_key('user'):
		cookies['user'] = ''
	user = cookies['user'].value
	if cookies.has_key('session'):
		session = cookies['session']
	else:
		session = False

	# parse CGI form data
	form = cgi.FieldStorage(environ=environ)
	op = form.getfirst('op', 'display').lower()

	if op == 'login':
		expire_time = time.strftime(cookie_date_stamp, time.gmtime(now + 7 * 24 * 60 * 60))
		# get user from the form, or use the cookie, or the default ''
		user_name = form.getfirst('user', user)
		password = form.getfirst('password', '')
		if user_name:
			found_user = ''
			found_md5 = ''
			cookies['user'] = user_name
			cookies['user']['expires'] = expire_time
			headers.append(('Set-Cookie', cookies['user'].output().split(':')[1]))
			passwd_file = file(os.path.join(base_dir, '.htpasswd'))
			for line in passwd_file:
				found_user, found_md5 = line.rstrip().split(':')
				if found_user == user_name:
					break
			if found_md5 == password:
				cookies['session'] = now
				cookies['session']['expires'] = expire_time
				headers.append(('Set-Cookie', cookies['session'].output().split(':')[1]))
		return redirect(referer, headers)

	elif op == 'logout':
		# clear user and session cookies for a new login
		expire_time = time.strftime(cookie_date_stamp, time.gmtime(now - 7 * 24 * 60 * 60))
		cookies['user'] = 'user'
		cookies['user']['expires'] = expire_time
		headers.append(('Set-Cookie', cookies['user'].output().split(':')[1]))
		cookies['session'] = 'session'
		cookies['session']['expires'] = expire_time
		headers.append(('Set-Cookie', cookies['session'].output().split(':')[1]))
		return redirect(referer, headers)

	elif op == 'dump':
		page = form.getfirst('p', os.path.basename(__file__))
		page_file = os.path.join(base_dir, page)
		try:
			filedata = file(page_file, 'r')
		except IOError:
			page_file = os.path.join(base_dir, os.path.basename(__file__))
			filedata = file(page_file, 'r')
		else:
			pass
	else:
		page = form.getfirst('p', 'tinfoil')
		if page == 'journal':
			page_file = os.path.join(base_dir, 'journal.py')
			j = journal.Journal(
				form,
				user_cookie,
				session_cookie,
				templateLoader
			)
			content = j.dispatch()
		else:
			# try to open the requested page .htf file
			try:
				page_file = os.path.join(content_dir, page + '.htf')
				content = file(page_file, 'r')
			# if not, use tinfoil.htf. if it's not there we got bigger probs
			except IOError:
				page = 'tinfoil'
				page_file = os.path.join(content_dir, page + '.htf')
				content = file(page_file, 'r')
		title = page.capitalize()

	# MS Internet Explorer (<= 7) doesn't understand application/xhtml+xml
	# If the request came from MSIE (<= 7), then use text/html instead
	agent = environ.get('HTTP_USER_AGENT', '')
	if 'MSIE' in agent:
		headers.append(('Content-type', 'text/html; charset=utf-8'))
	else:
		headers.append(('Content-type', 'application/xhtml+xml; charset=utf-8'))

	# get file modification times
	mod_time = os.stat(page_file)[8]
	# and format a nice HTTP style datestamp
	pretty_mod_time = time.strftime(http_date_stamp, time.gmtime(mod_time))
	# and send it to the client
	headers.append(('LastModified', pretty_mod_time))

	# load the template
	template_file = 'main.html'
	path = os.path.join(template_dir, template_file)
	values = {
		'title': title,
		'user': user,
		'session': session,
		'page': page,
		'content': content,
		'page_file': os.path.basename(page_file),
		'mod_time': pretty_mod_time,
	}
	# show it off!
	return status, headers, template.render(path, values)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
