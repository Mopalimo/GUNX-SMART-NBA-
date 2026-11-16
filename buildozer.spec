
[app]

title = GUNX SMART NBA

package.name = gunxsmartnba
package.domain = org.gunx

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json

version = 0.1

requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.accept_sdk_license = True

android.api = 35
android.minapi = 23
android.ndk = 28c
android.archs = arm64-v8a

p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 1
