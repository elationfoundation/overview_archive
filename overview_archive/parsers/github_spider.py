import scrapy
from urllib.parse import urlparse

class GithubSpider(scrapy.Spider):
    name = 'github'

    def __init__(self, url=None, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        if not self.is_github(url):
            raise ValueError("Not a githib url. Spider will not continue.")
        #TODO
        self.entity = self.get_entity(url)

    def is_github(self, link):
        try:
            parsed_url = urlparse(link)
            if parsed_url.netloc == 'github.com':
                return True
        except ValueError:
            return False
        return False

    def is_github_gist(self, link):
        try:
            parsed_url = urlparse(link)
            if parsed_url.netloc == 'gist.github.com':
                return True
        except ValueError:
            return False
        return False

    def is_github_entity(self, link):
        try:
            parsed_url = urlparse(link)
            # Github entities (users and projects) have a single word in the path.
            if parsed_url.netloc == 'github.com':
                path = [x for x in str.split(parsed_url.path, "/") if x != '']
                if len(path) == 1:
                    return True
        except ValueError:
            return False
        return False

    def is_github_repo_top(self, link):
        try:
            parsed_url = urlparse(link)
            # The top level of github repos have two words as the path.
            if parsed_url.netloc == 'github.com':
                path = [x for x in str.split(parsed_url.path, "/") if x != '']
                if len(path) == 1:
                    return True
        except ValueError:
            return False
        return False
