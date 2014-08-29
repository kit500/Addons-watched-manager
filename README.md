Add-ons watched backup
======================

Performs export/import/delete DB manipulation for "watched" flags and resume time positions for installed video addons.

How to use:
----------
All operations for addons requires for that addons to be istalled. For example, watch states of non installed addons won't be imported to prevent excessive rows in the DB.
The export/import files locations can be specified in Programs -> Addons watched manager -> Add-on settings, otherwise the default ones in the addon folder will be used.

The following actions is available:  
  Export - Export addons whatch states (watched flags and resume time positions) to a file.  
  Import - Import addons whatch states from a file.  
  View statistics / delete - Shows the amount of watched videos of every installed video addon. Choosing the particular addon will delete all watch states from DB for choosen addon.

Notes:
-----
* For reason the addon uses direct access to DB, it depends on used DB version. Therefore, it is important to keep to the compatibility. By now the compatibility is: XBMC 12 up to Kodi 14 alpha 2. This note can be extended while the new versions will be tested or implemented in the addon.
* Export/import file is a text file uses the following syntax: empty lines and lines starting with "#" are ignored, the separator between info items in lines should be ", " (at least one space following comma).