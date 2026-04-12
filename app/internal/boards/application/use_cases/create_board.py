"""
Use Case: Crear Tablero - CORREGIDO

Error original:
  "cover_image_url is an invalid keyword argument for Board"

El modelo Board de dominio no acepta cover_image_url en la creación.
Ese campo solo se puede asignar via UPDATE. Lo quitamos del constructor.
"""


class CreateBoardUseCase:
    def __init__(self, board_repository):
        self._repo = board_repository

    async def execute(
        self,
        user_id: str,
        name: str,
        description: str = None,
        is_private: bool = False,
        is_collaborative: bool = False,
    ):
        """
        Crea un nuevo tablero para el usuario.
        cover_image_url NO se pasa aquí — solo se puede actualizar después.
        """
        board = await self._repo.create(
            user_id=user_id,
            name=name,
            description=description,
            is_private=is_private,
            is_collaborative=is_collaborative,
        )
        return board