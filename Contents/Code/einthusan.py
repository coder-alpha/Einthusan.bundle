#!/usr/bin/env python

#
# Adapted by Coder-Alpha:
# Credits to SHANI08 (Kodi Addon developer)
# https://github.com/Shani-08
#

import cookielib, urllib, urllib2, re, base64, json
import common
import HTMLParser

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
	
def getUrl(url, cookieJar=None,post=None, timeout=20, headers=None,jsonpost=False):
	cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
	opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
	header_in_page=None
	if '|' in url:
		url,header_in_page=url.split('|')
	req = urllib2.Request(url)
	req.add_header('User-Agent',common.USER_AGENT)
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

def GetEinthusanData(url, debug=False, useProxy=False):
	
	try:
		id,lang = parseUrl(url)
		cookieJar = cookielib.LWPCookieJar()
		
		headers=[('Origin','https://einthusan.tv'),('Referer','https://einthusan.tv/movie/browse/?lang=hindi'),('User-Agent',common.USER_AGENT)]
		mainurl='https://einthusan.tv/movie/watch/%s/?lang=%s'%(id,lang)
		mainurlajax='https://einthusan.tv/ajax/movie/watch/%s/?lang=%s'%(id,lang)
		
		htm=getUrl(mainurl,headers=headers,cookieJar=cookieJar)
		
		lnk=re.findall('data-ejpingables=["\'](.*?)["\']',htm)[0]#.replace('&amp;','&')

		jdata='{"EJOutcomes":"%s","NativeHLS":false}'%lnk
		
		gid = re.findall('data-pageid=["\'](.*?)["\']',htm)[0]
		h = HTMLParser.HTMLParser()
		gid = h.unescape(gid).encode("utf-8")
		
		postdata={'xEvent':'UIVideoPlayer.PingOutcome','xJson':jdata,'arcVersion':'3','appVersion':'59','gorilla.csrf.Token':gid}
		postdata = urllib.urlencode(postdata)
		rdata=getUrl(mainurlajax,headers=headers,post=postdata,cookieJar=cookieJar)
		#print rdata
		
		r=json.loads(rdata)["Data"]["EJLinks"]
		data=(base64.b64decode(decodeEInth(r)))

		return data
	except Exception as err:
		return "error-fail - code execution error - %s, url - %s" % (str(err), url)
 
	
def Test(url, debug=False, useProxy=False):
	d = GetEinthusanData(url=url, debug=debug, useProxy=useProxy)
	d = json.loads(d)
	print (d)

#Test(url = 'https://einthusan.tv/movie/watch/9097/?lang=hindi', debug=True, useProxy=True)
