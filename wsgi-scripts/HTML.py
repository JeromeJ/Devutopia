#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @author: JeromeJ
# @contact: e-warning [at] hotmail [dot] com
# @website: http://www.olissea.com/


class HTML:
	pass


def application(environ, start_reponse):
	start_reponse('200 OK', [('Content-type', 'text/html; charset=utf-8'), ])

	return ('This is a system page.<br /><br />Nothing to see here. 😒'.encode('utf-8'), )
