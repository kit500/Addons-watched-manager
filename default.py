#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os, re, json, urllib
import sqlite3 as sqlite
import xbmcaddon, xbmcgui, xbmcplugin, xbmc

Addon = xbmcaddon.Addon(id = 'script.addons.watched.backup')
addon_path    = Addon.getAddonInfo('path')
addon_profile = Addon.getAddonInfo('profile')
addon_name    = Addon.getAddonInfo('name')
addon_id      = Addon.getAddonInfo('id')
#print addon_profile

ls = Addon.getLocalizedString
log = xbmc.log

def regexp(expr, item):
	reg = re.compile(expr)
	return reg.search(item) is not None

def showMessage(heading, message, times = 6000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading, message, times))

def construct_uri(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def GetDB():
	dbpath = xbmc.translatePath('special://database')
	dblist = os.listdir(dbpath)
	dbvs = []
	for file in dblist:
		if re.findall('MyVideos(\d+)\.db', file): dbvs.append(int(re.findall('MyVideos(\d+)\.db', file)[0]))
	dbv = str(max(dbvs))
	print 'DB version: ' + dbv
	dbpath = xbmc.translatePath(os.path.join('special://database', 'MyVideos' + dbv + '.db'))
	print "DB path: " + dbpath
	return dbpath

def get_params(paramstring):
    param = []
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    if len(param) > 0:
        for cur in param:
            param[cur] = urllib.unquote_plus(param[cur])
    return param

def SubmitSqlRequest(request, vars = (), many = False):
	try:
		dbconn = sqlite.connect(dbpath, timeout = 1000, check_same_thread = False)
	except Exception as e:
		log(ls(32000) % str(e))
		return None
	dbconn.create_function("REGEXP", 2, regexp)
	c = dbconn.cursor()
	try:
		c.execute(request, vars)
	except Exception as e:
		log(ls(32001) % (request, str(e)))
		dbconn.close()
		return None
	if re.search('(UPDATE|INSERT|DELETE)', request):
		try:
			dbconn.commit()
			result = c.rowcount
		except:
			log(ls(32002) % str(e))
			dbconn.close()
			return None
	else:
		if many: result = c.fetchall()
		else: result = c.fetchone()
	dbconn.close()
	return result

def GetAddons():
	response = xbmc.executeJSONRPC('{ \
		"jsonrpc": "2.0", \
		"id": 1, \
		"method": "Addons.GetAddons", \
		"params": {"type": "xbmc.addon.video"} \
		}')
	response = json.loads(response)
	addons = response["result"]["addons"]
	#print json.dumps(addons, indent = 1, ensure_ascii = False).encode('utf-8')
	addonids = []
	for addon in addons:
		addonids.append(addon["addonid"])
	return addonids

def GetLinesCount(filename):
	file = open(filename, 'r')
	filelen = sum(1 for line in file)
	file.close()
	return filelen


def Import(params):
	log(addon_id + ": Import")
	addonids = GetAddons()
	paths = SubmitSqlRequest('SELECT strPath, idPath FROM path WHERE strPath REGEXP "plugin://.+"', many = True)
	#print paths
	filelen = GetLinesCount(import_file)
	if filelen == 0:
		log(ls(32003))
		showMessage(addon_id, ls(32003))
		return
	imf = open(import_file, 'r')
	pdlg = xbmcgui.DialogProgress()
	pds = 100.0 / float(filelen)
	cpd = 0.0
	pdlg.create(addon_id, ls(32005))

	for linen, rline in enumerate(imf):
		cpd += pds
		pdlg.update(int(cpd))
		if not rline.strip() or rline.find('#') == 0: continue
		items = rline.split(", ")
		items = map(lambda i: i.strip(), items)
		items = map(lambda i: None if i == "null" else i, items)
		if items[1]:
			if items[1].isdigit():
				items[1] = int(items[1])
			else:
				log(ls(32006) % str(linen + 1))
				log(rline)
				continue
		try:
			path = re.compile('(plugin://.+?/).*').findall(items[0])[0]
		except Exception as e:
			log(ls(32007) % (str(linen + 1), str(e)))
			log(rline)
			continue
		addonid = re.compile('plugin://(.+?)/.*').findall(path)[0]
		if addonid not in addonids:
			log(ls(32008) % addonid, 1)
			log(rline, 1)
			continue
		log(str(items))
		existedidpath = filter(lambda i: i[0] == path, paths)
		if len(items) != 3 and len(items) != 5:
			log(ls(32009) % str(linen + 1))
			log(rline)
			continue

		if existedidpath:
			existedidpath = existedidpath[0][1]
			log("existed path id: " + str(existedidpath))
			existedidfile = SubmitSqlRequest('SELECT idFile FROM files WHERE strFilename=?', (items[0],))
			if existedidfile:
				log("existed file id: " + str(existedidfile[0]))
				tac = SubmitSqlRequest('UPDATE files SET idPath=?, strFilename=?, playCount=?, lastPlayed=? WHERE idFile=?', (existedidpath, items[0], items[1], items[2], existedidfile[0]))
				log("tac update files: " + str(tac))
			else:
				tac = SubmitSqlRequest('INSERT INTO files (idPath, strFilename, playCount, lastPlayed) VALUES (?,?,?,?)', (existedidpath, items[0], items[1], items[2]))
				log("tac insert files: " + str(tac))
		else:
			tac = SubmitSqlRequest('INSERT INTO path (strPath, strContent, strScraper) VALUES (?,?,?)', (path, "", ""))
			log("tac insert path: " + str(tac))
			cidpath = SubmitSqlRequest('SELECT idPath FROM path WHERE strPath=?', (path,))
			log("path id: " + str(cidpath[0]))
			#update current paths list
			paths.append((path, cidpath[0]))
			tac = SubmitSqlRequest('INSERT INTO files (idPath, strFilename, playCount, lastPlayed) VALUES (?,?,?,?)', (cidpath[0], items[0], items[1], items[2]))
			log("tac insert files: " + str(tac))
		
		if len(items) == 5:
			idfile = SubmitSqlRequest('SELECT idFile FROM files WHERE strFilename=?', (items[0],))
			log("file id: " + str(idfile[0]))
			existedidbookmark = SubmitSqlRequest('SELECT idBookmark FROM bookmark WHERE idFile=?', (idfile[0],))
			if existedidbookmark:
				tac = SubmitSqlRequest('UPDATE bookmark SET idFile=?, timeInSeconds=?, totalTimeInSeconds=? WHERE idBookmark=?', (idfile[0], items[3], items[4], existedidbookmark[0]))
				log("tac update bookmark: " + str(tac))
			else:
				tac = SubmitSqlRequest('INSERT INTO bookmark (idFile, timeInSeconds, totalTimeInSeconds, thumbNailImage, player, playerState, type) VALUES (?,?,?,?,?,?,1)', (idfile[0], items[3], items[4], "", "DVDPlayer", ""))
				log("tac insert bookmark: " + str(tac))
	
	pdlg.close()
	imf.close()


def Delete(params):
	log(addon_id + ": Delete")
	addonids = GetAddons()

	for addonid in addonids:
		result = SubmitSqlRequest('SELECT idFile FROM files WHERE strFilename REGEXP "plugin://'+addonid+'/.*?"', many = True)
		log(ls(32010) % (addonid, str(len(result))), 1)
		deltitle = addonid
		if len(result) > 0:
			deltitle = "[COLOR lime]" + deltitle + "[/COLOR]"
		deltitle = ls(32011) % (deltitle, "[COLOR yellowgreen]" + str(len(result)) + "[/COLOR]")
		li = xbmcgui.ListItem(deltitle)
		uri = construct_uri({"func": "deletespecific", "addonid": addonid})
		xbmcplugin.addDirectoryItem(h, uri, li)

	xbmcplugin.endOfDirectory(h, cacheToDisc = False)

def deletespecific(params):
	addonid = params['addonid']
	dialog = xbmcgui.Dialog()
	confirm = dialog.yesno(addon_id, ls(32012) % addonid)
	if confirm:
		result = SubmitSqlRequest('SELECT idFile FROM files WHERE strFilename REGEXP "plugin://'+addonid+'/.*?"', many = True)
		if len(result) == 0:
			showMessage(addon_id, ls(32013) % addonid)
			return
		pdlg = xbmcgui.DialogProgress()
		pds = 100.0 / float(len(result))
		cpd = 0.0
		pdlg.create(addon_id, ls(32014))
		for item in result:
			log("file id: " + str(item[0]))
			cpd += pds
			pdlg.update(int(cpd))
			bm = SubmitSqlRequest('SELECT idBookmark FROM bookmark WHERE idFile=? AND type=1', (item[0],))
			tac = SubmitSqlRequest('DELETE FROM files WHERE idFile=?' ,(item[0],))
			log("tac delete files: " + str(tac))
			if bm:
				tac = SubmitSqlRequest('DELETE FROM bookmark WHERE idBookmark=?',(bm[0],))
				log("tac delete bookmark: " + str(tac))
		pdlg.close()
		xbmc.executebuiltin('Container.Refresh')


def Export(params):
	log(addon_id + ": Export")
	addonids = GetAddons()
	log(str(addonids), 1)

	exf = open(export_file, 'w')
	pdlg = xbmcgui.DialogProgress()
	pds = 100.0 / float(len(addonids))
	cpd = 0.0
	pdlg.create(addon_id, ls(32015))
	for addonid in addonids:
		cpd += pds
		pdlg.update(int(cpd))
		result = SubmitSqlRequest('SELECT strFilename, playCount, lastPlayed, idFile FROM files WHERE strFilename REGEXP "plugin://'+addonid+'/.*?"', many = True)
		if len(result) > 0:
			#print result
			log(ls(32010) % (addonid, str(len(result))))
			exf.write('#' + addonid + ":\n")
			for item in result:
				bm = SubmitSqlRequest('SELECT timeInSeconds, totalTimeInSeconds FROM bookmark WHERE idFile=? AND type=1', (item[3],))
				#print bm
				item = map(str, item)
				rline = ", ".join(item[:-1])
				if bm:
					bm = map(str, bm)
					rline += ", " + ", ".join(bm)
				rline += "\n"
				rline = rline.replace("None", "null")
				exf.write(rline)
			exf.write("\n")
	exf.close()
	pdlg.close()


def Main():
	li = xbmcgui.ListItem(ls(32016))
	li.setInfo(type="video", infoLabels = {"plot": ls(32017)})
	uri = construct_uri({"func": "Export"})
	xbmcplugin.addDirectoryItem(h, uri, li)
	li = xbmcgui.ListItem(ls(32018))
	li.setInfo(type="video", infoLabels = {"plot": ls(32019)})
	uri = construct_uri({"func": "Import"})
	xbmcplugin.addDirectoryItem(h, uri, li)
	li = xbmcgui.ListItem(ls(32020))
	li.setInfo(type="video", infoLabels = {"plot": ls(32021)})
	uri = construct_uri({"func": "Delete"})
	xbmcplugin.addDirectoryItem(h, uri, li, isFolder = True)
	xbmcplugin.endOfDirectory(h)


#print sys.argv
h = int(sys.argv[1])
params = get_params(sys.argv[2])
func = params['func'] if 'func' in params else None

dbpath = GetDB()
export_file = Addon.getSetting('export_file')
if not export_file: export_file = os.path.join(addon_path, 'export.txt')
print "export file: " + export_file
import_file = Addon.getSetting('import_file')
if not import_file: import_file = os.path.join(addon_path, 'import.txt')
print "import file: " + import_file

if func != None:
	try: pfunc = globals()[func]
	except:
		pfunc = None
		log('[%s]: Function "%s" is not found' % (addon_id, func), 4)
		showMessage(addon_id, 'Function "%s" is not found' % func)
	if pfunc: pfunc(params)
else:
	Main()
