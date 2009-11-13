class Base(object):
    """
    Base object to handle setting the required __parent__ and __name__ attributes
    """
    def __init__(self,parent = None,name = None):
        self.__parent__ = parent
        self.__name__ = self.__class__.__name__.lower()

class SLCS(Base):
    """
    SLCS object
    """
    def __init__(self, parent=None, name=None):
        Base.__init__(self, parent, name)
        self._certificates = {}

    def store(self, session, certificate):
        self._certificates[session] = certificate

    def get(self, session):
        if self._certificates.has_key(session):
            return self._certificates[session]
        return None

class MyProxy(Base):
    """
    MyProxy Object
    """
    pass

class Root(Base):
    """
    Root object which has a foo attribute and a bar attribute, and implements __getitem__
    """
    __parent__ = None
    __name__ = None
    def __init__(self):
        self.slcs = SLCS(self)
        self.myproxy = MyProxy(self)


    def __getitem__(self,key):
        if hasattr(self,str(key)):
            return getattr(self,key,None)
        else:
            raise KeyError, key

root = Root()


def get_root(request):
    return root
