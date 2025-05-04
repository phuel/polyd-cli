class Delegate:
    '''Handles a list of methods and functions
    Usage:
        d = Delegate()
        d += function    # Add function to end of delegate list
        d(*args, **kw)   # Call all functions, returns a list of results
        d -= function    # Removes last matching function from list
        d -= object      # Removes all methods of object from list
    '''
    def __init__(self):
        self.__delegates = []

    def __iadd__(self, callback):
        self.__delegates.append(callback)
        return self

    def __isub__(self, callback):
        # If callback is a class instance,
        # remove all callbacks for that instance
        self.__delegates = [ cb
            for cb in self.__delegates
                if getattr(cb, 'im_self', None) != callback]

        # If callback is callable, remove the last
        # matching callback
        if callable(callback):
            for i in range(len(self.__delegates)-1, -1, -1):
                if self.__delegates[i] == callback:
                    del self.__delegates[i]
                    return self
        return self

    def __call__(self, *args, **kw):
        return [ callback(*args, **kw)
            for callback in self.__delegates]

