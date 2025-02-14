from scripts.physton_prompt.storage import Storage
import uuid
import time
from modules.paths import Paths

class History:
    histories = {
        'txt2img': [],
        'txt2img_neg': [],
        'img2img': [],
        'img2img_neg': [],
    }
    favorites = {
        'txt2img': [],
        'txt2img_neg': [],
        'img2img': [],
        'img2img_neg': [],
    }
    max = 100

    def __init__(self):
        # for type in self.histories:
        #     self.histories[type] = Storage.get('history.' + type)
        #     if self.histories[type] is None:
        #         self.histories[type] = []
        #         self.__save_histories(type)
        #
        # for type in self.favorites:
        #     self.favorites[type] = Storage.get('favorite.' + type)
        #     if self.favorites[type] is None:
        #         self.favorites[type] = []
        #         self.__save_favorites(type)
        pass

    def __save_histories(self, p: Paths, type, records):
        Storage.set(p, 'history.' + type, records)

    def __save_favorites(self, p: Paths, type, records):
        Storage.set(p, 'favorite.' + type, records)

    def __get_histories(self, p: Paths, type):
        histories = Storage.get(p, 'history.' + type)
        if histories is None:
            histories = []
        return histories

    def __get_favorites(self, p: Paths, type):
        favorites = Storage.get(p, 'favorite.' + type)
        if favorites is None:
            favorites = []
        return favorites

    def get_histories(self, p: Paths, type):
        histories = self.__get_histories(p, type)
        for history in histories:
            history['is_favorite'] = self.is_favorite(p, type, history['id'])
        return histories

    def is_favorite(self, p: Paths, type, id):
        favorites = self.__get_favorites(p, type)
        for favorite in favorites:
            if favorite['id'] == id:
                return True
        return False

    def get_favorites(self, p: Paths, type):
        return self.__get_favorites(p, type)

    def push_history(self, p: Paths, type, tags, prompt, name=''):
        histories = self.__get_histories(p, type)
        if len(histories) >= self.max:
            histories.pop(0)
        item = {
            'id': str(uuid.uuid1()),
            'time': int(time.time()),
            'name': name,
            'tags': tags,
            'prompt': prompt,
        }
        histories.append(item)
        self.__save_histories(p, type, histories)
        return item

    def push_favorite(self, p: Paths, type, tags, prompt, name=''):
        item = {
            'id': str(uuid.uuid1()),
            'time': int(time.time()),
            'name': name,
            'tags': tags,
            'prompt': prompt,
        }
        favorites = self.__get_favorites(p, type)
        favorites.append(item)
        self.__save_favorites(p, type, favorites)
        return item

    def move_up_favorite(self, p: Paths, type, id):
        favorites = self.__get_favorites(p, type)
        for index, favorite in enumerate(favorites):
            if favorite['id'] == id:
                if index > 0:
                    favorites.insert(index - 1, favorites.pop(index))
                    self.__save_favorites(p, type, favorites)
                    return True
                return False
        return False

    def move_down_favorite(self, p: Paths, type, id):
        favorites = self.__get_favorites(p, type)
        for index, favorite in enumerate(favorites):
            if favorite['id'] == id:
                if index < len(favorites) - 1:
                    favorites.insert(index + 1, favorites.pop(index))
                    self.__save_favorites(p, type, favorites)
                    return True
                return False
        return False

    def get_latest_history(self, p: Paths, type):
        histories = self.__get_histories(p, type)
        if len(histories) > 0:
            return histories[-1]
        return None

    def set_history(self, p: Paths, type, id, tags, prompt, name):
        histories = self.__get_histories(p, type)
        for history in histories:
            if history['id'] == id:
                history['tags'] = tags
                history['prompt'] = prompt
                history['name'] = name
                self.__save_histories(p, type, histories)
                if self.is_favorite(p, type, id):
                    self.set_favorite(p, type, id, tags, prompt, name)
                return True
        return False

    def set_favorite(self, p: Paths, type, id, tags, prompt, name):
        favorites = self.__get_favorites(p, type)
        for favorite in favorites:
            if favorite['id'] == id:
                favorite['tags'] = tags
                favorite['prompt'] = prompt
                favorite['name'] = name
                self.__save_favorites(p, type, favorites)
                return True
        return False

    def set_history_name(self, p: Paths, type, id, name):
        histories = self.__get_histories(p, type)
        favorites = self.__get_favorites(p, type)
        for history in histories:
            if history['id'] == id:
                history['name'] = name
                for favorite in favorites:
                    if favorite['id'] == id:
                        favorite['name'] = name
                self.__save_histories(p, type, histories)
                self.__save_favorites(p, type, favorites)
                return True
        return False

    def set_favorite_name(self, p: Paths, type, id, name):
        favorites = self.__get_favorites(p, type)
        histories = self.__get_histories(p, type)
        for favorite in favorites:
            if favorite['id'] == id:
                favorite['name'] = name
                self.__save_favorites(p, type, favorites)
                for history in histories:
                    if history['id'] == id:
                        history['name'] = name
                self.__save_histories(p, type, histories)
                self.__save_favorites(p, type, favorites)
                return True
        return False

    def dofavorite(self, p: Paths, type, id):
        favorites = self.__get_favorites(p, type)
        if self.is_favorite(p, type, id):
            return False
        histories = self.__get_histories(p, type)
        for history in histories:
            if history['id'] == id:
                favorites.append(history)
                self.__save_favorites(p, type, favorites)
                return True
        return False

    def unfavorite(self, p: Paths, type, id):
        favorites = self.__get_favorites(p, type)
        if not self.is_favorite(p, type, id):
            return False
        for favorite in favorites:
            if favorite['id'] == id:
                favorites.remove(favorite)
                self.__save_favorites(p, type, favorites)
                return True
        return False

    def remove_history(self, p: Paths, type, id):
        histories = self.__get_histories(p, type)
        for history in histories:
            if history['id'] == id:
                histories.remove(history)
                self.__save_histories(p, type, histories)
                return True
        return False

    def remove_histories(self, p: Paths, type):
        histories = []
        self.__save_histories(p, type, histories)
        return True
