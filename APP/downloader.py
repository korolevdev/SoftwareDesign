import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.exceptions import HTTPError
import ssl


class EncodedSatData:

    def __init__(self, fmt, data, compressed=False, url="localhost"):
        self.fmt = fmt
        self.data = data
        self.compressed = compressed
        self.url = url


class SecureAdapter(HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


class DownloaderError(Exception):

    def __init__(self, err):
        self.value = err

    def __str__(self):
        return repr(self.value)


class Downloader:

    def __init__(self, cfg="sources.list"):
        self.urls = []
        self.http = requests.Session()
        self.http.mount("https://", SecureAdapter())
        try:
            with open(cfg, 'r') as f:
                for line in f:
                    line = line.strip()
                    [fmt, compressed, url] = line.split()
                    self.urls.append((fmt, bool(compressed), url))
        except (EnvironmentError, ValueError) as e:
            raise DownloaderError("could not read config file: " + str(e))

    def fetch(self, url):
        response = self.http.get(url, timeout=10)
        response.raise_for_status()
        return response.content.decode(response.encoding)

    def get_data(self):
        for fmt, compressed, url in self.urls:
            print("fetching " + fmt + " from " + url + " ...")

            data = None
            try:
                data = self.fetch(url)
                yield EncodedSatData(fmt, data, compressed, url)
            except HTTPError as e:
                print("failed to fetch: " + str(e))
