class fn:
	def __init__(self,f,a,r=False):
		if r is False:
			self.f = f
			self.a = a
		else:
			self.f = f
			self.a = fn(a[0],a[1])
	def exe(self):
		if type(self.a) is fn:
			return self.f(self.a.exe())
		else:
			if self.a is not None:
				return self.f(self.a)
			else:
				return self.f()
