Einthusan.bundle
===================

This is a plugin that creates a new channel in Plex Media Server to view content indexed by the website einthusan.tv

[Plex Support thread] (https://forums.plex.tv/index.php/topic/165072-rel-einthusan-channel-indian-movies/)

System Requirements
===================

- **Plex Media Server:**
	- Tested Working (read Important Notes below):
		- Windows
		- Linux
		- Mac
- **Plex Clients:**
	- Tested Working:
		- Plex Home Theater
		- Plex/Web
		- Samsung Plex App
		- Android M (Samsung Galaxy S6)
		- iOS (Apple iPhone6)

How To Install
==============
- Download the latest version of the plugin.
- Unzip and rename folder to "Einthusan.bundle"
- Delete any previous versions of this bundle
- Copy Einthusan.bundle into the PMS plugins directory under your user account:
	- Windows 10, 8, 7, Vista, or Server 2008: 
		C:\Users[Your Username]\AppData\Local\Plex Media Server\Plug-ins
	- Windows XP, Server 2003, or Home Server: 
		C:\Documents and Settings[Your Username]\Local Settings\Application Data\Plex Media Server\Plug-ins
	- Mac/Linux: 
        ~/Library/Application Support/Plex Media Server/Plug-ins
- Restart PMS


Important Notes:
==============
Some Mac/Linux distributions of PMS have a SSL/TLS issue.
If your PMS does not have the recent SSL fix by Plex you might need to use one of the following options:

1. Try first with No SSL Alternate and No Proxy option.
2. Then try SSL alternate first (This should work for all OS with recent PMS.. I think 1.3.3+)
3. If #2 doesn't work use Proxy method and SlimerJS. Only the Proxy method needs SlimerJS enabled - read below.

For SlimerJS
- Download and install Python 2.7.13 or higher (Linux only)
- Download and install Firefox 40.x or higher (upto 51.x tested so far)
- Set paths to Python and Firefox in the channel preferences (not required if their paths are defined under system's env. variables)
- Linux requires 'xvfb' to be installed for SlimerJS to run headless
- Read more on the support thread mentioned above.

Acknowledgements
==============

- Credits to [SlimerJS] (http://slimerjs.org/)
