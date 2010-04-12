# -*- coding: utf-8 -*-
import os
import sys
import time
import traceback
import wsgiref

import cgi
import Cookie

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Page(db.Model):
	title = db.StringProperty(required=True)
	author = db.UserProperty(required=True)
	type = db.StringProperty(required=True)
	content = db.TextProperty(required=True)

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		admin = users.is_current_user_admin()

		form = cgi.FieldStorage(environ=self.request.environ)

		op = form.getfirst('op', 'display').lower()

		edit = ''
		if op == 'edit':
			edit = 'edit'
			op = 'display'

		if op == 'display':
			page = form.getfirst('p', 'home')
			content_dir = 'content'
			try:
				page_file = os.path.join(content_dir, page + '.htf')
				content = file(page_file, 'r')
			except IOError:
				page = 'home'
				page_file = os.path.join(content_dir, page + '.htf')
				content = file(page_file, 'r')

			title = page.capitalize()

			path = 'templates/main.html'
			values = {
				'title': title,
				'page': page,
				'content': content.readlines(),
				'user': user,
				'admin': admin,
				'edit': edit,
				'datetime': None,
			}

			self.response.out.write(template.render(path, values))

class LoginPage(webapp.RequestHandler):
	def get(self):
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
