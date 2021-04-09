import zipfile
from io import BytesIO

import requests
import os
from datetime import datetime, timedelta


class TrancoList():
    def __init__(self, date, list_id, lst):
        self.date = date
        self.list_id = list_id
        self.list_page = "https://tranco-list.eu/list/{}/1000000".format(list_id)
        self.list = lst

    def top(self, num=1000000):
        return self.list[:num]

    def rank(self, domain):
        try:
            return self.list.index(domain) + 1
        except ValueError:
            return -1

class Tranco():
    def __init__(self, **kwargs):
        """
        :param kwargs:
            cache: <bool> enables/disables caching, default: True
            cache_dir: <str> directory used to cache Tranco top lists, default: cwd + .tranco/
            account_email: <str> Account email address: retrieve from https://tranco-list.eu/account
            api_key: <str> API key: retrieve from https://tranco-list.eu/account
        """

        self.should_cache = kwargs.get('cache', True)
        self.cache_dir = kwargs.get('cache_dir', None)
        if self.cache_dir is None:
            cwd = os.getcwd()
            self.cache_dir = os.path.join(cwd, '.tranco')

        if self.should_cache and not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        self.account_email = kwargs.get('account_email')
        self.api_key = kwargs.get('api_key')

    def _cache_path(self, date):
        return os.path.join(self.cache_dir, date + '-DEFAULT.csv')

    def list(self, date=None, list_id=None):
        if date and list_id:
            raise ValueError("You can't pass a date as well as a list ID.")

        if not list_id:
            if (not date) or (date == 'latest'):  # no arguments given: default to latest list
                yesterday = (datetime.utcnow() - timedelta(days=1))
                date = yesterday.strftime('%Y-%m-%d')
            list_id = self._get_list_id_for_date(date)

        if self.should_cache and os.path.exists(self._cache_path(list_id)):
            with open(self._cache_path(list_id)) as f:
                top_list_text = f.read()
        else:
            top_list_text = self._download_zip_file(list_id)

        return TrancoList(date, list_id, list(map(lambda x: x[x.index(',') + 1:], top_list_text.splitlines())))

    def _get_list_id_for_date(self, date):
        r1 = requests.get('https://tranco-list.eu/daily_list_id?date={}'.format(date))
        if r1.status_code == 200:
            return r1.text
        else:
            raise AttributeError("The daily list for this date is currently unavailable.")

    def _download_zip_file(self, list_id):
        download_url = 'https://tranco-list.eu/download_daily/{}'.format(list_id)
        r = requests.get(download_url, stream=True)
        if r.status_code == 200:
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                with z.open('top-1m.csv') as csvf:
                    file_bytes = csvf.read()
                    if self.should_cache:
                        with open(self._cache_path(list_id), 'wb') as f:
                            f.write(file_bytes)
                    lst = file_bytes.decode("utf-8")
                    return lst
        elif r.status_code == 403:
            # List not available as ZIP file
            download_url = 'https://tranco-list.eu/download/{}/1000000'.format(list_id)
            r2 = requests.get(download_url)
            if r2.status_code == 200:
                file_bytes = r2.content
                if self.should_cache:
                    with open(self._cache_path(list_id), 'wb') as f:
                        f.write(file_bytes)
                lst = file_bytes.decode("utf-8")
                return lst
            else:
                raise AttributeError("The daily list for this date is currently unavailable.")
        elif r.status_code == 502:
            # List unavailable (bad gateway)
            raise AttributeError("The daily list for this date is currently unavailable.")
        else:
            # List unavailable (non-success status code)
            raise AttributeError("The daily list for this date is currently unavailable.")

    def configure(self, configuration):
        """
        Configure a custom list (https://tranco-list.eu/configure).
        Requires that valid credentials were passed when creating the `Tranco` object.
        :param configuration: dictionary that conforms to the following schema
                              (https://tranco-list.eu/api_documentation#datatypes-configuration):
                            ```
                            {
                              "providers": [
                                String("alexa"|"majestic"|"umbrella")
                              ],
                              "startDate": Date(YYYY-mm-dd),
                              "endDate": Date(YYYY-mm-dd),
                              "combinationMethod": String("dowdall"|"borda"),
                              "listPrefix": Integer|"full",  # Only aggregate domains from the list prefixes of length
                              "filterPLD": "on"|"off"  # Whether to retain only pay-level domains
                            }
                            ```
        :return Tuple[bool, str]: whether the list is already available; the ID (to be) assigned to this list.
        Use `list_metadata` with this ID to (continuously) check whether the list has finished generating
         and is now available.
        :raise ValueError if list generation failed
        """

        if not self.account_email or not self.api_key:
            raise ValueError("You have not supplied valid credentials.")

        if not isinstance(configuration, dict):
            raise ValueError("You supplied an invalid configuration.")

        r = requests.put(
            "https://tranco-list.eu/api/lists/create",
            auth=(self.account_email, self.api_key),
            json=configuration
        )

        if r.status_code == 200 or r.status_code == 202:
            # 200: list already exists (available=True); 202: list is being generated (available=False)
            response = r.json()
            return response["available"], response["list_id"]
        elif r.status_code == 400:
            raise ValueError("You supplied an invalid configuration.")
        elif r.status_code == 401:
            raise ValueError("You supplied invalid credentials.")
        elif r.status_code == 429:
            raise ValueError("You are already generating a list.")
        elif r.status_code == 403 or r.status_code == 502 or r.status_code == 503:
            raise ValueError("This service is temporarily unavailable.")

    def list_metadata(self, list_id):
        """
        Retrieve metadata for list (whether it is already available, what its configuration is, ...)
        :param list_id: ID of the list for which to query metadata
        :return: dictionary with the following information:
        ```
        {
          "list_id": String,
          "available": Boolean,
          "download": String,
          "created_on":
            Date(YYYY-mm-ddTHH:MM:SS.ffffff),
          "configuration": Configuration,
          "failed": Boolean,
          "jobs_ahead": Integer
        }
        ```
        """
        r = requests.get("https://tranco-list.eu/api/lists/id/{list_id}".format(list_id=list_id))
        if r.status_code == 404:
            raise ValueError("There is no list with the given ID.")
        else:
            return r.json()
