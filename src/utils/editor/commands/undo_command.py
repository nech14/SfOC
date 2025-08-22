from src.utils.editor.commands.base_command import BaseCommand


class UndoCommand(BaseCommand):
    def execute(self) -> bool:
        self._editor.undo()
        return False
