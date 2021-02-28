import csv
from time import sleep

import requests
import base64
from html.parser import HTMLParser
import re

class ParseFIDE(HTMLParser):
    def __init__(self, fide_name):
        super().__init__()
        self.name=str(fide_name)

    def handle_starttag(self, tag, attrs):
        if tag in "img":
            for name, value in attrs:
                if "class" in name:
                    if "profile-top__photo" in value:
                        try:
                            for name2, value2 in attrs:
                                if "src" in name2:
                                    try:
                                        filename=f'{str(self.name)}.jpg'
                                        with open(filename,'wb') as photo:
                                            photo.write(base64.b64decode(value2[23:]))
                                    except Exception as e:
                                        print(f"Could not write: {self.name} {e} {value2[23:]}")
                        except Exception as e:
                            print(f"Could not find photo: {e}")


with open('grandmasters.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
        fide_id = row[1]
        fide_name = re.sub('\W+', '', row[0])
        print(f"Processing {fide_name}")
        url = f"https://ratings.fide.com/profile/{fide_id}"
        try:
            r = requests.get(url)
            parser = ParseFIDE({fide_name})
            parser.feed(r.text)
        except Exception as e:
            print(f"Could not parse {fide_id} from server: {e}")

        with open('grandmaster_images.csv','a') as csvwriter:
            writer = csv.writer(csvwriter)
            writer.writerow([fide_name, f"{fide_name}.jpg"])

        sleep(4)

