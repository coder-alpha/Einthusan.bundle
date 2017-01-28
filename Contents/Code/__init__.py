######################################################################################
#
#	Einthusan.com / Einthusan.tv
#
######################################################################################

import common, updater, urllib2, time, sys, random
import slimerjs, json

TITLE = common.TITLE
PREFIX = common.PREFIX
ART = "art-default.jpg"
ICON = "icon-einthusan.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_SEARCH_QUEUE = "icon-search-queue.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
ICON_UPDATE = "icon-update.png"
ICON_UPDATE_NEW = "icon-update-new.png"
ICON_UNAV = "icon-unav.png"
ICON_PREFS = "icon-prefs.png"
ICON_LANG = "icon-lang.png"
ICON_SOURCES = "icon-sources.png"
BASE_URL = "https://einthusan.tv"
SEARCH_URL = "https://einthusan.tv/search/"
PROXY_URL = "https://ssl-proxy.my-addr.org/myaddrproxy.php/"
PROXY_PART = "/myaddrproxy.php/https/"
PROXY_PART_REPLACE = "//"
PROXY_PART2 = "/myaddrproxy.php/https/einthusan.tv/"
PROXY_PART2_REPLACE = "/"
LAST_PROCESSED_URL = []
VideoURL = {}
EINTHUSAN_SERVERS = ["Dallas","Washington","San Jose","Somerville","Toronto","London","Sydney"]
EINTHUSAN_SERVER_INFO = {}
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0"
SLIMERJS_INIT = []


######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = USER_AGENT
	HTTP.Headers['Referer'] = BASE_URL
	
	LAST_PROCESSED_URL = []
	VideoURL = {}
	
	# Initialize Server Info Thread once
	Thread.Create(AddSourceInfo)
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	if len(SLIMERJS_INIT) == 0:
		# Initialize SlimerJS module once for faster load times
		Thread.Create(initSlimerJS)
		SLIMERJS_INIT.append('True')
	
	defaultLang = Prefs['langPref']
	
	oc = ObjectContainer(title2=TITLE)

	oc.add(DirectoryObject(key = Callback(SortMenu, lang = defaultLang), title = defaultLang.title() + ' Movies', thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(SetLanguage), title = 'Movies (Language Menu)', thumb = R(ICON_LANG)))
	
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Movie Bookmarks"), title = "Bookmarks", thumb = R(ICON_QUEUE)))
	
	oc.add(InputDirectoryObject(key = Callback(Search, lang = defaultLang, page_count=1), title='Search', summary='Search Movies', prompt='Search for...', thumb = R(ICON_SEARCH)))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue'), title = 'Search Queue', summary='Search using saved search terms', thumb = R(ICON_SEARCH_QUEUE)))
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	if updater.update_available()[0]:
		oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (New Available)', thumb = R(ICON_UPDATE_NEW)))
	else:
		oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (Running Latest)', thumb = R(ICON_UPDATE)))
	
	return oc
	
@route(PREFIX + "/setlanguage")
def SetLanguage():
	
	oc = ObjectContainer(title2='Select Language')
	
	if Prefs["use_proxy"]:
		page_elems = HTML.ElementFromURL(PROXY_URL + BASE_URL + "/intro/")
	else:
		page_elems = HTML.ElementFromURL(BASE_URL + "/intro/")
	
	blocks = page_elems.xpath(".//div[@class='block1']//ul")
	for block in blocks:
		langblock = block.xpath(".//li")
		for langsq in langblock:
			lang = langsq.xpath(".//p//text()")[0]
			lang_img = "http:" + langsq.xpath(".//img//@src")[0].replace(PROXY_PART, PROXY_PART_REPLACE)
			oc.add(DirectoryObject(key = Callback(SortMenu, lang = lang.lower()), title = lang, thumb = Resource.ContentsOfURLWithFallback(url = lang_img, fallback='MoviePosterUnavailable.jpg')))
	
	return oc

@route(PREFIX + "/sortMenu")
def SortMenu(lang, **kwargs):

	cats1 = ['Hot Picks']
	cats2 = ['Staff Picks', 'Recently Added']
	cats3 = ['Number or Alphabet']
	cats4 = ['Year']
	cats5 = ['Coming Soon','Regional Hits']
	oc = ObjectContainer(title2='Sort ' + lang.title() + ' Movies By')
	for cat in cats1:
		oc.add(DirectoryObject(key = Callback(SortMenuHotPicks, lang=lang, cat=cat), title = cat, thumb = R(ICON_LIST)))
	for cat in cats2:
		oc.add(DirectoryObject(key = Callback(PageDetail, lang=lang, cat=cat), title = cat, thumb = R(ICON_LIST)))
	for cat in cats3:
		oc.add(DirectoryObject(key = Callback(SortMenuAlphabets, lang=lang, cat=cat), title = cat, thumb = R(ICON_LIST)))
	for cat in cats4:
		oc.add(DirectoryObject(key = Callback(SortMenuYears, lang=lang, cat=cat), title = cat, thumb = R(ICON_LIST)))
	for cat in cats5:
		oc.add(DirectoryObject(key = Callback(PageDetail, lang=lang, cat=cat), title = cat, thumb = R(ICON_LIST)))
		
	oc.add(InputDirectoryObject(key = Callback(Search, lang = lang), title='Search', summary='Search Movies', prompt='Search for...', thumb = R(ICON_SEARCH)))
		
	return oc	

	
@route(PREFIX + "/sortmenuhotpicks")
def SortMenuHotPicks(lang, cat, **kwargs):

	oc = ObjectContainer(title2=cat.title())
	
	if Prefs["use_proxy"]:
		page_elems = HTML.ElementFromURL(PROXY_URL + BASE_URL + "/movie/browse/?lang="+lang)
	else:
		page_elems = HTML.ElementFromURL(BASE_URL + "/movie/browse/?lang="+lang)
	
	tabs = page_elems.xpath(".//section[@id='UIFeaturedFilms']//div[@class='tabview']")
	for block in tabs:
		loc = BASE_URL + block.xpath(".//div[@class='block1']//@href")[0].replace(PROXY_PART2, PROXY_PART2_REPLACE)
		thumb = "http:" + block.xpath(".//div[@class='block1']//@src")[0].replace(PROXY_PART, PROXY_PART_REPLACE)
		title = block.xpath(".//div[@class='block2']//a[@class='title']//text()")[0]
		summary = "Synopsis currently unavailable."
		oc.add(DirectoryObject(key = Callback(EpisodeDetail, title=title, url=loc), title = title, summary=summary, thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')))
		
	oc.add(InputDirectoryObject(key = Callback(Search, lang = lang), title='Search', summary='Search Movies', prompt='Search for...', thumb = R(ICON_SEARCH)))
		
	return oc
	
@route(PREFIX + "/sortmenualphabets")
def SortMenuAlphabets(lang, cat, **kwargs):

	oc = ObjectContainer(title2=cat.title())
	
	if Prefs["use_proxy"]:
		page_elems = HTML.ElementFromURL(PROXY_URL + BASE_URL + "/movie/browse/?lang="+lang)
	else:
		page_elems = HTML.ElementFromURL(BASE_URL + "/movie/browse/?lang="+lang)
	
	tabs = page_elems.xpath(".//section[@id='UIMovieFinder']//div[@class='tabview'][1]//div[@class='innertab simpletext']//a")
	for block in tabs:
		url = BASE_URL + block.xpath(".//@href")[0]
		title = block.xpath(".//text()")[0]
		oc.add(DirectoryObject(key = Callback(PageDetail, lang=lang, cat=cat, key=title), title = title))
		
	oc.add(InputDirectoryObject(key = Callback(Search, lang = lang), title='Search', summary='Search Movies', prompt='Search for...', thumb = R(ICON_SEARCH)))
		
	return oc
	
@route(PREFIX + "/sortmenuyears")
def SortMenuYears(lang, cat, **kwargs):

	oc = ObjectContainer(title2=cat.title())
	
	if Prefs["use_proxy"]:
		page_elems = HTML.ElementFromURL(PROXY_URL + BASE_URL + "/movie/browse/?lang="+lang)
	else:
		page_elems = HTML.ElementFromURL(BASE_URL + "/movie/browse/?lang="+lang)
	
	tabs = page_elems.xpath(".//section[@id='UIMovieFinder']//div[@class='tabview'][2]//div[@class='innertab simpletext'][position()>1]//a")
	for block in tabs:
		url = BASE_URL + block.xpath(".//@href")[0]
		title = block.xpath(".//text()")[0]
		oc.add(DirectoryObject(key = Callback(PageDetail, lang=lang, cat=cat, key=title), title = title))
		
	oc.add(InputDirectoryObject(key = Callback(Search, lang = lang), title='Search', summary='Search Movies', prompt='Search for...', thumb = R(ICON_SEARCH)))
		
	return oc

######################################################################################

@route(PREFIX + "/pagedetail")
def PageDetail(cat, lang, key="none", page_count="1", **kwargs):

	if cat == 'Staff Picks':
		url = BASE_URL + "/movie/results/?find=StaffPick&lang="+lang+"&page="+page_count
	elif cat == 'Recently Added':
		url = BASE_URL + "/movie/results/?find=Recent&lang="+lang+"&page="+page_count
	elif cat == 'Regional Hits':
		url = BASE_URL + "/movie/results/?find=RegionalHit&lang="+lang+"&page="+page_count
	elif cat == 'Coming Soon':
		url = BASE_URL + "/movie/results/?find=ComingSoon&lang="+lang+"&page="+page_count
	elif cat == 'Number or Alphabet':
		if key == 'Number':
			url = BASE_URL + "/movie/results/?find=Numbers&lang="+lang+"&page="+page_count
		else:
			url = BASE_URL + "/movie/results/?find=Alphabets&lang="+lang+"&alpha="+key+"&page="+page_count
	elif cat == 'Year':
			url = BASE_URL + "/movie/results/?find=Year&lang="+lang+"&year="+key+"&page="+page_count
	
	oc = ObjectContainer(title2=cat.title() + " (Page" + page_count + ")")
	
	if Prefs["use_proxy"]:
		page_elems = HTML.ElementFromURL(PROXY_URL + url)
	else:
		page_elems = HTML.ElementFromURL(url)
	
	movies = page_elems.xpath(".//section[@id='UIMovieSummary']/ul/li")
	for block in movies:
		loc = BASE_URL + block.xpath(".//div[@class='block1']//@href")[0].replace(PROXY_PART2, PROXY_PART2_REPLACE)
		thumb = "http:" + block.xpath(".//div[@class='block1']//@src")[0].replace(PROXY_PART, PROXY_PART_REPLACE)
		title = block.xpath(".//div[@class='block2']//a[@class='title']//text()")[0]
		try:
			summary = block.xpath(".//p[@class='synopsis']//text()")[0]
			if summary == None or summary == "":
				summary = "Synopsis currently unavailable."
		except:
			summary = "Synopsis currently unavailable."
		try:
			profs = block.xpath(".//div[@class='professionals']//div[@class='prof']")
			for prof in profs:
				summary += "\n "
				summary += prof.xpath(".//label//text()")[0] + " : " + prof.xpath(".//p//text()")[0]
		except:
			pass
		if cat == 'Coming Soon':
			oc.add(DirectoryObject(key = Callback(ComingSoon, title=title), title = title, summary=summary, thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')))
		else:
			oc.add(DirectoryObject(key = Callback(EpisodeDetail, title=title, url=loc), title = title, summary=summary, thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')))
		
	curr_page = int(page_elems.xpath(".//div[@class='pagination']//span[@class='active']//text()")[0])
	last_page = int(page_elems.xpath("(.//div[@class='pagination']//span//text())[last()]")[0])
	if last_page > curr_page:
		oc.add(DirectoryObject(key = Callback(PageDetail, lang=lang, cat=cat, key=key, page_count=int(page_count)+1), title = "Next Page >>", thumb = R(ICON_NEXT)))
		
	oc.add(InputDirectoryObject(key = Callback(Search, lang = lang), title='Search', summary='Search Movies', prompt='Search for...', thumb = R(ICON_SEARCH)))
		
	return oc

@route(PREFIX + "/comingsoon")
def ComingSoon(title, **kwargs):
	return ObjectContainer(header=title, message=title + ' will be Available Soon')

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, **kwargs):
	
	Thread.Create(GetVideoUrl,{},url)
	
	if Prefs["use_proxy"]:
		page_elems = HTML.ElementFromURL(PROXY_URL + url)
	else:
		page_elems = HTML.ElementFromURL(url)
	
	try:
		thumb = "http:" + page_elems.xpath(".//section[@id='UIMovieSummary']//div[@class='block1']//@src")[0].replace(PROXY_PART, PROXY_PART_REPLACE)
	except:
		thumb = None
	try:
		summary = page_elems.xpath(".//section[@id='UIMovieSummary']//p[@class='synopsis']//text()")[0]
	except:
		summary = "Synopsis currently unavailable."
	try:
		year = str(page_elems.xpath(".//section[@id='UIMovieSummary']//div[@class='info']//p[1]//text()")[0])
	except:
		year = 0000
	try:
		ratings = page_elems.xpath(".//section[@id='UIMovieSummary']//ul[@class='average-rating']//p//text()")
		rating = float(0.0)
		for rate in ratings:
			rating += float(rate)
		rating = rating * 10/25
	except:
		rating = float(0.0)
	try:
		profs = page_elems.xpath(".//section[@id='UIMovieSummary']//div[@class='professionals']//div[@class='prof']")
		for prof in profs:
			summary += "\n "
			summary += prof.xpath(".//label//text()")[0] + " : " + prof.xpath(".//p//text()")[0]
	except:
		pass
		
	trailer_urls = page_elems.xpath(".//section[@id='UIMovieSummary']//div[@class='extras']//@href")
	for trailer_u in trailer_urls:
		if 'youtube' in trailer_u:
			trailer = trailer_u.replace("/myaddrproxy.php/https/", "http://")
	
	title = title
	oc = ObjectContainer(title1 = unicode(title), art=thumb)
	art = thumb
	
	timer = 0
	while VideoURL['GetVideoUrlComplete'] == 'False':
		time.sleep(1)
		timer += 1
		if timer > 20: # using 20 sec. timeout
			return ObjectContainer(header=title, message=title + ' : Timeout error occurred !')
		
	furl = VideoURL['GetVideoUrlComplete']
	datacenter = VideoURL['GetVideoUrlDatacenter']
	# fix San Jose datacenter label
	if datacenter == 'San':
		datacenter = 'San Jose'
	
	if 'error-fail' in furl:
		return ObjectContainer(header=title, message=title + ' could not be fetched !')
		
	server_n = DetermineCurrentServer(furl, datacenter)
	try:
		oc.add(VideoClipObject(
			url = "einthusan://" + E(JSON.StringFromObject({"url":furl, "title": title, "summary": summary, "thumb": thumb, "year": year, "rating": rating})),
			art = art,
			title = title + " (via " + datacenter + " Server ID:" + server_n + ")",
			thumb = thumb,
			summary = summary
			)
		)
	except:
		url = ""
		
	furl2, server_n2, ret_code = AvailableSourceFrom(furl, Prefs["locationPref"])
	if ret_code == "200":
		#server_n2 = DetermineCurrentServer(furl2, Prefs["locationPref"])
		try:
			oc.add(VideoClipObject(
				url = "einthusan://" + E(JSON.StringFromObject({"url":furl2, "title": title, "summary": summary, "thumb": thumb, "year": year, "rating": rating})),
				art = art,
				title = title + " (via " + Prefs["locationPref"] + " Server ID:" + server_n2 + ")",
				thumb = thumb,
				summary = summary
				)
			)
		except:
			url = ""
		
	try:
		oc.add(VideoClipObject(
			url = trailer,
			art = art,
			title = title + " (Trailer)",
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg'),
			summary = summary
			)
		)
	except:
		trailer = ""
		
	oc.add(DirectoryObject(
			key = Callback(AllAvailableSources, furl=furl, title=title, summary=summary, thumb=thumb, year=year, rating=rating, art=art),
			title = "Other Servers Available",
			art = art,
			summary = "Play using a different server",
			thumb = R(ICON_SOURCES)
		)
	)
	
	if Check(title=title,url=url):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = url),
			title = "Remove Bookmark",
			art = art,
			summary = 'Removes the current movie from the Boomark que',
			thumb = R(ICON_QUEUE)
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = url),
			title = "Bookmark Video",
			summary = 'Adds the current movie to the Boomark que',
			art = art,
			thumb = R(ICON_QUEUE)
		)
	)

	return oc
		
# Initialize SlimerJS and dependencies at startup for faster load time later in use	
def initSlimerJS():		
	Log("Initializing SlimerJS")
	python_dir = Prefs['python_dir']
	firefox_dir = Prefs['firefox_dir']
	Log("Prefs:")
	if python_dir == None:
		python_dir = ""
	if firefox_dir == None:
		firefox_dir = ""
	Log("OS: " + sys.platform)
	Log("Python directory: " + python_dir)
	Log("Firefox directory: " + firefox_dir)
	res = slimerjs.einthusan(python_dir=python_dir, firefox_dir=firefox_dir, url="https://einthusan.tv")
	if res == "":
		res = "Success"
	Log("Initialized SlimerJS: " + res)
	
@route(PREFIX + "/GetVideoUrl")
def GetVideoUrl(url):
	Log("Running SlimerJS routine for : " + url)
	VideoURL['GetVideoUrlComplete'] = 'False'
	furl = 'error-fail'
	datacenter = 'Unknown'
	debug = Prefs['use_debug']
	
	if url not in LAST_PROCESSED_URL:
		del LAST_PROCESSED_URL[:]
		#Log(url)
		python_dir = Prefs['python_dir']
		firefox_dir = Prefs['firefox_dir']
		res = slimerjs.einthusan(python_dir=python_dir, firefox_dir=firefox_dir, url=url, debug=debug)
		if 'error-fail' not in res and 'MP4Link' in res:
			try:
				res2 = "{" + find_between( res, "{", "}" ) + "}"
				res2 = json.loads(res2)
				furl = res2['MP4Link']
				datacenter = res2["Datacenter"]
				#Log("vidfile: " + furl)
				LAST_PROCESSED_URL.append(url)
				LAST_PROCESSED_URL.append(furl)
				LAST_PROCESSED_URL.append(datacenter)
				if debug:
					Log(res)
			except:
				Log(res)
		else:
			Log(res)
	else:
		furl = LAST_PROCESSED_URL[1]
		datacenter = LAST_PROCESSED_URL[2]
		
	# fix San Jose datacenter label
	if datacenter == 'San':
		datacenter = 'San Jose'
	VideoURL['GetVideoUrlComplete'] = furl
	VideoURL['GetVideoUrlDatacenter'] = datacenter

@route(PREFIX + "/AllAvailableSources")
def AllAvailableSources(furl, title, summary, thumb, year, rating, art):
	
	oc = ObjectContainer(title1 = unicode(title), art=thumb)	

	for location in EINTHUSAN_SERVERS:
		location_with_state_country = location
		if EINTHUSAN_SERVER_INFO[location]["State"] != "":
			location_with_state_country += " (" + EINTHUSAN_SERVER_INFO[location]["State"] + ") - " + EINTHUSAN_SERVER_INFO[location]["Country"]
		else:
			location_with_state_country += " - " + EINTHUSAN_SERVER_INFO[location]["Country"]
		oc.add(DirectoryObject(
			key = Callback(AllAvailableSources2, furl=furl, title=title, summary=summary, thumb=thumb, year=year, rating=rating, art=art, location=location),
			title = location_with_state_country,
			art = art,
			summary = "Play using " + location_with_state_country + " server",
			thumb = EINTHUSAN_SERVER_INFO[location]["Flag"]
			)
		)
		
	return oc	
	
@route(PREFIX + "/AllAvailableSources2")
def AllAvailableSources2(furl, title, summary, thumb, year, rating, art, location):
	
	oc = ObjectContainer(title1 = unicode(title), art=thumb)	
	vidpath = furl.split('.tv/')[1]

	for idx in EINTHUSAN_SERVER_INFO[location]["Servers"]:
		furl = ("https://s" + str(idx) + ".einthusan.tv/" + vidpath)
		ret_code = GetHttpStatus(url=furl)
		if ret_code == "200":
			oc.add(VideoClipObject(
				url = "einthusan://" + E(JSON.StringFromObject({"url":furl, "title": title, "summary": summary, "thumb": thumb, "year": year, "rating": rating})),
				art = art,
				title = unicode(title + " (Server ID:" + str(idx) + ")"),
				thumb = thumb,
				summary = summary
				)
			)
	return oc
	
@route(PREFIX + "/AvailableSourceFrom")
def AvailableSourceFrom(furl, location):

	# fix San Jose datacenter label
	if location == 'San':
		location = 'San Jose'
	
	try:
		vidpath = furl.split('.tv/')[1]
		choice_str = str(random.choice(EINTHUSAN_SERVER_INFO[location]["Servers"]))
	except:
		choice_str = '1'
		
	url = ("https://s" + choice_str + ".einthusan.tv/" + vidpath)
	ret_code = GetHttpStatus(url=url)
	
	return url, choice_str, ret_code

@route(PREFIX + "/DetermineCurrentServer")
def DetermineCurrentServer(furl, location):
	server_n = furl.split('.einthusan.tv')[0].strip('https://s')
	
	# fix San Jose datacenter label
	if location == 'San':
		location = 'San Jose'
	
	try:
		for idx in EINTHUSAN_SERVER_INFO[location]["Servers"]:
			if idx == int(server_n):
				return str(idx)
	except:
		pass
	
	Log("Unknown Server: Wrong assignment in constant EINTHUSAN_SERVER_INFO")
	Log(location)	
	Log(server_n)
	return "Unknown"
	
def AddSourceInfo():
	US_FLAG = "https://cdn4.iconfinder.com/data/icons/popular-flags-1/614/2_-_United_States-512.png"
	UK_FLAG = "https://cdn4.iconfinder.com/data/icons/flat-flags-part-one/512/GreatBritain512x512.png"
	CAN_FLAG = "https://cdn4.iconfinder.com/data/icons/flat-flags-part-one/512/Canada512x512.png"
	AUS_FLAG = "https://cdn4.iconfinder.com/data/icons/flat-flags-part-one/512/Australia512x512.png"
	
	EINTHUSAN_SERVER_INFO["Dallas"] = {}
	EINTHUSAN_SERVER_INFO["Dallas"]["Servers"]=[23,24,25,29,30,31,35,36,37,38,45]
	EINTHUSAN_SERVER_INFO["Dallas"]["Country"]="US"
	EINTHUSAN_SERVER_INFO["Dallas"]["State"]="TX"
	EINTHUSAN_SERVER_INFO["Dallas"]["Flag"]=US_FLAG
	
	EINTHUSAN_SERVER_INFO["Washington"] = {}
	EINTHUSAN_SERVER_INFO["Washington"]["Servers"]=[1,2,3,4,5,6,7,8,9,10,11,13,41,44]
	EINTHUSAN_SERVER_INFO["Washington"]["Country"]="US"
	EINTHUSAN_SERVER_INFO["Washington"]["State"]="D.C."
	EINTHUSAN_SERVER_INFO["Washington"]["Flag"]=US_FLAG
	
	EINTHUSAN_SERVER_INFO["San Jose"] = {}
	EINTHUSAN_SERVER_INFO["San Jose"]["Servers"]=[19,20,21,22,46]
	EINTHUSAN_SERVER_INFO["San Jose"]["Country"]="US"
	EINTHUSAN_SERVER_INFO["San Jose"]["State"]="CA"
	EINTHUSAN_SERVER_INFO["San Jose"]["Flag"]=US_FLAG
	
	EINTHUSAN_SERVER_INFO["Somerville"] = {}
	EINTHUSAN_SERVER_INFO["Somerville"]["Servers"]=[12]
	EINTHUSAN_SERVER_INFO["Somerville"]["Country"]="US"
	EINTHUSAN_SERVER_INFO["Somerville"]["State"]="MA"
	EINTHUSAN_SERVER_INFO["Somerville"]["Flag"]=US_FLAG
	
	EINTHUSAN_SERVER_INFO["Toronto"] = {}
	EINTHUSAN_SERVER_INFO["Toronto"]["Servers"]=[26,27]
	EINTHUSAN_SERVER_INFO["Toronto"]["Country"]="Canada"
	EINTHUSAN_SERVER_INFO["Toronto"]["State"]=""
	EINTHUSAN_SERVER_INFO["Toronto"]["Flag"]=CAN_FLAG
	
	EINTHUSAN_SERVER_INFO["London"] = {}
	EINTHUSAN_SERVER_INFO["London"]["Servers"]=[14,15,16,17,18,32,33,39,40,42]
	EINTHUSAN_SERVER_INFO["London"]["Country"]="UK"
	EINTHUSAN_SERVER_INFO["London"]["State"]=""
	EINTHUSAN_SERVER_INFO["London"]["Flag"]=UK_FLAG
	
	EINTHUSAN_SERVER_INFO["Sydney"] = {}
	EINTHUSAN_SERVER_INFO["Sydney"]["Servers"]=[28,34,43]
	EINTHUSAN_SERVER_INFO["Sydney"]["Country"]="Australia"
	EINTHUSAN_SERVER_INFO["Sydney"]["State"]=""
	EINTHUSAN_SERVER_INFO["Sydney"]["Flag"]=AUS_FLAG


def find_between( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title, **kwargs):

	oc = ObjectContainer(title1 = title)
	
	for each in Dict:
		url = Dict[each]
		#Log("url-----------" + url)
		if url.find(TITLE.lower()) != -1 and 'http' in url and '.mp4' not in url:
			if 'einthusan.com' in url:
				url = GetRedirector(url)
				Dict[each] = url
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = each, url = url),
				title = each,
				thumb = R(ICON_MOVIES)
				)
			)
		elif '.mp4' in url:
			Dict[each] = ""
	
	Dict.Save()
	
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
	
	if len(oc) == 1:
		return ObjectContainer(header=title, message='No Bookmarked Videos Available')
	return oc

######################################################################################
# Checks a show to the bookmarks list using the title as a key for the url
@route(PREFIX + "/checkbookmark")	
def Check(title, url, **kwargs):
	bool = False
	url = Dict[title]
	#Log("url-----------" + url)
	if url != None and (url.lower()).find(TITLE.lower()) != -1:
		bool = True
	
	return bool

######################################################################################
# Adds a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url, **kwargs):
	
	Dict[title] = url
	Dict.Save()
	return ObjectContainer(header=title, message='This movie has been added to your bookmarks.')
######################################################################################
# Removes a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, url, **kwargs):
	
	Dict[title] = 'removed'
	Dict.Save()
	return ObjectContainer(header=title, message='This movie has been removed from your bookmarks.')	
######################################################################################
# Clears the Dict that stores the bookmarks list
	
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	for each in Dict:
		if each.find(TITLE.lower()) != -1 and 'http' in each:
			Dict[each] = 'removed'
	Dict.Save()
	return ObjectContainer(header="Bookmarks", message='Your bookmark list will be cleared soon.')

######################################################################################
# Clears the Dict that stores the search list
	
@route(PREFIX + "/clearsearches")
def ClearSearches():

	for each in Dict:
		if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each:
			Dict[each] = 'removed'
	Dict.Save()
	return ObjectContainer(header="Search Queue", message='Your Search Queue list will be cleared soon.')
	
####################################################################################################
@route(PREFIX + "/search")
def Search(query, lang, page_count='1', **kwargs):
	
	title = query
	Dict[TITLE.lower() +'MyCustomSearch'+query] = query
	Dict[TITLE.lower() +'MyCustomSLang'+query] = lang
	Dict.Save()
	oc = ObjectContainer(title2='Search Results')
	
	url = (BASE_URL + '/movie/results/' + '?lang='+ lang + '&page=' + page_count + '&query=%s' % String.Quote(query, usePlus=True))
	if Prefs["use_proxy"]:
		page_elems = HTML.ElementFromURL(PROXY_URL + url)
	else:
		page_elems = HTML.ElementFromURL(url)

	movies = page_elems.xpath(".//section[@id='UIMovieSummary']/ul/li")
	for block in movies:
		loc = BASE_URL + block.xpath(".//div[@class='block1']//@href")[0].replace(PROXY_PART2, PROXY_PART2_REPLACE)
		thumb = "http:" + block.xpath(".//div[@class='block1']//@src")[0].replace(PROXY_PART, PROXY_PART_REPLACE)
		title = block.xpath(".//div[@class='block2']//a[@class='title']//text()")[0]
		try:
			summary = block.xpath(".//p[@class='synopsis']//text()")[0]
			if summary == None or summary == "":
				summary = "Synopsis currently unavailable."
		except:
			summary = "Synopsis currently unavailable."
		try:
			profs = block.xpath(".//div[@class='professionals']//div[@class='prof']")
			for prof in profs:
				summary += "\n "
				summary += prof.xpath(".//label//text()")[0] + " : " + prof.xpath(".//p//text()")[0]
		except:
			pass
		oc.add(DirectoryObject(key = Callback(EpisodeDetail, title=title, url=loc), title = title, summary=summary, thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')))
		
	curr_page = int(page_elems.xpath(".//div[@class='pagination']//span[@class='active']//text()")[0])
	last_page = int(page_elems.xpath("(.//div[@class='pagination']//span//text())[last()]")[0])
	if last_page > curr_page:
		oc.add(DirectoryObject(key = Callback(Search, lang=lang, query=query, page_count=int(page_count)+1), title = "Next Page >>", thumb = R(ICON_NEXT)))
		
	if len(oc) == 0:
		return ObjectContainer(header=title, message='No Videos Available')
	return oc
	

@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title, **kwargs):
	oc2 = ObjectContainer(title2='Search Using Term')
	#add a way to clear bookmarks list
	oc2.add(DirectoryObject(
		key = Callback(ClearSearches),
		title = "Clear Search Queue",
		thumb = R(ICON_SEARCH_QUEUE),
		summary = "CAUTION! This will clear your entire search queue list!"
		)
	)
	for each in Dict:
		query = Dict[each]
		#Log("each-----------" + each)
		#Log("query-----------" + query)
		if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each and query != 'removed':
			lang = Dict[TITLE.lower() +'MyCustomSLang'+query]
			if lang == None or lang == '':
				lang = Prefs['langPref']
			oc2.add(DirectoryObject(key = Callback(Search, query = query, lang = lang), title = query, thumb = R(ICON_SEARCH))
		)

	return oc2
####################################################################################################
@route(PREFIX + '/getredirector')
def GetRedirector(url, **kwargs):

	redirectUrl = url
	try:
		page = urllib2.urlopen(url)
		redirectUrl = page.geturl()
	except:
		redirectUrl = url
			
	#Log("Redirecting url ----- : " + redirectUrl)
	return redirectUrl
		
####################################################################################################
# Get HTTP response code (200 == good)
@route(PREFIX + '/gethttpstatus')
def GetHttpStatus(url):
	try:
		headers = {'User-Agent': USER_AGENT,
		   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		   'Accept-Encoding': 'none',
		   'Accept-Language': 'en-US,en;q=0.8',
		   'Connection': 'keep-alive',
		   'Referer': url}
	   
		if '|' in url:
			url_split = url.split('|')
			url = url_split[0]
			headers['Referer'] = url
			for params in url_split:
				if '=' in params:
					param_split = params.split('=')
					param = param_split[0].strip()
					param_val = urllib2.quote(param_split[1].strip(), safe='/=&')
					headers[param] = param_val

		if 'http://' in url or 'https://' in url:
			req = urllib2.Request(url, headers=headers)
			conn = urllib2.urlopen(req, timeout=10)
			resp = str(conn.getcode())
		else:
			resp = '200'
	except Exception as e:
		resp = '0'
		if Prefs['use_debug']:
			Log('Error > GetHttpStatus: ' + str(e))
			Log(url +' : HTTPResponse = '+ resp)
	return resp