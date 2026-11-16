
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

android.api = 36
android.minapi = 24
android.ndk = 29
android.ndk_api = 24
android.archs = arm64-v8a

p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
