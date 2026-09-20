class ResourcePool:
    """Tracks how many of each resource exist and how many are free right now."""

    def __init__(self, capacity):
        self.capacity = dict(capacity)   # total, e.g. {"bed": 10}
        self.free = dict(capacity)       # available right now

    def can_allocate(self, needs):
        """True only if EVERY resource in `needs` is available (all-or-nothing)."""
        return all(self.free.get(r, 0) >= n for r, n in needs.items())

    def allocate(self, needs):
        """Take resources. Refuses if anything is missing, so nothing is half-taken."""
        if not self.can_allocate(needs):
            raise ValueError(f"Not enough free resources for {needs}: free={self.free}")
        for r, n in needs.items():
            self.free[r] -= n

    def release(self, needs):
        """Give resources back. Errors if this would exceed total capacity."""
        for r, n in needs.items():
            self.free[r] += n
            if self.free[r] > self.capacity[r]:
                raise ValueError(f"Released too many {r}")

    def set_capacity(self, resource, new_capacity):
        """Change the total of a resource, e.g. staff going on or off shift.
        Patients already being treated keep their staff, so `free` can dip below 0
        until they finish. That just blocks new admissions in the meantime."""
        in_use = self.capacity[resource] - self.free[resource]
        self.capacity[resource] = new_capacity
        self.free[resource] = new_capacity - in_use