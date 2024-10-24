import urllib.request
import xml.etree.ElementTree as ET
import re
from html.parser import HTMLParser
from abc import ABC, abstractmethod
from html import unescape
from copy import deepcopy
try: import gc; gc.enable()
except: pass

class FeedNews(ABC):
    def __init_subclass__(self) -> None:
        self.schema = {}
        self.articles = []
        self.rss_link = ""
        self.out_minicast_dir = ""
        self.out_feeds_dir = ""
        self.mime = "application/rss+xml; charset=UTF-8"
        return super().__init_subclass__()
    @abstractmethod
    def consume_feed() -> bool: pass
    @abstractmethod
    def parse_feed() -> None: pass

class HackDay(FeedNews):
    def __init__(self) -> None:
        self.schema = {
            "title": str,
            "pub_date": str,
            "raw_html": str,
            "description": str,
            "content": [],
            "link": str,
            "creator": str,
            "category": []
        }

        self.articles = []
        self.rss_link = "https://hackaday.com/blog/feed/"
        self.out_minicast_dir = "./sounds/"
        self.out_feeds_dir = "./feeds/"
         
    def consume_feed(self) -> bool:
        try:
            with urllib.request.urlopen(self.rss_link, timeout=30) as feed:
                if feed.status == 200 and feed.getheaders()[2][1] == self.mime:
                    with open(f"{self.out_feeds_dir}feed.xml", "wb") as file:
                        file.write(feed.read())
                        return True
        except:
            return False

    def parse_feed(self) -> None:
        root = ET.parse("./feeds/feed.xml")
        items = []
        description_re = r"<\/div>(.*)<a"
        content_re = r"<p>(.*)<\/p>"
        
        for child in root.iter():
            if child.tag == "item":
                items.append(child)
        
        def iter_elements(html, tag):
            matches = ""
            if tag == "description":
                matches = re.finditer(description_re, html, re.MULTILINE)
            
            if tag == "content":
                matches = re.finditer(content_re, html, re.MULTILINE)
                stanzas = []
            
            if tag == "" or tag == None:
                return
                
            for matchNum, match in enumerate(matches, start=1):
                for groupNum in range(0, len(match.groups())):
                    groupNum = groupNum + 1
                    
                    if tag == "description":
                        return unescape(match.group(groupNum))
                    
                    if tag == "content":
                       stanzas.append(unescape(match.group(groupNum)))
            
            if len(stanzas) > 0 and tag == "content":
                return stanzas
            
        def explode(data):
            let = deepcopy(self.schema)
            for element in data:
                if element.tag == 'title': let["title"] = element.text
                if element.tag == 'link': let["link"] = element.text
                if element.tag == 'description': let["description"] = iter_elements(element.text, "description")
                if element.tag == 'pubDate': let["pub_date"] = element.text
                if element.tag == 'category': let['category'].append(element.text)  
                if element.tag == '{http://purl.org/dc/elements/1.1/}creator':
                    let["creator"] = element.text
                if element.tag == "{http://purl.org/rss/1.0/modules/content/}encoded":
                    let["content"] = iter_elements(element.text, "content")
                    return let
        
        self.articles = list(map(explode, items))