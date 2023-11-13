
class TwoKeyDict:
    def __init__(self):
        self.data = {}
        self.key1 = {}
        self.key2 = {}

    def set(self, key1, key2, value):
        unique_id = (key1, key2)  # Создание уникального идентификатора
        self.data[unique_id] = value
        self.key1[key1] = unique_id
        self.key2[key2] = unique_id

    def get_by_key1(self, key1):
        unique_id = self.key1.get(key1)
        return self.data.get(unique_id)

    def get_by_key2(self, key2):
        unique_id = self.key2.get(key2)
        return self.data.get(unique_id)

    def get_key1_by_key2(self, key2):
        unique_id = self.key2.get(key2)
        if unique_id is not None:
            key1, _ = unique_id
            return key1
        return None

    def get_key2_by_key1(self, key1):
        unique_id = self.key1.get(key1)
        if unique_id is not None:
            _, key2 = unique_id
            return key2
        return None

    def del_by_key1(self, key1):
        unique_id = self.key1.pop(key1, None)
        if unique_id:
            key2 = unique_id[1] # Также удаляем соответствующий ключ из key2_to_id
            self.key2.pop(key2, None)
            del self.data[unique_id]

    def del_by_key2(self, key2):
        unique_id = self.key2.pop(key2, None)
        if unique_id:
            key1 = unique_id[0] # Также удаляем соответствующий ключ из key1_to_id
            self.key1.pop(key1, None)
            del self.data[unique_id]