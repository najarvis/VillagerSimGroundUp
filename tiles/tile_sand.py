from tile import Tile

class Sand(Tile):

    def __init__(self) -> None:
        super().__init__()
        self.color = (194, 178, 128)