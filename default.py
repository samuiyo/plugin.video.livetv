#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import os
import re
import sys
import math
import time
from time import localtime, gmtime, strftime, sleep
import datetime
import unicodedata

import urllib
import urlparse
import requests
from BeautifulSoup import BeautifulSoup
import HTMLParser
parser = HTMLParser.HTMLParser()
from resources.lib.google_images_download import google_images_download

addonID = xbmcaddon.Addon('plugin.video.livetv')
media = addonID.getAddonInfo('path')+"/resources/media"
APP_NAME = addonID.getAddonInfo('name')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'videos')
language = xbmc.getInfoLabel('System.Language')

xbmc_version = xbmc.getInfoLabel("System.BuildVersion")
user_agent = "Kodi Mediaplayer %s / LiveTV Addon %s" % (xbmc_version, "1.0.0")
headers = {"User-Agent": user_agent, "Accept-Encoding": "gzip", "X-Cookies-Accepted": "1"}

# Localized strings
T_ED_RESUL=33054
T_NO_RESUL=33055
T_NO_LSTRM=33056

listing = []


def get_localized_string(code):
	dev = addonID.getLocalizedString(code)
	try:
		dev = dev.encode('utf-8')
	except:
		pass
	
	return dev

def change_date_format(pt):
	ptmonth = ""
	pt = pt.replace('de ','').split(' ') #16 March at 22:00 // 16 de marzo a 23:00
	if pt[1] == get_localized_string(33002): ptmonth = '01'
	if pt[1] == get_localized_string(33003): ptmonth = '02'
	if pt[1] == get_localized_string(33004): ptmonth = '03'
	if pt[1] == get_localized_string(33005): ptmonth = '04'
	if pt[1] == get_localized_string(33006): ptmonth = '05'
	if pt[1] == get_localized_string(33007): ptmonth = '06'
	if pt[1] == get_localized_string(33008): ptmonth = '07'
	if pt[1] == get_localized_string(33009): ptmonth = '08'
	if pt[1] == get_localized_string(33010): ptmonth = '09'
	if pt[1] == get_localized_string(33011): ptmonth = '10'
	if pt[1] == get_localized_string(33012): ptmonth = '11'
	if pt[1] == get_localized_string(33013): ptmonth = '12'
	
	if len(pt[0]) < 2: pt[0] = '0'+pt[0]
	yy = strftime('%y', localtime())
	premiered = pt[0]+'/'+ptmonth+'/'+yy+' '+pt[3]
	try:
		premiered = datetime.datetime.strptime(premiered, '%d/%m/%y %H:%M')
	except TypeError:
		premiered = datetime.datetime(*(time.strptime(premiered, '%d/%m/%y %H:%M')[0:6]))
	
	return premiered

def check_audio_lang(audioch):
	if audioch == '0': audlang = get_localized_string(33014)
	if audioch == '1': audlang = get_localized_string(33015)
	if audioch == '2': audlang = get_localized_string(33016)
	if audioch == '3': audlang = get_localized_string(33017)
	if audioch == '4': audlang = get_localized_string(33018)
	if audioch == '5': audlang = get_localized_string(33019)
	if audioch == '6': audlang = get_localized_string(33020)
	if audioch == '7': audlang = get_localized_string(33021)
	if audioch == '8': audlang = get_localized_string(33022)
	if audioch == '9': audlang = get_localized_string(33023)
	if audioch == '10': audlang = get_localized_string(33024)
	if audioch == '11': audlang = get_localized_string(33025)
	if audioch == '12': audlang = get_localized_string(33026)
	if audioch == '13': audlang = get_localized_string(33027)
	if audioch == '14': audlang = get_localized_string(33028)
	if audioch == '15': audlang = get_localized_string(33029)
	if audioch == '16': audlang = get_localized_string(33030)
	if audioch == '17': audlang = get_localized_string(33031)
	if audioch == '18': audlang = get_localized_string(33032)
	if audioch == '19': audlang = get_localized_string(33033)
	if audioch == '20': audlang = get_localized_string(33034)
	if audioch == '21': audlang = get_localized_string(33035)
	if audioch == '22': audlang = get_localized_string(33036)
	if audioch == '23': audlang = get_localized_string(33037)
	if audioch == '24': audlang = get_localized_string(33038)
	if audioch == '25': audlang = get_localized_string(33039)
	if audioch == '26': audlang = get_localized_string(33040)
	if audioch == '27': audlang = get_localized_string(33041)
	if audioch == '28': audlang = get_localized_string(33042)
	if audioch == '29': audlang = get_localized_string(33043)
	if audioch == '30': audlang = get_localized_string(33044)
	if audioch == '31': audlang = get_localized_string(33045)
	if audioch == '32': audlang = get_localized_string(33046)
	if audioch == '33': audlang = get_localized_string(33047)
	if audioch == '34': audlang = get_localized_string(33048)
	if audioch == '35': audlang = get_localized_string(33049)
	if audioch == '36': audlang = get_localized_string(33050)
	if audioch == '37': audlang = get_localized_string(33051)
	if audioch == '38': audlang = get_localized_string(33052)
	if audioch == '39': audlang = get_localized_string(33053)
	
	return audlang.decode('utf-8')

def hms_to_m(n):
	s = 0
	for u in n.split(':'):
		s = 60 * s + int(u)
	m = s/60
	
	return m

def build_url(urlqry):
	return base_url + '?' + urllib.urlencode(urlqry)

def get_event_list(url):
	li = ''
        response = requests.get(url, headers=headers)
        # response.status
        htm = response.text
        htm = htm.encode('iso-8859-1', 'ignore')
        htm = BeautifulSoup(htm)
	image = url.split('/')
	image = media + "/sports/" + image[5] + ".sport.png"
	plot = htm.findAll('span', attrs={'class': re.compile('sltitle')})
	plot = parser.unescape(str(plot).replace('\t','').replace('\n','').replace('[','').replace(']','').decode('utf-8').strip())
	plot = re.sub(r'<[^>]*>', r'', plot)
	htm = str(htm)
	
	tday = strftime("%-d de %B, %A ", localtime())
	htm = htm.split('<span class="sltitle">', 1)[-1]
	htm = htm.split('<a href="/es/archive/">', 1)[0]
	htm = re.sub(r'\t', r'', ''.join(htm))
	htm = re.sub(r'\n', r'', htm)
	htm = re.sub(r'/icons/', r'\n/icons/', htm)
	htm = re.sub(r'</span>', r'</span>\n', htm)
	htm = [line for line in htm.split('\n') if '/icons/' in line]
	htm = '\n'.join(htm)
	htm = parser.unescape(htm.decode('utf-8').strip())
	
	query = """/icons/(.+?)".+?<a class=.+?href="(.+?)">(.+?)</a>.+?"evdesc">(.+?)<.+?>(.+?)</span>"""
	events = re.compile(query, re.DOTALL).findall(htm)
	events = list(dict.fromkeys(events))
	
#	print (htm2)
#	print (events)
	
	for e in events:
		#image = "http://cdn.livetvcdn.net/img/icons/" + e[0]
		hrefs = urlbase + e[1]
		event = e[2]
		time = change_date_format(e[3])
		mins = 1440 - hms_to_m(str(datetime.datetime.now().time())[:-7])
		tnow =  datetime.datetime.now() + datetime.timedelta(minutes=30)
		tday =  datetime.datetime.now() + datetime.timedelta(minutes=mins)
		desc = e[4]
#		desc_image = unicodedata.normalize('NFD', desc[1:-1]).encode('ascii', 'ignore')
#		
#		response_image = google_images_download.googleimagesdownload()
#		arguments_image = {
#			"keywords": desc_image[1:-1],
#			"suffix_keywords": "logo",
#			"limit": 1,
#			"format": "jpg",
#			"output_directory": "storage",
#			#"image_directory": "pictures",
#			"no_directory": True,
#			"no_download": True
#		}
#		absolute_image_paths = response_image.download(arguments_image)
#		image = absolute_image_paths[desc_image[1:-1]+' logo'][0]
		
		if time < tnow:
			time = time.strftime("%d/%m/%y %H:%M")
			url = build_url({'mode': 'folder', 'foldername': hrefs})
			li = xbmcgui.ListItem('[COLOR lightskyblue]('+time+')[/COLOR] [B]'+event+'[/B] [COLOR lightseagreen]'+desc+'[/COLOR]')
			li.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
			li.setInfo('video', { 'plot': plot })
			xbmcplugin.addSortMethod(handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
		
		elif time < tday:
			time = time.strftime("%d/%m/%y %H:%M")
			url = ''
			li = xbmcgui.ListItem('[I][COLOR lightskyblue]('+time+')[/COLOR] [B]'+event+'[/B] [COLOR lightseagreen]'+desc+'[/COLOR][/I]')
			li.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
			li.setInfo('video', { 'plot': plot })
			xbmcplugin.addSortMethod(handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
			xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
		
	if li == '':
		image = media + '/33056.png'
		url = ''
		li = xbmcgui.ListItem('[I][B]'+get_localized_string(T_NO_LSTRM)+'[/B][/I]')
		li.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
		li.setInfo('video', { 'plot': plot })
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
	
	xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True)

def get_links_list(url):
	response = requests.get(url, headers=headers)
	# response.status
	htm = response.text
	htm = htm.encode('iso-8859-1', 'ignore')
	htm = BeautifulSoup(htm)
	plot = htm.findAll('h1', attrs={'class': re.compile('sporttitle')})
	plot = parser.unescape(str(plot).replace('\t','').replace('\n','').replace('[','').replace(']','').decode('utf-8').strip())
	plot = re.sub(r'<[^>]*>', r'', plot)
	htm = str(htm)
	
	if re.search(get_localized_string(T_ED_RESUL), htm):
		htm = re.split(get_localized_string(T_ED_RESUL), htm, 1)[1]
		htm = htm.split('<div id="comblockabs">', 1)[0]
		htm = re.sub(r'\t', r'', ''.join(htm))
		htm = re.sub(r'\n', r'', htm)
		htm = parser.unescape(htm.decode('utf-8').strip())
		
		query = """.+?<b>(.+?)</b>.+?"""
		elinks = re.compile(query, re.DOTALL).findall(htm)
		elinks[0] = '[COLOR lightskyblue]'+get_localized_string(T_ED_RESUL)+elinks[0]+'[/COLOR]'
		for el in elinks:
			image = media + '/33054.png'
			
			list_item = xbmcgui.ListItem(label=el)
			list_item.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
			list_item.setInfo('video', { 'plot': plot })
			list_item.setProperty('IsPlayable', 'false')
			
			k_url = ''
			
			listing.append((k_url, list_item, False))
	
	elif re.search('AceStream Links', htm):
		htm = htm.split('<span class="lnkt">AceStream Links</span>', 1)[-1]
		htm = htm.split('<div id="comblockabs">', 1)[0]
		htm = re.sub(r'\t', r'', ''.join(htm))
		htm = re.sub(r'\n', r'', htm)
		htm = re.sub(r'<td width="16">', r'\n', htm)
		htm = parser.unescape(htm.decode('utf-8').strip())
		
		query = """<img title=".+?/linkflag/(.+?).png" />.+?class="bitrate".+?">(.+?)/td>.+?<a href="acestream:(.+?)">.+?"""
		elinks = re.compile(query, re.DOTALL).findall(htm)
		
		for el in elinks:
			image = media + "/flags/" + el[0] + ".gif"
			
			list_item = xbmcgui.ListItem(label='[B]Audio: '+check_audio_lang(el[0])+', Bitrate: AceStream '+el[1].replace('<','')+'[/B]')
			list_item.setArt({ 'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image })
			list_item.setInfo('video', { 'plot': plot })
			list_item.setProperty('IsPlayable', 'true')
			
			k_url = 'plugin://program.plexus/?mode=1&url=acestream:'+el[2]+'&name=[B]Audio: '+check_audio_lang(el[0])+', Bitrate: AceStream '+el[1].replace('<','')+'[/B]'
			
			listing.append((k_url, list_item, False))
		
	else:
		image = media + '/33056.png'
		list_item = xbmcgui.ListItem(label='[I][B]'+get_localized_string(T_NO_LSTRM)+'[/B][/I]')
		list_item.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
		list_item.setInfo('video', { 'plot': plot })
		list_item.setProperty('IsPlayable', 'false')
		
		k_url = ''
		
		listing.append((k_url, list_item, False))
	
	if len(listing) < 1:
		image = media + '/33057.png'
		list_item = xbmcgui.ListItem(label='¡¡¡GRFTJX!!! ¡¡¡GRMBLFJ!!!')
		list_item.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
		list_item.setInfo('video', { 'plot': plot })
		list_item.setProperty('IsPlayable', 'false')
		
		k_url = ''
		
		listing.append((k_url, list_item, False))
	
	return listing


#xbmcgui.Dialog().ok(APP_NAME, "HOLA")

urlbase = "http://185.39.10.6"
urllang = get_localized_string(33001)
urlall = "/allupcoming"
url = urlbase + urllang + urlall

try:
	mode = args.get('mode', None)
except (SyntaxError, TypeError) as e:
	xbmc.log(msg='Error: %s' % str(e), level=xbmc.LOGERROR)

if mode is None:
	li = ''
        response = requests.get(url, headers=headers)
        # response.status
        htm = response.text
        htm = htm.encode('iso-8859-1', 'ignore')
        htm = BeautifulSoup(htm)
	htm = str(htm)
	
	htm = htm.split('<div id="aul">', 1)[-1]
	htm = htm.split('<a href="/es/majorcompetitions/">', 1)[0]
	htm = [line for line in htm.split('\n') if '<a class="main" ' in line]
	htm = re.sub(r'\t', r'', ''.join(htm))
	htm = re.sub(r'</td>', r'</td>\n', htm)
	htm = re.sub(r'</a><td background=', r'</a>\n<td background=', htm)
	htm = re.sub(r'(?m)^<td background=.*\n?', r'', htm)
	htm = parser.unescape(htm.decode('utf-8').strip())
	
	query = """<a class=.+?href="(.+?)".+?<b>(.+?)</b>.+?"""
	sports = re.compile(query, re.DOTALL).findall(htm)
	
	#print (htm)
	#print (sports)
	
	for s in sports:
		hrefs = urlbase + s[0]
		image = s[0].split('/')
		image = media + "/sports/" + image[3] + ".cubic.gif"
		sport = s[1].encode('utf-8')
		
		url = build_url({'mode': 'folder', 'foldername': hrefs})
		li = xbmcgui.ListItem(sport)
		li.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
		xbmcplugin.addSortMethod(handle=addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
		
	if li == '':
		image = media + '/33055.png'
		url = ''
		li = xbmcgui.ListItem('[I][B]'+get_localized_string(T_NO_RESUL)+'[/B][/I]')
		li.setArt({'fanart': addonID.getAddonInfo('fanart'), 'icon': image, 'thumb': image, 'poster': image})
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)

	
	xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True)


elif mode[0] == 'folder' and 'allupcomingsports' in args['foldername'][0]:
	foldername = args['foldername'][0]
	url = foldername
	
	get_event_list(url)
	#listing = get_event_list(url)

elif mode[0] == 'folder' and 'eventinfo' in args['foldername'][0]:
	foldername = args['foldername'][0]
	url = foldername
	
	listing = get_links_list(url)
	
	# Add list to Kodi.
	xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
	xbmcplugin.endOfDirectory(handle=addon_handle, succeeded=True)

