from src.editor.commands.base_command import BaseCommand


class CommandHistory:
    __history = []

    def push(self, command: BaseCommand):
        self.__history.append(command)

    def pop(self):
        return self.__history.pop()
