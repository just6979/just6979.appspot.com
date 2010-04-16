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
	datetime = db.DateTimeProperty(required=True)
	title = db.StringProperty(required=True)
	author = db.UserProperty(required=True)
	content = db.TextProperty(required=True)
	tags = db.StringProperty()

class SinglePage(webapp.RequestHandler):
	def get(self, page):
		user = users.get_current_user()
		admin = users.is_current_user_admin()

		content_dir = 'content'
		try:
			page_file = os.path.join(content_dir, page + '.htf')
			content = file(page_file, 'r')
		except IOError:
			page = 'home'
			page_file = os.path.join(content_dir, page + '.htf')
			content = file(page_file, 'r')

		title = page.capitalize()

		path = 'html/main.html'
		values = {
			'title': title,
			'page': page,
			'content': content.readlines(),
			'user': user,
			'admin': admin,
			'datetime': None,
		}

		self.response.out.write(template.render(path, values))

class EditForm(webapp.RequestHandler):
	def get(self, page):
		user = users.get_current_user()
		admin = users.is_current_user_admin()

		content_dir = 'content'
		try:
			page_file = os.path.join(content_dir, page.lower() + '.htf')
			content = file(page_file, 'r')
		except IOError:
			page = 'home'
			page_file = os.path.join(content_dir, page.lower() + '.htf')
			content = file(page_file, 'r')
		
		title = page.capitalize()

		path = 'html/edit_form.html'
		values = {
			'title': title,
			'page': page,
			'content': content.readlines(),
			'user': user,
			'admin': admin,
			'datetime': None,
		}

		self.response.out.write(template.render(path, values))

class LoginPage(webapp.RequestHandler):
	def get(self):
		self.redirect(users.create_login_url(self.request.referrer))

class LogoutPage(webapp.RequestHandler):
	def get(self):
		self.redirect(users.create_logout_url(self.request.referrer))

class MainPage(webapp.RequestHandler):
	def get(self):
		self.redirect('/page/home')

class MercurialPage(webapp.RequestHandler):
	def get(self):
		self.redirect('http://bitbucket.org/just6979/just6979')

application = webapp.WSGIApplication([
	('/', MainPage),
	(r'/page/(.*)', SinglePage),
	(r'/edit/(.*)', EditForm),
	('/login', LoginPage),
	('/logout', LogoutPage),
	('/hg', MercurialPage),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
