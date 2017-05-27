# plugin.video.flix2kodi
kodi addon

Big thanks to logi85, z-e-r-o and many others making this addon possible.

## Changelog
### 0.6.8
* Improved API_URL detection
* Fixed wrong credentials detection
* Fixed suggestions retrieval. See #1
* Fixed support on Kodi 17.x in Windows. See #2

### 0.6.7
* Adapted to working on new API scheme
* Dynamic shakti API build change support
* Fixed searching
* Changed browsing from suggested to AZ, to get a natural pagination.
* Included metadata fro non HD videos
* Other minor changes

## FAQ
### Not working in linux (ImportError: No module named Crypto.Cipher)
Make sure that *pycrypto* library was installed.
### Remote controls doesn't work in Linux
Make sure that *xdotool* is install.
