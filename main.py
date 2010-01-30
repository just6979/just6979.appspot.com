# -*- coding: utf-8 -*-
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
		req = self.request
		env = req.environ
		hdrs = req.headers
		res = self.response

		base_dir = os.path.dirname(__file__)
		template_dir = os.path.join(base_dir, 'templates')
		content_dir = os.path.join(base_dir, 'content')

		# datestamp for HTTP headers: LastModified, Expires
		http_date_stamp = '%a, %d %b %Y %H:%M:%S GMT'
		# datestamp for cookies
		cookie_date_stamp = '%a, %d-%b-%Y %H:%M:%S GMT'

		user = users.get_current_user()
		if not user:
			user = ''

		now = time.time()
		res.headers['Expires'] = time.strftime(http_date_stamp, time.gmtime(now))

		# save the referer for possible redirects
		referer = env.get('HTTP_REFERER', '')

		# parse CGI form data
		form = cgi.FieldStorage(environ=env)
		op = form.getfirst('op', 'display').lower()

		if op == 'dump':
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
					user,
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
		agent = env.get('HTTP_USER_AGENT', '')
		if 'MSIE' in agent:
			res.headers['Content-type'] = 'text/html; charset=utf-8'
		else:
			res.headers['Content-type'] = 'application/xhtml+xml; charset=utf-8'

		# get file modification times
		mod_time = os.stat(page_file)[8]
		# and format a nice HTTP style datestamp
		pretty_mod_time = time.strftime(http_date_stamp, time.gmtime(mod_time))
		# and send it to the client
		res.headers['LastModified'] = pretty_mod_time

		# load the template
		template_file = 'main.html'
		path = os.path.join(template_dir, template_file)
		values = {
			'title': title,
			'user': user,
			'page': page,
			'content': content,
			'page_file': os.path.basename(page_file),
			'mod_time': pretty_mod_time,
		}
		# show it off!
		res.out.write(template.render(path, values))


class LoginPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			self.redirect(self.request.uri)
		else:
			self.redirect(users.create_login_url(self.request.referrer))


class LogoutPage(webapp.RequestHandler):
	def get(self):
		self.redirect(users.create_logout_url(self.request.referrer))

class MercurialPage(webapp.RequestHandler):
	def get(self):
		self.redirect('http://just6979.hg.sourceforge.net/hgweb/just6979/just6979/')


application = webapp.WSGIApplication([
	('/', MainPage),
	('/login', LoginPage),
	('/logout', LogoutPage),
	('/hg', MercurialPage),
], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
