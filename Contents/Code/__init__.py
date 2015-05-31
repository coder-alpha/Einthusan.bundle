######################################################################################
#
#	Einthusan.com - v0.01
#
######################################################################################

TITLE = "Einthusan"
PREFIX = "/video/einthusan"
ART = "art-default.jpg"
ICON = "icon-einthusan.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
ICON_UNAV = "MoviePosterUnavailable.jpg"
BASE_URL = "http://www.einthusan.com"
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
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
	
	oc = ObjectContainer(title2=TITLE)
	oc.add(InputDirectoryObject(key = Callback(Search, lang = Prefs['langPref'], page_count=1), title='Search', summary='Search Movies', prompt='Search for...'))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Movie Bookmarks"), title = "My Movie Bookmarks", thumb = R(ICON_QUEUE)))
	oc.add(PrefsObject(title = 'Preferences', thumb = R('icon-prefs.png')))

	oc.add(DirectoryObject(key = Callback(ShowMenu, title = 'Movies'), title = 'Movies', thumb = R(ICON_MOVIES)))

	return oc

@route(PREFIX + "/showMenu")
def ShowMenu(title):
	oc2 = ObjectContainer(title2='Movies')
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Bluray Movies', lang = Prefs['langPref'], cat = CATEGORY_BLURAY_URL, page_count = 1), title = 'Bluray Movies', thumb = R(ICON_MOVIES)))
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'HD Movies', lang = Prefs['langPref'], cat = CATEGORY_HD_URL, page_count = 1), title = 'HD Movies', thumb = R(ICON_MOVIES)))

	return oc2
	

@route(PREFIX + "/sortMenu")
def SortMenu(title, lang, cat, page_count):
	oc = ObjectContainer(title2='Sort Movies By')
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
	
	categorytitle = title
	oc = ObjectContainer(title1 = title)

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

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = ffurl, thumb = thumb, summary = summary, art = art),
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
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, thumb, summary, art):
	
	url = BASE_URL + url
	oc = ObjectContainer(title1 = unicode(title), art=art)
	
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
####################################################################################################
	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title)
	
	for each in Dict:
		url = Dict[each]
		#Log("url-----------" + url)
		if url.find(TITLE.lower()) != -1:
			page_data = HTML.ElementFromURL(url)
			movies = page_data.xpath(".//div[@class='video-object-wrapper']")
	
			for each in movies:
				#Log("Each--------" + str(movies[0]))
			
				ffurl = each.xpath("a/@href")[0].lstrip('..')
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

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = title, url = ffurl, thumb = thumb, summary = summary, art = art),
					title = title,
					summary = summary,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
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

	Dict.Reset()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.')

####################################################################################################
@route(PREFIX + "/search")
def Search(query, lang, page_count):

	oc = ObjectContainer(title2='Search Results')
	data = HTTP.Request(SEARCH_URL + '?lang='+ lang +'&search_query=%s' % String.Quote(query, usePlus=True), headers="").content
	page_data = HTML.ElementFromString(data)
	movies1 = page_data.xpath(".//div[@class='search-category']//ul//li")
	c=0
	for each1 in movies1:
		name = each1.xpath(".//a//text()")[0]
		Log("name--------" + name)
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
			Log("ffurl--------" + str(ffurl))
			title = str(each.xpath(".//div//div//h1//a//text()")[0])
			#title = unicode(each.xpath("div/a/img/@alt"))
			#Log("title--------" + title)
			art = str(each.xpath('.//a//img//@src')[0])
			#Log("art--------" + str(art))
			thumb = BASE_URL + str(each.xpath('.//a//img//@src')[1]).lstrip('..').replace(" ","%20")
			#Log("thumb--------" + str(thumb))
			summary = unicode(each.xpath("div//div//p[@class='desc_body']//text()")[0])
			#Log("summary--------" + str(summary))

			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = ffurl, thumb = thumb, summary = summary, art = art),
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
				)
			)
		
	
	if len(oc) == 1:
		return ObjectContainer(header=title, message='No Videos Available')
	return oc
	
####################################################################################################