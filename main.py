# -*- coding: utf-8 -*-
import os
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class Page(db.Model):
    datetime = db.DateTimeProperty(required=True)
    title = db.StringProperty(required=True)
    author = db.UserProperty(required=True)
    content = db.TextProperty(required=True)
    tags = db.StringProperty()


def get_page_data(page):
    content_dir = 'content'
    try:
        page_file = os.path.join(content_dir, page.lower() + '.htf')
        data = file(page_file, 'r')
    except IOError:
        page = 'home'
        page_file = os.path.join(content_dir, page.lower() + '.htf')
        data = file(page_file, 'r')

    content = ''
    for line in data:
        content += line

    return content


class SinglePage(webapp.RequestHandler):
    def get(self, page):
        user = users.get_current_user()
        admin = users.is_current_user_admin()

        title = page.capitalize()

        path = 'html/main.html'
        values = {
            'title': title,
            'page': page,
            'content': get_page_data(page),
            'user': user,
            'admin': admin,
        }

        self.response.out.write(template.render(path, values))


class UpdatePage(webapp.RequestHandler):
    def post(self, page, form):
        pass


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


app = webapp.WSGIApplication([
    ('/', MainPage),
    (r'/page/(.*)', SinglePage),
    (r'/update/(.*)', UpdatePage),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
    ('/hg', MercurialPage),
], debug=True)
