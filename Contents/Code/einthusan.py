#!/usr/bin/env python

#
# Adapted by Coder-Alpha:
# Credits to SHANI08 (Kodi Addon developer)
# https://github.com/Shani-08
#

import cookielib, urllib, urllib2, re, base64, json, sys
import HTMLParser

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0"

def decodeEInth(lnk):
	t=10
	#var t=10,r=e.slice(0,t)+e.slice(e.length-1)+e.slice(t+2,e.length-1)
	r=lnk[0:t]+lnk[-1]+lnk[t+2:-1]
	return r
	
def encodeEInth(lnk):
	t=10
	#var t=10,r=e.slice(0,t)+e.slice(e.length-1)+e.slice(t+2,e.length-1)
	r=lnk[0:t]+lnk[-1]+lnk[t+2:-1]
	return r
	
def request(url, cookieJar=None, post=None, timeout=20, headers=None, jsonpost=False, https_skip=False):

	cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
	
	if sys.version_info < (2, 7, 9): raise Exception()
	import ssl; ssl_context = ssl.create_default_context()
	ssl_context.check_hostname = False
	ssl_context.verify_mode = ssl.CERT_NONE
	if https_skip == True:
		opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
	else:
		opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ssl_context), cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
	
	header_in_page=None
	if '|' in url:
		url,header_in_page=url.split('|')
	req = urllib2.Request(url)
	req.add_header('User-Agent',USER_AGENT)
	if headers:
		for h,hv in headers:
			req.add_header(h,hv)
	if header_in_page:
		header_in_page=header_in_page.split('&')
		
		for h in header_in_page:
			if len(h.split('='))==2:
				n,v=h.split('=')
			else:
				vals=h.split('=')
				n=vals[0]
				v='='.join(vals[1:])
				#n,v=h.split('=')
			#print n,v
			req.add_header(n,v)
			
	if jsonpost:
		req.add_header('Content-Type', 'application/json')
	response = opener.open(req,post,timeout=timeout)
	if response.info().get('Content-Encoding') == 'gzip':
			from StringIO import StringIO
			import gzip
			buf = StringIO( response.read())
			f = gzip.GzipFile(fileobj=buf)
			link = f.read()
	else:
		link=response.read()
	response.close()
	
	return link
	
def parseUrl(url):
	id = url.split('watch/')[1].split('/')[0]
	lang = url.split('lang=')[1]
	
	return id, lang
	
def requestWithHeaders(url):
	cookieJar = cookielib.LWPCookieJar()	
	headers=[('Origin','https://einthusan.tv'),('Referer','https://einthusan.tv/movie/browse/?lang=hindi'),('User-Agent',USER_AGENT)]
	htm=request(url,headers=headers,cookieJar=cookieJar)
	return htm

def GetEinthusanData(url, debug=False):
	
	try:
		id,lang = parseUrl(url)
		cookieJar = cookielib.LWPCookieJar()
		
		headers=[('Origin','https://einthusan.tv'),('Referer','https://einthusan.tv/movie/browse/?lang=hindi'),('User-Agent',USER_AGENT)]
		mainurl='https://einthusan.tv/movie/watch/%s/?lang=%s'%(id,lang)
		mainurlajax='https://einthusan.tv/ajax/movie/watch/%s/?lang=%s'%(id,lang)
		
		htm=request(mainurl,headers=headers,cookieJar=cookieJar)
		
		lnk=re.findall('data-ejpingables=["\'](.*?)["\']',htm)[0]#.replace('&amp;','&')

		jdata='{"EJOutcomes":"%s","NativeHLS":false}'%lnk
		
		gid = re.findall('data-pageid=["\'](.*?)["\']',htm)[0]
		h = HTMLParser.HTMLParser()
		gid = h.unescape(gid).encode("utf-8")
		
		postdata={'xEvent':'UIVideoPlayer.PingOutcome','xJson':jdata,'arcVersion':'3','appVersion':'59','gorilla.csrf.Token':gid}
		postdata = urllib.urlencode(postdata)
		rdata=request(mainurlajax,headers=headers,post=postdata,cookieJar=cookieJar)
		
		r=json.loads(rdata)["Data"]["EJLinks"]
		data=(base64.b64decode(decodeEInth(r)))

		return data
	except Exception as err:
		return "error-fail - code execution error - %s, url - %s" % (str(err), url)
 
	
def Test():
	url = 'https://einthusan.tv/movie/watch/9097/?lang=hindi'
	d = GetEinthusanData(url=url,)
	d = json.loads(d)
	print (d)

def Test2():
	url = 'https://einthusan.tv'
	d = requestWithHeaders(url=url)
	print (d)