######################################################################################
#
#	Einthusan.com
#
######################################################################################

import common, updater, urllib

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
BASE_URL = "http://einthusan.com"
BASE_R_URL = "http://tiny.cc/Einthusan"
LANG_URL = "index.php?lang="
CATEGORY_BLURAY_URL = 'bluray'
CATEGORY_HD_URL = 'movies'
SEARCH_URL = "http://einthusan.com/search/"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)
	
	#HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'
	HTTP.Headers['Referer'] = 'http://www.einthusan.com'
	
	BASE_URL = GetRedirector(BASE_R_URL)
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
	
	defaultLang = Prefs['langPref']
	
	oc = ObjectContainer(title2=TITLE)

	oc.add(DirectoryObject(key = Callback(ShowMenu, lang = defaultLang), title = defaultLang.title() + ' Movies', thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(SetLanguage), title = 'Movies (Language Menu)', thumb = R(ICON_LANG)))
	
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Movie Bookmarks"), title = "My Movie Bookmarks", thumb = R(ICON_QUEUE)))
	
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
	page_elems = HTML.ElementFromURL(BASE_URL)
	langs = page_elems.xpath(".//*[@id='jumptolang']/li/a/text()")
	for lang in langs:
		oc.add(DirectoryObject(key = Callback(ShowMenu, lang = lang.lower()), title = lang, thumb = R(ICON_MOVIES)))
	
	return oc


@route(PREFIX + "/showMenu")
def ShowMenu(lang):

	oc = ObjectContainer(title2= lang.title() + ' Movies')
	oc.add(DirectoryObject(key = Callback(SortMenu, title = 'Bluray Movies', lang = lang, cat = CATEGORY_BLURAY_URL, page_count = 1), title = 'Bluray Movies', thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(SortMenu, title = 'HD Movies', lang = lang, cat = CATEGORY_HD_URL, page_count = 1), title = 'HD Movies', thumb = R(ICON_MOVIES)))
	oc.add(InputDirectoryObject(key = Callback(Search, lang = lang, page_count=1), title='Search', summary='Search Movies', prompt='Search for...'))
	
	return oc
	

@route(PREFIX + "/sortMenu")
def SortMenu(title, lang, cat, page_count):

	oc = ObjectContainer(title2='Sort ' + lang.title() + ' Movies By')
	oc.add(DirectoryObject(key = Callback(SortMenu2, title=title, lang=lang, cat=cat, page_count=page_count, org='Activity', filter='RecentlyPosted'), title = 'Activity', thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(SortMenu2, title=title, lang=lang, cat=cat, page_count=page_count, org = 'Alphabetical', filter='RecentlyPosted'), title = 'Alphabetical', thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(SortMenu2, title=title, lang=lang, cat=cat, page_count=page_count, org = 'Cast', filter='RecentlyPosted'), title = 'Cast', thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(SortMenu2, title=title, lang=lang, cat=cat, page_count=page_count, org = 'Year', filter='RecentlyPosted'), title = 'Year', thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(SortMenu2, title=title, lang=lang, cat=cat, page_count=page_count, org = 'Rating', filter='RecentlyPosted'), title = 'Rating', thumb = R(ICON_LIST)))
	oc.add(DirectoryObject(key = Callback(SortMenu2, title=title, lang=lang, cat=cat, page_count=page_count, org = 'Director', filter='RecentlyPosted'), title = 'Director', thumb = R(ICON_LIST)))

	return oc	

@route(PREFIX + "/sortMenu2")
def SortMenu2(title, lang, cat, page_count, org, filter):

	oc = ObjectContainer(title2='Filter Using')
	furl = BASE_URL + '/' + cat + '/' + LANG_URL + lang + '&organize=' + org + '&filtered=' + filter + '&org_type=' + org
	Log(furl)
	page_data = HTML.ElementFromURL(str(furl))
	elem = page_data.xpath(".//div[@class='video-organizer-element-wrapper']")
	for each in elem:
		filters = each.xpath(".//a//text()")

	for each in filters:
		filter = each
		filterS = filter
		if org == 'Activity':
			filterS = filter.replace(" ", "")
		#Log(" Filter ------------ " + filter)
		oc.add(DirectoryObject(key = Callback(ShowCategory, title=title, lang=lang, org=org, filter=filterS, cat=cat, page_count=page_count, search='null'), title = filter, thumb = R(ICON_LIST)))
	
	return oc
	
######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, lang, org, filter, cat, page_count, search):

	furl = BASE_URL + '/' + cat + '/' + LANG_URL + lang
	furl = furl + '&page=' + page_count + '&organize=' + org + '&filtered=' + filter + '&org_type=' + org

	if cat == 'bluray':
		furl = furl + '&bluray=BLURAY'
		
	if search != 'null':
		furl = furl + '&search=' + search
	
	categorytitle = lang.title() + ' - ' + title
	oc = ObjectContainer(title1 = categorytitle)

	page_data = HTML.ElementFromURL(str(furl))
	movies = page_data.xpath(".//div[@class='video-object-wrapper']")
	
	for each in movies:
		#Log("Each--------" + str(movies[0]))
	
		ffurl = each.xpath("a/@href")[0].lstrip('..')
		#Log("ffurl--------" + str(ffurl))
		title = str(each.xpath(".//div//div//h1//a//text()")[0])
		if cat == 'bluray':
			title = title.replace(" Blu-ray", "")
		#title = unicode(each.xpath("div/a/img/@alt"))
		#Log("title--------" + title)
		art = str(each.xpath('.//a//img//@src')[0])
		#Log("art--------" + str(art))
		thumb = BASE_URL + str(each.xpath('.//a//img//@src')[1]).lstrip('..').replace(" ","%20")
		#Log("thumb--------" + str(thumb))
		summary = unicode(each.xpath("div//div//p[@class='desc_body']//text()")[0])
		#Log("summary--------" + str(summary))
		wiki_url = each.xpath("div//div//a//@href")[1]

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = ffurl, thumb = thumb, summary = summary, art = art, wiki_url = wiki_url, cat=cat),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
			)
		)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = title, lang = lang, org = org, filter = filter, cat = cat, page_count = int(page_count) + 1, search=search),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	if len(oc) == 1:
		return ObjectContainer(header=title, message='No More Videos Available')
	return oc

######################################################################################

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, thumb, summary, art, wiki_url, cat):
	
	furl = BASE_URL + url
	#Log("url ------------------- " + furl)
	id = furl.split('id=')[1]
	url = "http://cdn.einthusan.com/geturl/"+id+"/"+cat+"/Washington%2CDallas%2CLondon%2CToronto%2CSan%2CSydney/+&+" + furl
	oc = ObjectContainer(title1 = unicode(title), art=art)
	#jsonOBJ = JSON.ObjectFromURL(wiki_url)['query']['pages']
	
	title = title
	description = summary
	thumb = thumb

	try:
		#Log("----------- url ----------------")
		#Log(url)
		oc.add(VideoClipObject(
			url = url,
			art = art,
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg'),
			summary = description
		)
	)
	except:
		url = ""
	
	if Check(title=title,url=furl):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = furl),
			title = "Remove Bookmark",
			art = art,
			summary = 'Removes the current movie from the Boomark que',
			thumb = R(ICON_QUEUE)
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = furl),
			title = "Bookmark Video",
			summary = 'Adds the current movie to the Boomark que',
			art = art,
			thumb = R(ICON_QUEUE)
		)
	)

	return oc
####################################################################################################
	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title)
	
	for each in Dict:
		url = Dict[each]
		#Log("url-----------" + url)
		if url.find(TITLE.lower()) != -1 and 'http' in url:
			page_data = HTML.ElementFromURL(url)
			movies = page_data.xpath(".//div[@class='video-object-wrapper']")
	
			for each in movies:
				#Log("Each--------" + str(movies[0]))
			
				ffurl = each.xpath("a/@href")[0].lstrip('..')
				if ' & ' in ffurl:
					ffurl = ffurl.split(' & ')[1]
					
				#Log("ffurl--------" + str(ffurl))
				title = str(each.xpath(".//div//div//h1//a//text()")[0])
				#title = unicode(each.xpath("div/a/img/@alt"))
				#Log("title--------" + title)
				art = str(each.xpath('.//a//img//@src')[0])
				#Log("art--------" + str(art))
				thumb = BASE_URL + str(each.xpath('.//a//img//@src')[1]).lstrip('..')
				#Log("thumb--------" + str(thumb))
				summary = unicode(each.xpath("div//div//p[@class='desc_body']//text()")[0])
				#Log("summary--------" + str(summary))
				wiki_url = each.xpath("div//div//a//@href")[1]

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = title, url = ffurl, thumb = thumb, summary = summary, art = art, wiki_url = wiki_url, cat='hd'),
					title = title,
					summary = summary,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
	
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
def Check(title, url):
	bool = False
	url = Dict[title]
	#Log("url-----------" + url)
	if url != None and (url.lower()).find(TITLE.lower()) != -1:
		bool = True
	
	return bool

######################################################################################
# Adds a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url):
	
	Dict[title] = url
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been added to your bookmarks.')
######################################################################################
# Removes a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, url):
	
	Dict[title] = 'removed'
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been removed from your bookmarks.')	
######################################################################################
# Clears the Dict that stores the bookmarks list
	
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	for each in Dict:
		if each.find(TITLE.lower()) != -1 and 'http' in each:
			Dict[each] = 'removed'
	Dict.Save()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.')

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
def Search(query, lang, page_count):

	Dict[TITLE.lower() +'MyCustomSearch'+query] = query
	Dict[TITLE.lower() +'MyCustomSLang'+query] = lang
	Dict.Save()
	oc = ObjectContainer(title2='Search Results')
	data = HTTP.Request(SEARCH_URL + '?lang='+ lang +'&search_query=%s' % String.Quote(query, usePlus=True), headers="").content
	page_data = HTML.ElementFromString(data)
	movies1 = page_data.xpath(".//div[@class='search-category-wrapper-left']//ul//li")
	c=0
	for each1 in movies1:
		name = each1.xpath(".//a//text()")[0]
		#Log("name--------" + name)
		c=c+1
		if name == 'show more movies...' or c > 6:
			oc.add(NextPageObject(
				key = Callback(ShowCategory, title=query, lang=lang, org='Activity', filter='RecentlyPosted', cat='movies', page_count=int(page_count)+1, search=query),
				title = "More...",
				thumb = R(ICON_NEXT)
					)
				)
			break
		url =  BASE_URL + each1.xpath(".//a//@href")[0].lstrip('..')
		page_data = HTML.ElementFromURL(url)
		movies = page_data.xpath(".//div[@class='video-object-wrapper']")

		for each in movies:
			#Log("Each--------" + str(movies[0]))
		
			ffurl = each.xpath(".//a//@href")[0].lstrip('..')
			if ' & ' in ffurl:
				ffurl = ffurl.split(' & ')[1]

			#Log("ffurl--------" + str(ffurl))
			title = str(each.xpath(".//div//div//h1//a//text()")[0])
			#title = unicode(each.xpath("div/a/img/@alt"))
			#Log("title--------" + title)
			art = str(each.xpath('.//a//img//@src')[0])
			#Log("art--------" + str(art))
			thumb = BASE_URL + str(each.xpath('.//a//img//@src')[1]).lstrip('..').replace(" ","%20")
			#Log("thumb--------" + str(thumb))
			summary = unicode(each.xpath("div//div//p[@class='desc_body']//text()")[0])
			#Log("summary--------" + str(summary))
			wiki_url = each.xpath("div//div//a//@href")[1]

			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = ffurl, thumb = thumb, summary = summary, art = art, wiki_url = wiki_url, cat='hd'),
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
				)
			)
		
	
	if len(oc) == 0:
		return ObjectContainer(header=title, message='No Videos Available')
	return oc
	

@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title):
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
			oc2.add(DirectoryObject(key = Callback(Search, query = query, lang = lang, page_count=1), title = query, thumb = R(ICON_SEARCH))
		)

	return oc2
####################################################################################################
####################################################################################################
# Gets the redirecting url for .m3u8 streams
@route(PREFIX + '/getredirector')
def GetRedirector(url):

	redirectUrl = url
	try:
		if '.m3u8' not in url and '.mp3' not in url and '.aac' not in url and '.m3u' not in url and '.mp4' not in url:
			page = urllib.urlopen(url)
			redirectUrl = page.geturl()
	except:
		redirectUrl = url
			
	#Log("Redirecting url ----- : " + redirectUrl)
	return redirectUrl