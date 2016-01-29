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

import collections
import datetime
import html
import logging  # TODO: Change the format of logging so that it includes the date [minor]
import operator
import os
import re
import sqlite3
import string
import sys
import time
import types
import urllib.parse
import uuid

from functools import wraps

sys.path.append('/usr/local/lib/python3.3/dist-packages/')

from urllib.parse import urljoin

# TODO: Upgrade to Flask [important] (Status: Started)
from flask import Flask, request, Response, stream_with_context
from werkzeug.contrib.atom import AtomFeed

try:
	import names
except ImportError:
	names = None

# TODO: Make an offical address (*@devutopia.net) if possible [normal]
# COMMENT ID: tag:devutopia.net,2013-11-03:Topic-changing-contact-info

__author__ = "JeromeJ"
__contact__ = "devutopia.devs [this would be an amphora symbol but we don't like spambots] olissea.net"
__website__ = "http://devutopia.net/"
__licence__ = "Copy left: Share-alike"


# ## Reminder / Helper: Way I did setup Flask for Python 3 ##
# (Note: You 'may' not have those packages available to you by default)
# (… Personnally I had to temporarly add the saucy packages for the newer version of Ubuntu)
#
# aptitude install python3-pip
# pip3 install flask
# # May differ on your system! (May be improved too)
# echo "export PYTHONPATH=/usr/local/lib/python3.3/dist-packages/" >> .bashrc
# # Alternative: sys.path.append('/usr/local/lib/python3.3/dist-packages/')

app = Flask(__name__)
application = app

# Decorator to make Flask accept generators

# app.route is a decorator with parameter…
@wraps(app.route)
def route_accept_generators(*args, **kwargs):
	# So we first call the original app.route (that we stored into this function to save place)
	# and call it to receive our decorator

	route = route_accept_generators.app_route(*args, **kwargs)  # Getting our route decorator.

	# At this point we have our traditional app.route('/myRoute/')
	# Next, app.route('/myRoute/')(f) will happen
	# But app.route('/myRoute/'), who will call f(), doesn't like when f return a generator.
	# If one want to return a generator, he has to use Response(stream_with_context(r))
	# So we'll decorate app.route('/myRoute/') so that it will decorate f, so that, when called, it will always return a valid value
	# i.e. not a generator or Response(stream_with_contect(gen))

	# Decorating the decorator so that it also accepts generator.
	@wraps(route)
	def decorated(f):

		# Make so that the function that will be called return a valid Flask answer in case of returning a generator.
		@wraps(f)
		def function_accept_generators(*args, **kwargs):
			r = f(*args, **kwargs)

			if isinstance(r, types.GeneratorType):
				# return Response(r, direct_passthrough=True)  # Solution proposed here: http://flask.pocoo.org/mailinglist/archive/2010/11/3/using-yield/#478b0c1829b5263700da1db7d2d22c79
				return Response(stream_with_context(r))  # Solution found here: http://stackoverflow.com/q/13386681/1524913

			return r

		# Would have normally just return route(f)
		return route(function_accept_generators)

	return decorated

# Store the function so that it doesn't make an infinite recursion call
# Because accessing from app.route rather than directly)
# And storing it in itself instead of creating another standalone variable
# TODO: Should I use a class decorator instead then? ([minor] ?)
route_accept_generators.app_route = app.route

app.route = route_accept_generators

try:
	# Uniformisation

	# Sometimes "os.path.dirname" return an empty string which is an invalid parameter for "os.chdir".
	# → Using "or" instead of catching the FileNotFound exception which varies from one OS to another.

	os.chdir(os.path.dirname(__file__) or ".")
except NameError:
	# "__file__" is not always defined, notably when running through interactive shell for instance.

	pass


instance_name = '{} (<strong>UUID:</strong> {})'.format(html.escape(names.get_full_name()), html.escape(str(uuid.uuid4()))) if names else str(uuid.uuid4())


# TODO: Must inherit object?? Isn't it only in Python2 that we do that?? [minor]
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

	def __init__(self, strict=True, safe=True, *args, **kwargs):
		self.strict = strict
		self.safe = safe
		super().__init__(*args, **kwargs)

	def __getitem__(self, key):
		if self.safe:
			return html.escape(super().__getitem__(key))

		return super().__getitem__(key)

	def __missing__(self, key):
		if self.strict:
			return super().__missing__(key)

		return '{' + html.escape(key) + '}'


started_on = datetime.datetime.now()

# TODO: Finish to setup the SQLite db alternative ([important] ?) (Status: started)

try:
	hw_conn = sqlite3.connect('data/helloworld.db')

	# # If you want being able to access by columns name too
	# hw_conn.row_factory = sqlite3.Row
	with hw_conn:
		hw_conn.execute(
		"""CREATE TABLE
			IF NOT EXISTS
			langs (
				id INTEGER PRIMARY KEY,
				author INTEGER,
				lang_name VARCHAR,
				translation VARCHAR,
				added DATE
			)
		""")

	hello_world = list(hw_conn.execute('SELECT lang_name, translation FROM langs'))

	# raise sqlite3.OperationalError
except sqlite3.OperationalError:
	# TODO: Is that that a good idea? [normal]
	# → ① It's very rare,
	# → ② the content wont even be the same!
	# 	→ But at least we serve some content ☺
	#	→ So maybe, then, we should at least warn the user that this happenned!
	#	→ Eg: "Warning! We couldn't access database, you are seing alternative content!" … kind of.
	logging.warning("Cannot open database! → Accessing text file instead.")

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
		logging.warning("data/helloworld.txt NOT FOUND! → Creating an empty list.")
	else:
		hello_world = map(operator.methodcaller('split', None, 1), hello_world)

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
	contact=re.sub('\[[^\]]+\]', '[at symbol]', __contact__),
	# Cannot use 'expr if hello_world else "No translation registered yet"' because hello_world returns True (as it is a generator)
	# Even if it will not yield anything (which was confusing at first but totaly normal).
	# → Using the "or" trick instead.
	langs='\n'.join('<span class="lang">({})</span> <bdi>{}</bdi> ☺<br />'.format(*lang)
						for lang in hello_world)
			or "<em>No translation registered yet!</em><br />",

	moto='<li>' + '</li>\n<li>'.join('<br />\n'.join(rule) for rule in moto) + '</li>')

# # Not used
# test = """\
# <strong>GET:</strong> {get}<br />
# <strong>POST:</strong> {post}<br /><br />

# <strong>Method:</strong> {method}\
# """

# TODO: Use it. Maybe improving it first (+ see Args class) [normal]

# # Not used
# class NotStrictList(list):
# 	"""Offer the possibility to normalize data automatically when testing for the presence of some data in that list."""
# 	# TODO: Should/could it be about sequences in general? [normal]
#	
# 	default_normalizer = operator.methodcaller('lower')
#
# 	def __contains__(self, item, strict=False, normalizer=None):
# 		if strict:
# 			return super().__contains__(item)
#
# 		if normalizer is None:
# 			normalizer = NotStrictList.default_normalizer
#
# 		return normalizer(item) in map(normalizer, self)


# TODO: To be finished too! [normal]
# Will probably be used to automatically do what is needed for args and post? (for instance changing them into a dict of NonStrictList?)
# Instead to be directly handled in the main class

# # Not used
# class Args(dict):
# 	def __init__(self, args):
# 		pass

# TODO: Continuing studying ATOM feeds and finish to generate ATOM automatically [important] (Status: Started)
# Ressources:  # TODO: Open a GitHub's issue instead? ([important]: Talking about the question) (→ Thinking so, but idk)
# * http://www.diveinto.org/python3/xml.html
# * http://www.tutorialspoint.com/rss/what-is-atom.htm
# * http://atomenabled.org/developers/syndication/
# * …
# Important notes:
# → "A feed may have multiple author elements. A feed must contain at least one author element unless all of the entry elements contain at least one author element."
#	→ I propose to not check that with Python but stick to that note and try to respect it.

def make_external(url):
	return urljoin(request.url_root, url)

# TODO: Get rid o' that. Currently kept while upgrading the RSS. [normal]
rss_template = """\
<?xml version="1.0" encoding="utf-8" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
	<!--<author><name></name></author>-->
	<!--<category term=""></category>-->
	<id>{id}</id>
	<link href="{src_html}" type="text/html" /><!-- Default rel="alternate" -->
	<link href="{src}" rel="self" />
	<title>{name}</title>
	<!--<subtitle></subtitle>-->
	<!--<updated></updated>--><!-- # TODO: Is REQUIRED!! [important] -->
	{items}
</feed>\
"""

# TODO: Get rid o' that. Currently kept while upgrading the RSS. [normal]
# TODO: Also make so that, if {msg} has more than one line, then it automatically becomes a block [normal]
# COMMENT ID: tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting
rss_item = """\
<entry>
	<title>{descript}</title>
	<!--<author><name></name></author>-->
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

# RSS
@app.route('/helloworld.atom')
def helloworld_atom():
	feed = AtomFeed('Hello World', feed_url=request.url, url=request.url_root, id=Tag('2013-09-22', 'helloworldfeed'), subtitle='Hello World in many languages!')

	l_escape = html.escape  # Optimization
	l_make_external = make_external  # Optimization
	l_date = datetime.datetime  # Optimization

	for i, line in enumerate(hello_world):
		lang_code, helloworld_translated = line
		feed.add('Hello World in {}'.format(l_escape(lang_code)),
			helloworld_translated,
			content_type='html',
			author='Devutopia',
			url=l_make_external('helloworld/entry.id.{}'.format(i)),
			updated=l_date(2014, 1, 5, 20, 12),
			published=l_date(2014, 1, 5, 20, 12),
		)
	return feed.get_response()

@app.after_request
def after_request(response):
	# Remove the display of the full version of Werkzeug and Python.
	response.headers.add('Server', 'Werkzeug Python 3')  # TODO: Should we consider removing it completly or is it good enough? [minor]
	return response

@app.route('/')
def index():
	""" Main WSGI app (Flask). """

	# TODO: Change the docstring? ([normal]? or minor)
	# Calling it "presentation" or "homepage"?
	# Or let it be the "Helloworld app" even though it will probably eventually not be the "homepage app" anymore?
	# Maybe create the "homepage app" and set it so "homepage_app = hello_world_app"?

	# TODO: Implement str.format_map for BetterFormat so that one can use DynamicMapping? [normal]

	# TODO: Errrm, could/should we use two level of "[ normal ]" TODO thing? [important]
	# (NOTE: Put spaces so that they aren't matched when searching for them with Ctrl+F as actual TODO things)
	# What we currently have (for [ normal ] and above)
	# → [ normal ],
	# → [ important ] (seems already too strong),
	# → [ critic ] (Erm, if there is something critic, shouldn't it be fixed immediately? ;D and so, this tag shouldn't be used often ^^)

	# Not used # TODO: Get rid o' that. Currently kept while upgrading the RSS. [normal]
	if False and 'RSS' in map(operator.methodcaller('upper'), self.args['do']):
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

	# TODO: Should I put time.mktime and datetime.datetime into local variables? (that's not that a big matter, isn't it?)  [minor]

	hours = int((time.mktime(datetime.datetime.now().timetuple()) - time.mktime(started_on.timetuple())) / (60 * 60))
	minutes = int((time.mktime(datetime.datetime.now().timetuple()) - time.mktime(started_on.timetuple())) / 60) - hours * 60
	# TODO: Could be improved by some kind of "time % 60"? [minor]
	seconds = int((time.mktime(datetime.datetime.now().timetuple()) - time.mktime(started_on.timetuple()))) - hours * 60 * 60 - minutes * 60

	yield BetterFormat().format(template,
		# TODO: See tag:devutopia.net,2013-12-05:junkomania-handling [normal]
		# test=test.format(get=html.escape(str(self.args)), post=html.escape(str(self.post)), method=html.escape(self.environ["REQUEST_METHOD"])),
		# test='Nothing to see here 😒', # Don't delete me :p I'm a fancy smiley and I don't want to disappear, let me be!
		# TODO: Should be put in the test variable? (helloworld.py scope) [minor]

		# TODO: Should also automatically forms a block, right? (See: tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting ) [normal]
		test='<b>Instance name:</b> {name}<br /><b>Started {hours}{minutes}{seconds} ago.</b>'.format(
			name=instance_name,
			hours='{} hour{} '.format(hours, 's' * (hours >1)) if hours else '',
			minutes='{} minute{} '.format(minutes, 's' * (minutes > 1)) if minutes or hours else '',
			seconds='{} second{}'.format(seconds, 's' * (seconds > 1)),
		)
	)
	# TODO: See tag:devutopia.net,2013-12-05:junkomania-handling [normal]
	# +'<br /><strong>Environ:</strong>'+html.escape(str(self.environ)).replace(',', ',<br />\n'),


class OLDWSGI:
	"""Alternative WSGI app (uses pure WSGI) (Not used but kept for the transition to Flask)."""

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

if __name__ == '__main__':
	# TODO: See tag:devutopia.net,2013-12-05:junkomania-handling [normal]
	# → That is less junk though, important pieces of information here.
	# TODO: Make a specific comment/TODO-thing for this type o' content or just the comment below? ([minor]? or normal)

	# Then run wsgiref for local testing
	# → I don't know if wsgiref handles multiple instances (and if so, by its own) (→ I guess/think/hope so)  # TODO: Investiguate/make sure [minor]
	# → I don't know if I have to handle the request myself if using wsgiref (→ Yep, see answer below)

	# Answer: "If you want to serve multiple applications on a single host and port, you should create a WSGI application that parses PATH_INFO to select which application to invoke for each request. (E.g., using the shift_path_info() function from wsgiref.util.)"

	# TODO: Improve the logging of errors and all with Flask [important]
	# Currently showing everything with debug on or not showing anything at all -.-'
	app.debug = False

	# TODO: Apparently, when debug is enabled, the server asks for those info twice. Why? Does it create two instances because of input? [normal]
	addr = input('Addr? [devutopia.net] ')
	port = input('Port? [80] ')

	try:
		app.run(addr or 'devutopia.net', int(port or 80))
	except KeyboardInterrupt:
		print('Shuting down... Good bye!')  # Can't use "…" in case of Windows, because Windows is stupid. I said it. UTF-8 isn't yet handle by everyone in 2013… That's sad, isn't it? (Or you can "modify" the Windows environnement but it's not a good idea and not perfect)
