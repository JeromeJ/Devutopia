#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Platform that aim to bring the decentralize advantages to the whole world.

Everything will be user-collaborative-able, everyone will be able to add content
without asking and without replacing original content.
Every contribution will be available to the public,
if the publisher wish so. This is not up to the original publisher though.
Original author can then choose to ignore, accept or merge new modifications.

Technical note: Probably wont be really decentralized at first, for the sake of simplicity of dev,
but the goal is to make it really decentralized later. For now, we'd like a quick neat way
to bring a decentralized-like plateform for everybody and every type of content.
"""

import cgi
import collections
import datetime
# import functools  # Not used
import logging  # TODO: Change the format of logging so that it includes the date [minor]
import operator
import os
import re
# import sqlite3  # Not used
import string
# import sys  # Not used
import time
import urllib.parse
import uuid

# TODO: Make an offical address (*@devutopia.net) [normal]
# COMMENT ID: tag:devutopia.net,2013-11-03:Topic-changing-contact-info

# TODO: Make the email address being put dynamically in the .tpl (instead of being hardcoded) [normal]

__author__ = "JeromeJ"
__contact__ = "devutopia.devs [this would be an amphora symbol but we don't like spambots] olissea.net"
__website__ = "http://devutopia.net/"
__licence__ = "Copy left: Share-alike"


try:
	# Uniformisation

	# Sometimes "os.path.dirname" return an empty string which is an invalid parameter for "os.chdir".
	# → Using "or" instead of catching the FileNotFound exception which varies from one OS to another.

	os.chdir(os.path.dirname(__file__) or ".")
except NameError:
	# "__file__" is not always defined, notably when running through interactive shell for instance.

	pass


instance_name = str(uuid.uuid4())


class cached_property(object):
	"""
	A read-only @property that is only evaluated once. The value is cached
	on the object itself rather than the function or class; this should prevent
	memory leakage.
	"""

	# Source: http://www.toofishes.net/blog/python-cached-property-decorator/  # TODO: Should it be a metada? (like __source__) [minor]

	# This decorator allows to create properties that get properly generated only when accessed
	# for the first time (without requiring to create a dynamic property that would have to check
	# everytime if the content has been generated yet or not, generate it if required, and return it)

	def __init__(self, fget, doc=None):
		self.fget = fget
		self.__doc__ = doc or fget.__doc__
		self.__name__ = fget.__name__
		self.__module__ = fget.__module__

	def __get__(self, obj, cls):
		if obj is None:
			return self
		obj.__dict__[self.__name__] = result = self.fget(obj)
		return result


# TODO: Question: Couldn't it use @staticmethod instead? [normal]
class BetterFormat(string.Formatter):
	"""
	Introduce better formattings.

	Currently, it allows to automatically indent a block of text according to its current depth of identation.
	"""

	def parse(self, format_string):
		"""Receive the raw string and split its elements apart to facilitate the actual replacing."""

		return [
			(
				before,
				identifiant,
				str(
					len(
						re.search('\t*$', before).group(0)
					)
				) + '\t' + (param if param is not None else ''),
				modif,
			)
			for before, identifiant, param, modif
			in super().parse(format_string)
		]

	def format_field(self, v, pattern):
		"""Receive the string to be transformed and the pattern according which it is supposed to be modified."""

		# Hacky way to remove a dynamic sequence of characters ([0-9]+\t) and returning it (= pop some text)

		shared_data = {'numberOfTabs': 0}

		def extractTabs(pattern):  # Creating a closure on sharedData
			shared_data['numberOfTabs'] = int(pattern.group(0)[:-1])
			return ""

		pattern = re.sub('[0-9]+\t', extractTabs, pattern)

		# End of Hacky way to "pop some text"

		if shared_data['numberOfTabs']:  # If there are tabs to be added
			v = (shared_data['numberOfTabs'] * '\t').join(v.splitlines(True))

		return super().format_field(v, pattern)


class Tag:
	"""Utility class to ease the creation of URI tags."""
	
	DEFAULT_AUTHORITY_NAME = None  # To be manually set
	
	# Arguments are named according to RFC 4151.
	# Although, fragment (what comes after the "#") isn't implemented
	# → Directly put into specific (eg: specific="myExample#fragment")
	def __init__(self, date, specific, authority_name=None):
		self.authority_name = authority_name or Tag.DEFAULT_AUTHORITY_NAME
		self.date = date
		self.specific = specific 
	
	def __str__(self):
		
		# TODO: Should we tag object immutable (would be more logical)? [normal]
		# → Plus, we could raise the ValueError on the creation rather than when displaying (it's hard to debug).
		# (→ Then, elements should be stored as _private or should we inherit a NamedTuple? (I like the second I think))
		
		try:
			assert self.authority_name is not None
		except AssertionError:
			raise ValueError("Must set an authority name. Cannot generate tag.")
		
		return "tag:{authority_name},{date}:{specific}".format(
			authority_name=self.authority_name,
			date=self.date,
			specific=self.specific
		)

Tag.DEFAULT_AUTHORITY_NAME = 'devutopia.net'

class DynamicMapping(dict):
	"""
	Provide a special dict to ease the formatting of strings for displaying on the website.

	Options to allow to automatically escape data and/or to allow missing keys.
	"""

	def __init__(self, *args, strict=True, safe=True, **kwargs):
		self.strict = strict
		self.safe = safe
		super().__init__(*args, **kwargs)

	def __getitem__(self, key):
		if self.safe:
			return cgi.escape(super().__getitem__(key))

		return super().__getitem__(key)

	def __missing__(self, key):
		if self.strict:
			return super().__missing__(key)

		return '{' + cgi.escape(key) + '}'


started_on = datetime.datetime.now()

try:
	# TODO: Wont this implicitely call ".read()" when we iter over it? ([minor]? or normal)
	# See tag:devutopia.net,2013-11-03:Probably-implicitely-calling-read-without-parameter
	
	# Then, if so, it shouldn't be let paremeter-less, right?
	# → Check the opener parameter of http://docs.python.org/3.3/library/functions.html#open
	# → Also opened an issue on GitHub with more info: https://github.com/JeromeJ/Devutopia/issues/1

	# TODO: Also find a way to embed that into a "with" block as it should? [normal]

	hello_world = open('data/helloworld.txt', encoding="utf-8")
except OSError:
	# TODO: Try to create the file? [minor]
	# Maybe only try to create it when needed?  # On saving?
	
	hello_world = []  # Default value
	logging.warning("data/helloworld.txt NOT FOUND! → Creating an empty list.")  # TODO: Check if "→" displays well in the log (Guessing so) [minor]

# TODO: Finish to setup the SQLite db alternative ([important] ?) (Status: started)

# HW_conn = sqlite3.connect('data/helloworld.db')
# c = HW_conn.cursor()
# c.execute('CREATE TABLE IF NOT EXISTS langs (id INTEGER PRIMARY KEY, author INTEGER, lang_name VARCHAR, translation VARCHAR, added DATE)')

# TODO: Improve the moto by making it more accesible? ([normal]? or minor)
# → Make it more accessible to the man in the street? (dat idiom though… Hope it's the right one. I meant "monsieur/madame tout le monde")
# And let geeky explanations available for geeks (but as extra info. It shouldn't come confuse everyday ppl (valid alternative of "dat idiom"?))

moto = [
	("Bring the advantages of programming's world decentralized systems (like git, …) to the whole world.",),

	("Let everyone bring content / edits / ideas / … in a non intrusive way:",
		"Just like if you created your clone of a project and modify it."),

	("These rules also apply to this very project:",
		"This project is YOURS. Bring your ideas, opinions, code, content, …"),
]

# TODO: Hey, should/could we setup open as 'open = functools.partial(open, encoding="utf-8")' "as it should be"? ([normal]: Talking about the question)
# TODO: Why 4096 if not "why not?"? [minor]
template = BetterFormat().format(open('tpl/index.tpl', encoding="utf-8").read(4096),
	# Cannot use 'expr if hello_world else "No lang registered yet"' because hello_world returns True (as it is a generator)
	# Even if it will not yield anything (which was confusing at first but totaly normal).
	# → Using the "or" trick instead.
	langs='\n'.join(
		'<span class="lang">({})</span> <bdi>{}</bdi> ☺<br />'.format(
			*cgi.escape(line[:-1]).split(None, 1))
		for line in hello_world)  # CODE ID: tag:devutopia.net,2013-11-03:Probably-implicitely-calling-read-without-parameter
	or "<em>No lang registered yet!</em>",

	moto='<li>' + '</li>\n<li>'.join('<br />\n'.join(rule) for rule in moto) + '</li>')

# # Not used
# test = """\
# <strong>GET:</strong> {get}<br />
# <strong>POST:</strong> {post}<br /><br />

# <strong>Method:</strong> {method}\
# """

# TODO: Continuing studying ATOM feeds. [important] (Status: Started)
# Ressources:  # TODO: Open a GitHub's issue instead? ([important]: Talking about the question) (→ Thinking so, but idk)
# * http://www.diveinto.org/python3/xml.html
# * http://www.tutorialspoint.com/rss/what-is-atom.htm
# * …
rss_template = """\
<?xml version="1.0" encoding="utf-8" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
	<title>{name}</title>
	<!--<subtitle></subtitle>-->
	<!--<updated></updated>--><!-- # TODO: Is REQUIRED!! [important] -->
	<!--<author><name></name><uri></uri></author>-->
	<link rel="alternate" type="text/html" href="{src_html}" />
	<link rel="self" href="{src}" />
	<id>{id}</id>
	<!--<description>{descript}</description>-->
	{items}
</feed>\
"""

# TODO: Also make so that, if {msg} has more than one line, then it automatically becomes a block [normal]
# COMMENT ID: tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting
rss_item = """\
<entry>
	<title>{descript}</title>
	<!--<author></author>-->
	<id>{id}</id>
	<link rel="alternate" type="text/html">{url}</link>
	<description>{msg}</description>
	<published>{date}</published>
	<!--<updated></updated>--><!-- # TODO: Is REQUIRED!! (not published) [important] -->
	<!--<summary type="html"></summary>-->
	<content type="html"></content>
</entry>"""
# TODO: Isn't 'rel="alternate"' by default in that case? (Couldn't specify a link to a RSS entry, right?) [minor]
# → I think so but I also think it should be indicated anyway


class HTTPException(Exception):

	def __init__(self, code, msg):
		self.code = code
		self.msg = msg
		super().__init__(code)

	def __call__(self, environ):
		self.msg = self.msg.format_map(
			DynamicMapping(environ, strict=False, safe=True))

		return self


# TODO: Improve by making more dynamic? (like the charset? etc) [normal]
# TODO: Using a template (right?) [normal]
# TODO: Also implement other errors… [normal]
# …Ideally all based on the same base template: Shouldn't it be handled by the HTTPException class then?)
HTTPException.error404 = HTTPException('404 Not Found', """
<!DOCTYPE html>
<html>
	<head>
		<title>404 Not Found</title>
		<meta charset="UTF-8" />
	</head>
	<body>
		<h1>Not Found</h1>
		<p>The requested URL {SCRIPT_NAME} was not found on this server.</p>
	</body>
</html>\
""")

# TODO: Use it. Maybe improving it first (+ see Args class) [normal]

# Not used (Note: Automatically commented using the Ctrl+e command in Geany)
#~ class NotStrictList(list):
	#~ """Offer the possibility to normalize data automatically when testing for the presence of some data in that list."""
	#~ # TODO: Should/could it be about sequences in general? [normal]
#~ 
	#~ default_normalizer = operator.methodcaller('lower')
#~ 
	#~ def __contains__(self, item, strict=False, normalizer=None):
		#~ if strict:
			#~ return super().__contains__(item)
#~ 
		#~ if normalizer is None:
			#~ normalizer = NotStrictList.default_normalizer
#~ 
		#~ return normalizer(item) in map(normalizer, self)


# TODO: To be finished too! [normal]
# Will probably be used to automatically do what is needed for args and post? (for instance changing them into a dict of NonStrictList?)
# Instead to be directly handled in the main class

# Not used (Note: Automatically commented using the Ctrl+e command in Geany)
#~ class Args(dict):
#~ 
	#~ def __init__(self, args):
		#~ pass


class HTTPManager:
	"""WSGI HTTP Managing Utility tool."""

	status = '200 OK'

	headers = {
		'Content-Type': 'text/html; charset=utf-8',

		# TODO: Idea: Make so that when editting Content-Type… [normal]
		# …it automatically becomes '{content-type}; charset={charset}' (or something like that ;) )
		# COMMENT ID: tag:devutopia.net,2013-12-05:editing-content-type-would-automatically-update-charset
		# → Handle them automatically
	}

	committed = False

	def __init__(self, start_response):
		self.start_response = start_response
		self.headers = HTTPManager.headers.copy()

	def exception(self, err):
		self.status = err.code
		self.commit()

	def commit(self):
		if not self.committed:
			self.start_response(
				self.status,
				list(self.headers.items())
			)

			self.committed = True


class application:
	"""Main WSGI app."""

	# TODO: Change the docstring? ([normal]? or minor)
	# Calling it "presentation" or "homepage"?
	# Or let it be the "Helloworld app" even though it will probably eventually not be the "homepage app" anymore?
	# Maybe create the "homepage app" and set it so "homepage_app = hello_world_app"?

	def __init__(self, environ, start_response):
		self.environ = environ
		self.start_response = start_response

		self.http = HTTPManager(start_response)

	# TODO: Handle the two methods below with the Args class? [normal]
	@cached_property
	def args(self):
		return collections.defaultdict(list, urllib.parse.parse_qs(self.environ['QUERY_STRING']))

	@cached_property
	def post(self):
		# TODO: Make the encoding/decoding be dynamic instead of hardcoded? [normal]
		# → Which fool wouldn't use UTF-8 though? (Wouldn't it be more 'right' anyway)
		# → Erm, though… I think that this has nothing to do with decoding: (EDIT: Indeed ;) )
		# → Cause decoding is depending on the ressources being opened (right?)
		# → But, in the other hand, the encoding, mainly if meant to be 'printed out' (or returned by WSGI) then,
		# → maybe it should be handled automatically ;)
		# COMMENT ID: tag:devutopia.net,2013-12-05:dynamic-encoding-type#instead_of_hardcoded
		return collections.defaultdict(list, urllib.parse.parse_qs(self.environ['wsgi.input'].readline().decode('utf-8'), True) if self.environ["REQUEST_METHOD"] == 'POST' else {})

	def __iter__(self):
		try:
			# As "yield from" is only avaible from Python 3.3, this is done manually

			# TODO: We can't put that in a decorator right? ([minor] as it works like that anyway and isn't too hard to understand, I think)
			# I think I tried and finished with that only solution: __iter__ is kind of the decorator for self.main

			main_gen = self.main()

			first_item = next(main_gen)

			# Default commit (if none has been sent yet)
			self.http.commit()
			
			# TODO: Make sure the following note is right ([minor]? or normal)
			# Note: I don't think anything is *sent back* (generator.send and "foo = (yield bar)") to the main app generator (by WSGI itself), so I don't handle that here…
			# Also see tag:devutopia.net,2013-12-05:dynamic-encoding-type#instead_of_hardcoded
			yield first_item.encode('utf-8')

			for el in main_gen:
				# TODO: See tag:devutopia.net,2013-12-05:dynamic-encoding-type#instead_of_hardcoded [normal]
				yield el.encode('utf-8')

		except HTTPException as HTTP_exception:
			HTTPManager(self.start_response).exception(HTTP_exception)
			# TODO: See tag:devutopia.net,2013-12-05:dynamic-encoding-type#instead_of_hardcoded [normal]
			yield HTTP_exception(self.environ).msg.encode('utf-8')

	def main(self):
		
		# To be able to run in local:
		if os.path.isfile(self.environ['PATH_INFO'][1:]):  # Getting rid of the starting "/" to make it relative
			authorised_ext = {".css": "text/css", ".js": "application/x-javascript"}
			ext = os.path.splitext(self.environ['PATH_INFO'])[1]

			if ext in authorised_ext:
				# TODO: See tag:devutopia.net,2013-12-05:editing-content-type-would-automatically-update-charset [normal]
				self.http.headers['Content-Type'] = authorised_ext[ext] + "; charset=utf-8"

				yield open(self.environ['PATH_INFO'][1:], encoding="utf-8").read(1048576) # Funky arbitrary number, right?
				raise StopIteration
			else:
				raise HTTPException.error404
		elif self.environ['PATH_INFO'].rstrip('/') != '':
			raise HTTPException.error404

		if 'RSS' in map(operator.methodcaller('upper'), self.args['do']):  # TODO: Use NotStrictList class [normal]
			# TODO: See tag:devutopia.net,2013-12-05:editing-content-type-would-automatically-update-charset [normal]
			self.http.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'

			# TODO: Implement str.format_map for BetterFormat so that one can use DynamicMapping? [normal]
			
			# TODO: Errrm, could/should we use two level of "[ normal ]" TODO thing? [important]
			# (NOTE: Put spaces so that they aren't matched when searching for them with Ctrl+F as actual TODO things)
			# What we currently have (for [ normal ] and above)
			# → [ normal ],
			# → [ important ] (seems already too strong),
			# → [ critic ] (Erm, if there is something critic, shouldn't it be fixed immediately? ;D and so, this tag shouldn't be used often ^^)

			# TODO: Finish to generate RSS automatically [important] (Status: Started)
			yield BetterFormat().format(
				rss_template,
				**{
					'id': Tag('2013-09-22', 'helloworldfeed'),
					'name': 'Hello World',
					'src_html': 'http://devutopia.net/',  # TODO: Make dynamic [normal]
					'src': 'http://devutopia.net/?do=RSS',  # TODO: Make dynamic [normal]
					'descript': 'Hello World in several langages',
					'items': BetterFormat().format(
						rss_item,
						**{
							'descript': '[fr] Bonjour tout le monde',
							'id': Tag('2013-09-22', 'helloworldentry-in_french-by_devutopia'),
							'url': 'http://devutopia.net/helloworld.py?itemid=1',
							# TODO: Should automatically aligns on two lines (see tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting)
							'msg': 'French version.<br />\nAdded by devutopia.',
							'date': '2013-09-22'
						}
					)
				}
			)

			raise StopIteration
		
		# TODO: What to do with the junks? ([normal]? or minor)
		# → Should get rid of some
		# → Could(/should?) keep some but at least tidy up things? group them?
		# → idk…
		# COMMENT ID: tag:devutopia.net,2013-12-05:junkomania-handling
		
		# # Some junk :) ([fr] "syllogomanie"; [en] "compulsive hoarding")
		# yield __import__('sys').version+'<br />'
		# yield __import__('sqlite3').dbapi2.sqlite_version # → Not the one I would have hoped for (but not required anyway)
		
		# Timestamp in minutes of now minus timestamp of minutes since when that instance started
		minutes = int(time.mktime(datetime.datetime.now().timetuple()) / 60 - time.mktime(started_on.timetuple()) / 60)

		yield BetterFormat().format(template,
			# TODO: See tag:devutopia.net,2013-12-05:junkomania-handling [normal]
			# test=test.format(get=cgi.escape(str(self.args)), post=cgi.escape(str(self.post)), method=cgi.escape(self.environ["REQUEST_METHOD"])),
			# test='Nothing to see here 😒', # Don't delete me :p I'm a fancy smiley and I don't want to disappear, let me be!
			# TODO: Should be put in the test variable? (helloworld.py scope) [minor]
			
			# TODO: Should also automatically forms a block, right? (See: tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting ) [normal]
			test='<b>Instance name:</b> {name}<br /><b>Started {minutes} minute{s} ago.</b>'.format(\
				name=cgi.escape(instance_name),
				minutes=minutes,
				s='s' * (minutes > 1)
			)
		)
		# TODO: See tag:devutopia.net,2013-12-05:junkomania-handling [normal]
		# +'<br /><strong>Environ:</strong>'+cgi.escape(str(self.environ)).replace(',', ',<br />\n'),

if __name__ == '__main__':
	# TODO: See tag:devutopia.net,2013-12-05:junkomania-handling [normal]
	# → That is less junk though, important pieces of information here.
	# TODO: Make a specific comment/TODO-thing for this type o' content or just the comment below? ([minor]? or normal)
	
	# Then run wsgiref for local testing
	# → I don't know if wsgiref handles multiple instances (and if so, by its own) (→ I guess/think/hope so)  # TODO: Investiguate/make sure [minor]
	# → I don't know if I have to handle the request myself if using wsgiref (→ Yep, see answer below)

	# Answer: "If you want to serve multiple applications on a single host and port, you should create a WSGI application that parses PATH_INFO to select which application to invoke for each request. (E.g., using the shift_path_info() function from wsgiref.util.)"

	from wsgiref.simple_server import make_server

	httpd = make_server('', 8000, application)

	print('Launching the server in local mode... Hello!')  # Can't use "…" in case of Windows, because Windows is stupid. I said it. UTF-8 isn't yet handle by everyone in 2013… That's sad, isn't it? (Or you can "modify" the Windows environnement but it's not a good idea and not perfect)

	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print('Shuting down... Good bye!')
