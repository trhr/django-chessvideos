import requests
import base64
from html.parser import HTMLParser


class ParseFIDE(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag in "img":
            for name, value in attrs:
                if "class" in name:
                    if "profile-top__photo" in value:
                        for name2, value2 in attrs:
                            if "src" in name2:
                                print(value2[23:])
                                with open('test.jpg','wb') as photo:
                                    photo.write(base64.b64decode(value2[23:]))



url="https://ratings.fide.com/profile/13400665"

r = requests.get(url)
parser = ParseFIDE()
parser.feed(r.text)