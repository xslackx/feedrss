from abs.consume_feed import FeedNews
from syndication import *

class LinuxMagazine(FeedNews):
    def __init__(self) -> None:
        self.schema["origin"] = "LinuxMagazine"
        self.rss_link = "https://www.linux-magazine.com/rss/feed/lmi_news"
        self.feed_file = f"{self.out_feeds_dir}{urllib.parse.urlsplit(self.rss_link).netloc}.feed.xml"

        try:
            self.check_out_dirs()
        except: raise Exception("Cannot create the out_minicast_dir or out_feeds_dir in FeedNews abs")

        super().__init__()
        
    
    def parse_feed() -> bool:
        pass