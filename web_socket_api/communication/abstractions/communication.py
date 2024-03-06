import abc

class ISubscriber(abc.ABC):
    """
    Class base for a publish
    """

    def subscribe(self, to: str):
        """
        Subscribe events
        """
        raise NotImplementedError("Method send events not implemented")
