"""
Object pool - reuses Projectile/Particle instances to reduce GC pressure.
"""


class ObjectPool:
    def __init__(self, factory, reset_fn=None, max_size=512):
        self.factory = factory
        self.reset_fn = reset_fn or (lambda o, *a, **kw: o)
        self.free = []
        self.in_use = []
        self.max_size = max_size

    def acquire(self, *args, **kwargs):
        if self.free:
            obj = self.free.pop()
        else:
            obj = self.factory(*args, **kwargs)
        self.reset_fn(obj, *args, **kwargs)
        self.in_use.append(obj)
        return obj

    def release(self, obj):
        try:
            self.in_use.remove(obj)
        except ValueError:
            pass
        if len(self.free) < self.max_size:
            self.free.append(obj)

    def release_dead(self, is_alive):
        survivors = []
        for o in self.in_use:
            if is_alive(o):
                survivors.append(o)
            else:
                if len(self.free) < self.max_size:
                    self.free.append(o)
        self.in_use = survivors

    def __len__(self):
        return len(self.in_use)
