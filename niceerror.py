from collections.abc import MutableSequence


class NicerErrorList(MutableSequence):
    """
    This class pretends to be a list, except it returns
    a much more useful error description if the user indexes an empty array.

    This is to mitigate a common beginners issue where an array is indexed
    without checking that the array has any items
    """

    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        try:
            self.data[item]
        except IndexError as e:
            if len(self.data) == 0:
                raise IndexError("Trying to index an empty list")
            else:
                raise e

    def __setitem__(self, key, value):
        self.data[key] = value

    def insert(self, index, value):
        self.data.insert(index, value)

    def __len__(self):
        return len(self.data)
