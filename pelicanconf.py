AUTHOR = 'ZeroToDev'
SITENAME = 'ZeroToDev'
SITESUBTITLE = 'From Zero To Developer'
SITEURL = "https://zerotodev-4jq.pages.dev"

PATH = "content"
THEME = "theme"

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = 'zh'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = [
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
]

# Social widget
SOCIAL = [
    ("GitHub", "https://github.com/zerotodev"),
    ("Gitee", "https://gitee.com/zerotodev"),
]

# Display settings
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False

DEFAULT_PAGINATION = 10

# Use relative URLs for local development
RELATIVE_URLS = True

# Static files configuration
STATIC_PATHS = ['images', 'static', 'extra']
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
}
