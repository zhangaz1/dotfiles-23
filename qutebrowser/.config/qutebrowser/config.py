# note: this will be run with python 3

import os
import socket
import operator
import subprocess
from shutil import which

from qutebrowser.config.configfiles import ConfigAPI  # noqa: F401
from qutebrowser.config.config import ConfigContainer  # noqa: F401

from qutebrowser.api import interceptor, message

config = config  # type: ConfigAPI # noqa: F821
c = c  # type: ConfigContainer # noqa: F821

# https://github.com/noctuid/dotfiles/blob/master/browsing/.config/qutebrowser/config.py
def nmap(key, command):
    """Bind key to command in normal mode."""
    config.bind(key, command, mode='normal')


# is this the first time running?
initial_start = c.tabs.background == False

# ui
c.completion.scrollbar.width = 10
c.tabs.position = 'top'
c.tabs.show = 'multiple'
c.tabs.indicator.width = 0
c.tabs.title.format = '{current_title}'
c.tabs.title.alignment = 'center'
c.downloads.position = 'bottom'
c.tabs.favicons.show = 'never'

# behavior
c.downloads.location.prompt = False
c.hints.scatter = False
c.url.searchengines = {'DEFAULT': 'https://google.com/search?q={}' }
c.input.insert_mode.auto_load = True
c.input.insert_mode.auto_leave = False
c.tabs.background = True

if 'EDITOR' in os.environ:
    c.editor.command = [os.environ['EDITOR'] + ' "{}"']

if which("qutebrowser-edit"):
    c.editor.command = [which("qutebrowser-edit"), '-l{line}', '-c{column}', '-f{file}']

c.auto_save.session = True

nmap('b', 'set-cmd-text --space :buffer')

# trying to match to 's' avy hinting in emacs
config.unbind('sf');
config.unbind('sk');
config.unbind('sl');
config.unbind('ss');
nmap('s', 'hint')


# kill the old habit:
config.unbind('f');

# colemak
c.hints.chars = 'arstgkneio'
nmap('n', 'scroll-page 0 0.2')
nmap('e', 'scroll-page 0 -0.2')
nmap('N', 'tab-next')
nmap('E', 'tab-prev')
nmap('k', 'search-next')
nmap('K', 'search-prev')

# keep autosave session in sync when tabs are closed as well as opened
# total hack
d_sync = ';;'.join([
    'tab-close',
    'set messages.timeout 1',
    'session-save --force _autosave',
    'set messages.timeout 2000',
    ])

nmap('d', d_sync)

# default theme:
theme = {
    'panel': {'height': 25,},
    'fonts': {
        'tabbar': 'monospace',
        'completion': 'monospace',
        'completion_size': 9,
        'tab_bold': False,
        'tab_size': 11,
        'status_size': 9,
    },
    'colors': {
        'bg': {
            'normal': '#FAFAFA',
            'active': '#E4E4E4',
            'inactive': '#FAFAFA',
        },
        'fg': {
            'normal': '#546E7A',
            'active': '#546E7A',
            'inactive': '#546E7A',
            'match': '#18323E', # completion and hints
        },
    }
}

# import templated theme when file exists
themefile = os.environ["HOME"] + '/.config/qutebrowser/colors.py'
if os.path.exists(themefile):
    exec(open(themefile).read())

colors = theme['colors']

# apply the theme:
def setToBG(colortype, target):
    config.set('colors.' + target, colors['bg'][colortype])

def setToFG(colortype, target):
    config.set('colors.' + target, colors['fg'][colortype])

def colorSync(colortype, setting):
    if setting.endswith('.fg'):
        setToFG(colortype, setting)
    elif setting.endswith('.bg'):
        setToBG(colortype, setting)
    elif setting.endswith('.top') or setting.endswith('.bottom'):
        setToFG(colortype, setting)
    else:
        setToFG(colortype, setting + '.fg')
        setToBG(colortype, setting + '.bg')

targets = {
    'normal' : [
        'statusbar.normal',
        'statusbar.command',
        'statusbar.url.success.http.fg',
        'statusbar.url.success.https.fg',
        'hints',
        'downloads.bar.bg',
        'completion.category',

        'tabs.even',
        'tabs.odd',
    ],

    'active' : [
        'tabs.selected.even',
        'tabs.selected.odd',
        'statusbar.insert',
        'downloads.stop',
        'prompts',
        'messages.warning',
        'messages.error',
        'statusbar.url.hover.fg',
        'completion.item.selected',

        'completion.category.border.top',
        'completion.category.border.bottom',

        'completion.item.selected.border.top',
        'completion.item.selected.border.bottom',
    ],

    'inactive': [
        'completion.scrollbar',
        'downloads.start',
        'messages.info',
        'completion.fg',
        'completion.odd.bg',
        'completion.even.bg',
    ],

    'match': [
        'completion.match.fg',
        'hints.match.fg',
    ]
}

for colortype in targets:
    for target in targets[colortype]:
        colorSync(colortype, target)

setToFG('active', 'statusbar.progress.bg')

config.set('hints.border', '1px solid ' + colors['fg']['normal'])

# tabbar
def makePadding(top, bottom, left, right):
    return { 'top': top, 'bottom': bottom, 'left': left , 'right': right }

# this doesn't work?? the value is 2small
# font_height = {{{txth -f "$q_tab_font" -s $q_tab_fontsize ph}}}

# todo:
# inkscape --without-gui --query-id=id1 -H <(echo '<svg><text id="id1" font-family="Equity Text B">python</text></svg>') 2>/dev/null
font_height = 19 # -- measured on a 'ph' qute title in pinta for test theme

surround = round((theme['panel']['height'] - font_height) / 2)
c.tabs.padding = makePadding(surround, surround, 8, 8)
c.tabs.indicator.padding = makePadding(0, 0, 0, 0)

# fonts
fonts = theme['fonts']
# c.fonts.monospace = fonts['tabbar']

def GetSize(fontType):
    return str(fonts[fontType + '_size']) + 'pt '

tabFont = GetSize('tab') + fonts['tabbar']

if fonts['tab_bold']:
    tabFont = 'bold {0}'.format(tabFont)

# c.fonts.tabs = tabFont

# next stable qutebrowser version:
c.fonts.tabs.selected = tabFont
c.fonts.tabs.unselected = tabFont

c.fonts.completion.entry = GetSize('completion') + fonts['completion']
c.fonts.statusbar = GetSize('completion') + fonts['completion']

nmap('<F10>', 'spawn --userscript chrome_open')
# nmap('W', 'spawn --userscript scrape')
nmap('<F12>', 'inspector')

REDIRECT_MAP = {
    # note: the redirect stuff needs a newish version of qb (at least, newer than nixpkgs stable)
    "reddit.com": operator.methodcaller('setHost', 'old.reddit.com'),
    "www.reddit.com": operator.methodcaller('setHost', 'old.reddit.com'),
}

def redirect_intercept(info):
    """Block the given request if necessary."""
    if (info.resource_type != interceptor.ResourceType.main_frame
            or info.request_url.scheme() in {"data", "blob"}):
        return

    url = info.request_url
    # message.info(url.host())
    redir = REDIRECT_MAP.get(url.host())
    if redir is not None and redir(url) is not False:
        message.info("Redirecting to " + url.toString())
        info.redirect(url)

# idea here: you could have an interceptor that does the url note check for emacs
if initial_start:
    interceptor.register(redirect_intercept)

adblock_file = os.environ["HOME"] + '/.config/qutebrowser/adblock.txt'
if os.path.exists(adblock_file):
    c.content.host_blocking.lists = [
        'https://raw.githubusercontent.com/stevenblack/hosts/master/hosts',
        'file://' + adblock_file,
        ]
