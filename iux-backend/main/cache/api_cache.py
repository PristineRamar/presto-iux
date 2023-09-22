# api_cache.py

import difflib
import json
import os

class APICache:
    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as file:
                return json.load(file)
        return {}

    def save_cache(self):
        with open(self.cache_file, 'w') as file:
            json.dump(self.cache, file)

    def is_similar(self, str1, str2):
        similarity_ratio = difflib.SequenceMatcher(None, str1, str2).ratio()
        return similarity_ratio >= 1.0

    def cache_response(self, api_name, prompt, json_response):
        api_cache = self.cache.get(api_name, {})
        api_cache[prompt] = json_response
        self.cache[api_name] = api_cache
        self.save_cache()

    def get_cached_response(self, api_name, prompt):
        api_cache = self.cache.get(api_name, {})
        for cached_prompt, json_response in api_cache.items():
            if self.is_similar(prompt, cached_prompt):
                return json_response
        return None

    def clear_cache_for_api(self, api_name):
        if api_name in self.cache:
            del self.cache[api_name]
            self.save_cache()
