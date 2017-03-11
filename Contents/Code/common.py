#!/usr/bin/env python

import einthusan

################################################################################
TITLE = "Einthusan"
VERSION = '0.14' # Release notation (x.y - where x is major and y is minor)
GITHUB_REPOSITORY = 'coder-alpha/Einthusan.bundle'
PREFIX = "/video/einthusan"
################################################################################

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0"

# SSL Web Proxy
PROXY_URL = "https://ssl-proxy.my-addr.org/myaddrproxy.php/"
PROXY_PART1 = "/myaddrproxy.php/https/einthusan.tv/"
PROXY_PART1_REPLACE = "/"
PROXY_PART2A = "/myaddrproxy.php/https/"
PROXY_PART2B = "/myaddrproxy.php/http/"
PROXY_PART2_REPLACE = "//"

######################################################################################
@route(PREFIX + "/GetPageElements")
def GetPageElements(url, headers=None, **kwargs):

	page_data_elems = None
	try:
		page_data_string = GetPageAsString(url=url, headers=headers)
		page_data_elems = HTML.ElementFromString(page_data_string)
	except:
		pass

	return page_data_elems
	
######################################################################################
@route(PREFIX + "/GetPageAsString")
def GetPageAsString(url, headers=None, timeout=15, **kwargs):

	page_data_string = None
	try:
		if Prefs["use_https_alt"]:
			if Prefs["use_debug"]:
				Log("Using SSL Alternate Option")
				Log("Url: " + url)
			page_data_string = einthusan.requestWithHeaders(url = url)
		elif Prefs["use_proxy"]:
			if Prefs["use_debug"]:
				Log("Using SSL Web-Proxy Option")
				Log("Url: " + url)
				
			if headers == None:
				page_data_string = HTTP.Request(PROXY_URL + url, timeout=timeout).content
			else:
				page_data_string = HTTP.Request(PROXY_URL + url, headers=headers, timeout=timeout).content
			page_data_string = page_data_string.replace(PROXY_PART1, PROXY_PART1_REPLACE)
			page_data_string = page_data_string.replace(PROXY_PART2A, PROXY_PART2_REPLACE)
			page_data_string = page_data_string.replace(PROXY_PART2B, PROXY_PART2_REPLACE)
		else:
			if headers == None:
				page_data_string = HTTP.Request(url, timeout=timeout).content
			else:
				page_data_string = HTTP.Request(url, headers=headers, timeout=timeout).content
	except Exception as e:
		Log('ERROR common.py>GetPageAsString: %s URL: %s' % (e.args,url))
		pass
		
	return page_data_string
	
#########################################################################################################
