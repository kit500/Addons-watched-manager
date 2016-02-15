Add-ons watched backup
======================

Performs export/import/delete DB manipulation for "watched" flags and resume time positions for installed video addons.

How to use:
----------
All operations for addons requires for that addons to be istalled. This is to prevent accidental excessive rows in the DB.
The export/import files locations can be specified in Programs -> Addons watched manager -> Add-on settings, otherwise the default ones in the addon folder will be used.

The following actions are available:  
  Export - Export addons watch statuses ("watched" flags and resume time positions) to a file.  
  Import - Import addons watch statuses from a file.  
  View statistics / delete - Shows the amount of watched videos of every installed video addon. Choosing the particular addon from the list will delete all watch statuses from DB for a choosen addon.

Notes:
-----
* For reason the addon uses direct access to DB, its workability depends on used DB version. By now I've only tested it on XBMC 12, 13 and Kodi 14 alpha 2. On these verisons it works fine. Furthermore it has a good chance to work on a newer versions, since it uses DB tables, which have not changed for a long time among different versions. Nevertheless there is no guarantee, and formally speaking can even corrupt the DB (if importing) on non tested versions. This note can be extended while the new versions will be tested or implemented into the addon.
* Export/import file is a text file uses the following syntax: empty lines and lines starting with "#" are ignored, the separator between info items in lines should be ", " (at least one space following comma). So, can be edited to include or exclude rows, i.e. for particular addon.