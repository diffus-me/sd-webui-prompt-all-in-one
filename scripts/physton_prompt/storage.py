import os
import json
import pathlib
import time

from modules.paths import Paths

class Storage:
    @staticmethod
    def __init__(p: Paths):
        Storage.__dispose_all_locks(p)

    @staticmethod
    def __get_storage_path(p: Paths):
        # Storage.storage_path = os.path.dirname(os.path.abspath(__file__)) + '/../../storage'
        # Storage.storage_path = os.path.normpath(Storage.storage_path)
        storage_path = pathlib.Path(p.workdir(), "prompt-all-in-one", "storage")
        storage_path.mkdir(parents=True, exist_ok=True)

        # old_storage_path = os.path.join(Path().absolute(), 'physton-prompt')
        # if os.path.exists(old_storage_path):
        #     # 复制就的存储文件到新的存储文件夹
        #     for file in os.listdir(old_storage_path):
        #         old_file_path = os.path.join(old_storage_path, file)
        #         new_file_path = os.path.join(Storage.storage_path, file)
        #         if not os.path.exists(new_file_path):
        #             os.rename(old_file_path, new_file_path)
        #     # 删除旧的存储文件夹
        #     os.rmdir(old_storage_path)

        return str(storage_path)

    @staticmethod
    def __get_data_filename(p: Paths, key):
        return Storage.__get_storage_path(p) + '/' + key + '.json'

    @staticmethod
    def __get_key_lock_filename(p: Paths, key):
        return Storage.__get_storage_path(p) + '/' + key + '.lock'

    @staticmethod
    def __dispose_all_locks(p: Paths):
        directory = Storage.__get_storage_path(p)
        for filename in os.listdir(directory):
            # 检查文件是否以指定后缀结尾
            if filename.endswith('.lock'):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                    print(f"Disposed lock: {file_path}")
                except Exception as e:
                    print(f"Dispose lock {file_path} failed: {e}")

    @staticmethod
    def __lock(p: Paths, key):
        file_path = Storage.__get_key_lock_filename(p, key)
        with open(file_path, 'w') as f:
            f.write('1')

    @staticmethod
    def __unlock(p: Paths, key):
        file_path = Storage.__get_key_lock_filename(p, key)
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def __is_locked(p: Paths, key):
        file_path = Storage.__get_key_lock_filename(p, key)
        return os.path.exists(file_path)

    @staticmethod
    def __get(p: Paths, key):
        filename = Storage.__get_data_filename(p, key)
        if not os.path.exists(filename):
            return None
        if os.path.getsize(filename) == 0:
            return None
        try:
            import launch
            if not launch.is_installed("chardet"):
                with open(filename, 'r') as f:
                    data = json.load(f)
            else:
                import chardet
                with open(filename, 'rb') as f:
                    data = f.read()
                    encoding = chardet.detect(data).get('encoding')
                    data = json.loads(data.decode(encoding))
        except Exception as e:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                print(e)
                return None
        return data

    @staticmethod
    def __set(p: Paths, key, data):
        file_path = Storage.__get_data_filename(p, key)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=True)

    @staticmethod
    def set(p: Paths, key, data):
        while Storage.__is_locked(p, key):
            time.sleep(0.01)
        Storage.__lock(p, key)
        try:
            Storage.__set(p, key, data)
            Storage.__unlock(p, key)
        except Exception as e:
            Storage.__unlock(p, key)
            raise e

    @staticmethod
    def get(p: Paths, key):
        return Storage.__get(p, key)

    @staticmethod
    def delete(p: Paths, key):
        file_path = Storage.__get_data_filename(p, key)
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def __get_list(p: Paths, key):
        data = Storage.get(p, key)
        if not data:
            data = []
        return data

    # 向列表中添加元素
    @staticmethod
    def list_push(p: Paths, key, item):
        while Storage.__is_locked(p, key):
            time.sleep(0.01)
        Storage.__lock(p, key)
        try:
            data = Storage.__get_list(p, key)
            data.append(item)
            Storage.__set(p, key, data)
            Storage.__unlock(p, key)
        except Exception as e:
            Storage.__unlock(p, key)
            raise e

    # 从列表中删除和返回最后一个元素
    @staticmethod
    def list_pop(p: Paths, key):
        while Storage.__is_locked(p, key):
            time.sleep(0.01)
        Storage.__lock(p, key)
        try:
            data = Storage.__get_list(p, key)
            item = data.pop()
            Storage.__set(p, key, data)
            Storage.__unlock(p, key)
            return item
        except Exception as e:
            Storage.__unlock(p, key)
            raise e

    # 从列表中删除和返回第一个元素
    @staticmethod
    def list_shift(p: Paths, key):
        while Storage.__is_locked(p, key):
            time.sleep(0.01)
        Storage.__lock(p, key)
        try:
            data = Storage.__get_list(p, key)
            item = data.pop(0)
            Storage.__set(p, key, data)
            Storage.__unlock(p, key)
            return item
        except Exception as e:
            Storage.__unlock(p, key)
            raise e

    # 从列表中删除指定元素
    @staticmethod
    def list_remove(p: Paths, key, index):
        while Storage.__is_locked(p, key):
            time.sleep(0.01)
        Storage.__lock(p, key)
        data = Storage.__get_list(p, key)
        data.pop(index)
        Storage.__set(p, key, data)
        Storage.__unlock(p, key)

    # 获取列表中指定位置的元素
    @staticmethod
    def list_get(p: Paths, key, index):
        data = Storage.__get_list(p, key)
        return data[index]

    # 清空列表中的所有元素
    @staticmethod
    def list_clear(p: Paths, key):
        while Storage.__is_locked(p, key):
            time.sleep(0.01)
        Storage.__lock(p, key)
        try:
            Storage.__set(p, key, [])
            Storage.__unlock(p, key)
        except Exception as e:
            Storage.__unlock(p, key)
            raise e
