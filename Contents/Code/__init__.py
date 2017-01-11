######################################################################################
#
#	Einthusan.com / Einthusan.tv
#
######################################################################################

import common, updater, urllib
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
BASE_URL = "https://einthusan.tv"
SEARCH_URL = "https://einthusan.tv/search/"
LAST_PROCESSED_URL = []

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
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'
	HTTP.Headers['Referer'] = 'http://www.einthusan.tv'
	
	#BASE_URL = GetRedirector(BASE_R_URL)
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
	
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
		
	# Initialize SlimerJS module once for faster load times
	Thread.Create(initSlimerJS)
	
	return oc
	
@route(PREFIX + "/setlanguage")
def SetLanguage():
	
	oc = ObjectContainer(title2='Select Language')
	page_elems = HTML.ElementFromURL(BASE_URL + "/intro/")
	blocks = page_elems.xpath(".//div[@class='block1']//ul")
	for block in blocks:
		langblock = block.xpath(".//li")
		for langsq in langblock:
			lang = langsq.xpath(".//p//text()")[0]
			lang_img = "http:" + langsq.xpath(".//img//@src")[0]
			#Log(lang)
			#Log(lang_img)
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
	
	page_elems = HTML.ElementFromURL(BASE_URL + "/movie/browse/?lang="+lang)
	tabs = page_elems.xpath(".//section[@id='UIFeaturedFilms']//div[@class='tabview']")
	for block in tabs:
		loc = BASE_URL + block.xpath(".//div[@class='block1']//@href")[0]
		thumb = "http:" + block.xpath(".//div[@class='block1']//@src")[0]
		title = block.xpath(".//div[@class='block2']//a[@class='title']//text()")[0]
		summary = "Synopsis currently unavailable."
		oc.add(DirectoryObject(key = Callback(EpisodeDetail, title=title, url=loc), title = title, summary=summary, thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')))
		
	oc.add(InputDirectoryObject(key = Callback(Search, lang = lang), title='Search', summary='Search Movies', prompt='Search for...', thumb = R(ICON_SEARCH)))
		
	return oc
	
@route(PREFIX + "/sortmenualphabets")
def SortMenuAlphabets(lang, cat, **kwargs):

	oc = ObjectContainer(title2=cat.title())
	
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
	page_elems = HTML.ElementFromURL(url)
	movies = page_elems.xpath(".//section[@id='UIMovieSummary']/ul/li")
	for block in movies:
		loc = BASE_URL + block.xpath(".//div[@class='block1']//@href")[0]
		thumb = "http:" + block.xpath(".//div[@class='block1']//@src")[0]
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
	
	page_elems = HTML.ElementFromURL(url)
	try:
		thumb = "http:" + page_elems.xpath(".//section[@id='UIMovieSummary']//div[@class='block1']//@src")[0]
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
			trailer = trailer_u
	
	title = title
	#Log("url ------------------- " + url)
	oc = ObjectContainer(title1 = unicode(title), art=thumb)
	art = thumb
	res = "fail"
	
	if url not in LAST_PROCESSED_URL:
		#Log(url)
		python_dir = Prefs['python_dir']
		firefox_dir = Prefs['firefox_dir']
		res = slimerjs.einthusan(python_dir=python_dir, firefox_dir=firefox_dir, url=url)
		if 'error-fail' not in res:
			del LAST_PROCESSED_URL[:]
			furl = json.loads(res)['MP4Link']
			#Log("vidfile: " + furl)
			LAST_PROCESSED_URL.append(url)
			LAST_PROCESSED_URL.append(furl)
		else:
			Log(res)
			return ObjectContainer(header=title, message=title + ' could not be fetched !')
	else:
		furl = LAST_PROCESSED_URL[1]

	try:
		#Log("----------- url ----------------")
		#Log(url)
		oc.add(VideoClipObject(
			url = "einthusan://" + E(JSON.StringFromObject({"url":furl, "title": title, "summary": summary, "thumb": thumb, "year": year, "rating": rating})),
			art = art,
			title = title,
			thumb = thumb,
			summary = summary
		)
	)
	except:
		url = ""
		
	try:
		#Log("----------- url ----------------")
		#Log(url)
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
	python_dir = Prefs['python_dir']
	firefox_dir = Prefs['firefox_dir']
	res = slimerjs.einthusan(python_dir=python_dir, firefox_dir=firefox_dir, url="https://einthusan.tv")

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
	page_elems = HTML.ElementFromURL(url)
	movies = page_elems.xpath(".//section[@id='UIMovieSummary']/ul/li")
	for block in movies:
		loc = BASE_URL + block.xpath(".//div[@class='block1']//@href")[0]
		thumb = "http:" + block.xpath(".//div[@class='block1']//@src")[0]
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
		page = urllib.urlopen(url)
		redirectUrl = page.geturl()
	except:
		redirectUrl = url
			
	#Log("Redirecting url ----- : " + redirectUrl)
	return redirectUrl
	
######################################################################################	