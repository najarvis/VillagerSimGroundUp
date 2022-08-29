from tile import Tile

class Stone(Tile):

    def __init__(self) -> None:
        super().__init__()
        self.color = (111, 122, 132 )
