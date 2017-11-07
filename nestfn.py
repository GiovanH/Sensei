class fn:
    def __init__(self, f, a, r=False):
        """Prepares function f with argument a"""
        if r is False:
            self.f = f
            self.a = a
        else:
            self.f = f
            self.a = fn(a[0], a[1])

    def exe(self):
        """Executes prepared function"""
        if type(self.a) is fn:
            return self.f(self.a.exe())
        else:
            if self.a is None:
                return self.f()
            else:
                return self.f(self.a)
