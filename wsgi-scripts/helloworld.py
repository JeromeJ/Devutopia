#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: PEP 257 → http://www.python.org/dev/peps/pep-0257/

"""
This script is the starting of a, hopefully, huge collaborative platform.

Everything will be user-collaborative-able, everyone will be able to add content.
And every content will automatically accepted and stored in the "Content by users" tab (the name might differ).
Some lucky data could even get "officialised" by the original author.
"""

# TODO: Change the descript for something more appropriate?

import cgi
import collections
import datetime
# import functools # Not used
import logging  # TODO: Change the format of logging so that it includes the date
import operator
import os
import re
import sqlite3
import string
# import sys # Not used
import time
import urllib.parse
import uuid

# TODO: Should we changed official contact info? Creating an offical contact adress? I guess it's ok for now.
# Comment ID: tag:devutopia.net,2013-11-03:Topic-changing-contact-info
__author__ = "JeromeJ"
__contact__ = "e-warning [this would be an amphora symbol but we don't like spambots] hotmail.com"
__website__ = "http://www.olissea.com/"
__licence__ = "Really Free (but I always appreciate credits) aka you do whatever you want with it (something 'good' I hope)"

# Bugfix: Sometimes (seems to be OS related), if the script is launched directly from the current folder (eg. not launched by mod_wsgi),
# os.path.dirname(__file__) then returns '' which raises a FileNotFound exception.
# (But as FileNotFound exceptions aren't handled the same way on each OS, we check instead of catching it)
if os.path.dirname(__file__):
	os.chdir(os.path.dirname(__file__))

instance_name = str(uuid.uuid4())


class cached_property(object):
	"""
	A read-only @property that is only evaluated once. The value is cached
	on the object itself rather than the function or class; this should prevent
	memory leakage.
	"""

	# Source: http://www.toofishes.net/blog/python-cached-property-decorator/ # TODO: Should it be a metada? (like __source__)

	# This decorator allows to create properties that get properly generated only when accessed for the first time (without requiring to create a dynamic property that would have to check everytime if the content has been generated yet or not, generate it if required, and return it)

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


class BetterFormat(string.Formatter):
	"""
	Introduce better formattings

	Currently, it allows to automatically indent a block of text according to its current depth of identation.
	"""

	def parse(self, format_string):
		""" Receive the raw string and split its elements apart to facilitate the actual replacing """

		return [(
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
				in super().parse(format_string)]

	def format_field(self, v, pattern):
		""" Receive the string to be transformed and the pattern according which it is supposed to be modified """

		# Hacky way to remove a dynamic sequence of characters ([0-9]+\t) and returning it (= pop some text)

		sharedData = {'numberOfTabs': 0}

		def extractTabs(pattern):  # Creating a closure on sharedData
			sharedData['numberOfTabs'] = int(pattern.group(0)[:-1])
			return ""

		pattern = re.sub('[0-9]+\t', extractTabs, pattern)

		# End of Hacky way to "pop some text"

		if sharedData['numberOfTabs']:  # If there are tabs to be added
			v = (sharedData['numberOfTabs'] * '\t').join(v.splitlines(True))

		return super().format_field(v, pattern)


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
	# TODO: Wont this implicitely call ".read()"? (when we iter over it, see tag:devutopia.net,2013-11-03:Probably-implicitely-calling-read-without-parameter )
	# Then, it shouldn't be let paremeter-less, right?
	# → Check the opener parameter of http://docs.python.org/3.3/library/functions.html#open

	# TODO: Also find a way to embed that into a "with" block as it should?

	helloworld = open('data/helloworld.txt', encoding="utf-8")
except OSError:
	# TODO: Try to create the file # Or only try to create it when needed? # Hmm?
	helloworld = []
	logging.warning("data/helloworld.txt NOT FOUND! → Creating an empty list.") # TODO: Check if "→" displays well in the log (I guess so)


# TODO: TO BE FINISHED YET
# HW_conn = sqlite3.connect('data/helloworld.db')
# c = HW_conn.cursor()
# c.execute('CREATE TABLE IF NOT EXISTS langs (id INTEGER PRIMARY KEY, author INTEGER, lang_name VARCHAR, translation VARCHAR, added DATE)')
# End of not yet finished code

moto = [
	("Bring the advantages of programming's world decentralized systems (like git, …) to the whole world.",),

	("Let everyone bring content / edits / ideas / … in a non intrusive way:",
		"Just like if you created your clone of a project and modify it."),

	("These rules also apply to this very project :",
		"This project is YOURS. Bring your ideas, opinions, code, content, …"),
]

template = BetterFormat().format("""
<!DOCTYPE html>
<html>
	<head>
		<title>Hello world ☺ - Olissea DEV</title>
		<meta charset="UTF-8" />
		<link rel="stylesheet" media="screen" type="text/css" title="Main style" href="/css/main.css" />
	</head>
	<body>
		<div id="status"><strong><span class="WIP">WIP</span> - Work In Progress</strong>, <em>come back later!</em></div><!-- # TODO: Remove that? When? -->
		<div id="extra"><em>Contact me if interested!</em><br /><strong>Contact:</strong> e-warning [at symbol] hotmail.com</div><!-- # TODO: See tag:devutopia.net,2013-11-03:Topic-changing-contact-info (in helloworld.py) -->
		<div id="title"><strong><span class="dev">Dev</span><span class="utopia">utopia</span></strong></div>

		<hr class="clear" />

		<div id="main">
			<div id="leftContainer">
				<h1>Hello World</h1>
				<div id="helloWorld">
					{langs}
					…<br />
					<button>Add a lang</button> <em>or</em> edit one… (<em>Not implemented yet… Soon!</em>)
				</div>

				<div id="test">
					<h2>Testing zone</h2>

					<p>
						{{test}}
					</p>
				</div>
			</div>
			<div id="rightContainer">
				<h1>« A huge collaborative project to come! »</h1>
				<h2>What is this?</h2>
				<div class="spoiler">
					<ol id="moto">
						{moto}
					</ol>

					<p>
					So, your contributions will be automatically accepted under the "By users" tab and will be displayed to the whole world (if you wish), they'll stay there (if you wish), and, in case you proposed data for someone else's content and if you're lucky, it may get merged with the original content by his original author or be choosen to be the new official version.
					</p>
				</div>
			</div>
			<div class="clear"></div>
		</div>

		<div id="foot">
			<span id="privacyPolicy"> We don't collect data about you ☺<span class="heart">♥</span> → We <strong class="love">love</strong> you! <span class="hearts">❤💓💕💖💘💗💙💚💛💜💝💞💟💖💙💜💚💗💘💛💝💞💟</span><!-- # TODO: Ne s'affiche que sous win… Une piste: U+1F495, U+1F496, U+1F497, U+1F499, U+1F49A, U+1F49B, U+1F49C, U+1F49D, U+1F49E, U+1F49F, U+1F496, U+1F497, U+1F498, U+1F49B, U+1F49D, U+1F49E, U+1F49F la séquence complète. C’est valide, et il existe sûrement une fonte qui les a --><!-- Note for myself: If you edit that under windows, it will look glitched, don't edit that part!! --></span>
			<span id="source"><strong>Source:</strong> ftp://anonymous@devutopia.net/ </span>
		</div>
	</body>
</html>""",
	# Can't use '<gen> if helloword else "No lang registered yet"' because helloworld returns True (as it is a generator) even if it will not yield anything (which was confusing at first but totaly normal)
	# So we are using "or" instead
	langs='\n'.join(
		'<span class="lang">({})</span> <bdi>{}</bdi> ☺<br />'.format(
			*cgi.escape(line[:-1]).split(None, 1))
		for line in helloworld) # Code ID: tag:devutopia.net,2013-11-03:Probably-implicitely-calling-read-without-parameter
	or "<em>No lang registered yet!</em>",

	moto='<li>'+'</li>\n<li>'.join('<br />\n'.join(rule) for rule in moto)+'</li>')

test = """\
<strong>GET:</strong> {get}<br />
<strong>POST:</strong> {post}<br /><br />

<strong>Method:</strong> {method}\
"""

# TODO: Continuing studying ATOM feeds.
rss_template = """\
<?xml version="1.0" encoding="utf-8" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
	<title>{name}</title>
	<link rel="self" href="{src}" />
	<id>tag:devutopia.net,2013-09-22:helloworldfeed</id>
	<!--<description>{descript}</description>-->
	{items}
</feed>\
"""

rss_item = """\
<entry>
	<title>{descript}</title>
	<id>tag:devutopia.net,{id}</id>
	<link>{url}</link>
	<description>{msg}</description>
	<pubDate>{date}</pubDate>
</entry>"""  # TODO: Also make so that, if {msg} has more than one line, then it automatically becomes a block (tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting)


class HTTPException(Exception):

	def __init__(self, code, msg):
		self.code = code
		self.msg = msg
		super().__init__(code)

	def __call__(self, environ):
		self.msg = self.msg.format_map(
			DynamicMapping(environ, strict=False, safe=True))

		return self

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


class NotStrictList(list):  # TODO: Use it!? Maybe improving it first (+ see Args class)
	""" Allows to normalize data automatically when testing for the presence of some data in that list. """
	# TODO: Should/could it be about sequences in general?

	defaultNormalizer = operator.methodcaller('lower')

	def __contains__(self, item, strict=False, normalizer=None):
		if strict:
			return super().__contains__(item)

		if normalizer is None:
			normalizer = NotStrictList.defaultNormalizer

		return normalizer(item) in map(normalizer, self)


# TODO: Finish it too…
# Will probably be used to automatically do what is needed for args and post? (for instance changing them into a dict of NonStrictList?)
class Args(dict):

	def __init__(self, args):
		pass


class HTTPManager:
	"""
	WSGI HTTP Managing Utility tool
	"""

	status = '200 OK'

	headers = {
		'Content-Type': 'text/html; charset=utf-8',

		# TODO: Idea: Make so that when editting Content-Type
		# it automatically becomes '{content-type}; charset={charset}'
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
	"""
	Main WSGI app
	"""
	# TODO: Change the docstring? Call it "presentation" or "homepage"? Or let it be the "Helloworld app" even though it will probably eventually not be the "homepage app" anymore? (Maybe create the "homepage app" and set it so "homepage_app = hello_world_app"?)

	def __init__(self, environ, start_response):
		self.environ = environ
		self.start_response = start_response

		self.http = HTTPManager(start_response)

	# TODO: Handle the two methods below by the class Args?
	@cached_property
	def args(self):
		return collections.defaultdict(list, urllib.parse.parse_qs(self.environ['QUERY_STRING']))

	@cached_property
	def post(self):
		return collections.defaultdict(list, urllib.parse.parse_qs(self.environ['wsgi.input'].readline().decode('UTF-8'), True) if self.environ["REQUEST_METHOD"] == 'POST' else {})

	def __iter__(self):
		try:
			# As "yield from" is only avaible from Python 3.3, this is done manually

			# TODO: We can't put that in a decorator right? I think I tried and finished with that only solution: __iter__ is kind of the decorator for self.main

			mainGen = self.main()

			firstItem = next(mainGen)

			# Default commit (if none has been sent yet)
			self.http.commit()

			# Note: I don't think anything is *sent back* (generator.send and "foo = (yield bar)") to the main app generator (by WSGI itself), so I don't handle that here…
			yield firstItem.encode('utf-8')

			for el in mainGen:
				yield el.encode('utf-8')

		except HTTPException as HTTP_exception:
			HTTPManager(self.start_response).exception(HTTP_exception)

			yield HTTP_exception(self.environ).msg.encode('utf-8')

	def main(self):
		if self.environ['PATH_INFO'].rstrip('/') != '':
			raise HTTPException.error404

		if 'RSS' in map(operator.methodcaller('upper'), self.args['do']):  # In the future, will use NotStrictList class.
			self.http.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'

			# TODO: Finish to generate RSS automatically
			yield BetterFormat().format(rss_template,
										name='Hello World',
										src='http://devutopia.net/helloworld.py?do=RSS',
										descript='Hello World in several langages',
										items=BetterFormat().format(rss_item,
											descript='[fr] Bonjour tout le monde',
											id='2013-09-22:helloworldentry-in_french-by_devutopia',
											url='http://devutopia.net/helloworld.py?itemid=1',
											msg='French version.<br />\nAdded by devutopia.',  # TODO: Should automatically aligns on two lines (see tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting)
											date='2013-09-22')
										)

			raise StopIteration

		# yield __import__('sys').version+'<br />'
		# yield __import__('sqlite3').dbapi2.sqlite_version # → Not the one I would have hoped for (but not required anyway)

		minutes = int(time.mktime(datetime.datetime.now().timetuple())/60 - time.mktime(started_on.timetuple())/60) # Timestamp in minutes of now minus timestamp of minutes since when that instance started

		yield BetterFormat().format(template,
			# test=test.format(get=cgi.escape(str(self.args)), post=cgi.escape(str(self.post)), method=cgi.escape(self.environ["REQUEST_METHOD"])),
			# test='Nothing to see here 😒',
			# TODO: Should be put in the test variable? (helloworld.py scope)
			# TODO: Should also automatically forms a block, right? (See: tag:devutopia.net,2013-10-05:Improve-auto-identation-formatting )
			test='<b>Instance name:</b> {name}<br /><b>Started {minutes} minute{s} ago.</b>'.format(name=cgi.escape(instance_name), minutes=minutes, s='s'*(minutes > 1)))   # +'<br /><strong>Environ:</strong>'+cgi.escape(str(self.environ)).replace(',', ',<br />\n'),

if __name__ == '__main__':
	# Then run wsgiref for local testing
	# → I don't know if wsgiref handles multiple instances (and if so, by its own) (→ I guess/hope so) # TODO: Investiguate
	# → I don't know if I have to handle the request myself if using wsgiref (→ Yep, see answer below)

	# Answer: "If you want to serve multiple applications on a single host and port, you should create a WSGI application that parses PATH_INFO to select which application to invoke for each request. (E.g., using the shift_path_info() function from wsgiref.util.)"

	from wsgiref.simple_server import make_server

	httpd = make_server('', 8000, application)

	print('Launching the server in local mode... Hello!')  # Can't use "…" in case of Windows, because Windows is stupid. I said it. UTF-8 isn't yet handle by everyone in 2013… That's sad, isn't it? (Or you can "modify" the Windows environnement but it's not a good idea and not perfect)

	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print('Shuting down... Good bye!')
