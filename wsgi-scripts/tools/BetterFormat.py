#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string
import re


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

		def extractTabs(pattern):
			sharedData['numberOfTabs'] = int(pattern.group(0)[:-1])
			return ""

		pattern = re.sub('[0-9]+\t', extractTabs, pattern)

		if sharedData['numberOfTabs']:  # If there are tabs to be added
			v = (sharedData['numberOfTabs'] * '\t').join(v.splitlines(True))

		return super().format_field(v, pattern)
