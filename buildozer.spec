
[app]

title = GUNX SMART NBA

package.name = gunxsmartnba
package.domain = org.gunx

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json

icon.filename = %(source.dir)s/gunx_logo.png

# Native Android launch splash: use the official GUNX SMART NBA logo
presplash.filename = %(source.dir)s/gunx_logo.png
presplash.color = #070D1B

version = 0.1

requirements = python3,kivy,requests,certifi,urllib3,idna,charset-normalizer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.accept_sdk_license = True

android.api = 35
android.minapi = 24
android.ndk = 29
android.ndk_api = 24

android.archs = arm64-v8a

p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
