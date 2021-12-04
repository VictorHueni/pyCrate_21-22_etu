class Actor:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def set_x(self, _x):
        self.x = _x

    def set_y(self, _y):
        self.y = _y

