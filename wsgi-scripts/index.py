#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @author: JeromeJ
# @contact: e-warning [at] hotmail [dot] com
# @website: http://www.olissea.com/

def application(environ, start_response):
	status = '200 OK'

	response_headers = [
		('Content-type', 'text/html; charset=utf-8'),
	]

	start_response(status, response_headers)

	return [__import__('sys').version.encode('utf-8')]
