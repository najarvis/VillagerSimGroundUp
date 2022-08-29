from .tile import Tile

class Snow(Tile):

    def __init__(self) -> None:
        super().__init__()
        self.color = (255, 255, 255)
