import abc


class StorageProtocol(abc.ABC):
    @abc.abstractmethod
    def save_pif(self, pif_obj):
        raise NotImplementedError

    @abc.abstractmethod
    def get_open_pifs(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_pif(self, post_id):
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_all_pifs(self):
        raise NotImplementedError

    @abc.abstractmethod
    def open_pif_exists(self, post_id):
        raise NotImplementedError
