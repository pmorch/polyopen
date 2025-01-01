from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class XdgOpenPath:
    publisherHostnames: list[str]
    path: str


@dataclass
class XdgOpenPathWithField:
    xdgOpenPath: XdgOpenPath


@dataclass
class XdgOpenURL:
    URL: str


@dataclass
class XdgOpenURLWithField:
    xdgOpenURL: XdgOpenURL


Message = XdgOpenPathWithField | XdgOpenURLWithField


# deriving from messages.HandleMessage ensures we get quick errors if we're not
# handling all the message types. So please don't create multiple other if elif
# else statements than this one.
class HandleMessage(ABC):
    def handle(self, topic: str, message: Message):
        if isinstance(message, XdgOpenPathWithField):
            self.handleXdgOpenPath(topic, message.xdgOpenPath)
        elif isinstance(message, XdgOpenURLWithField):
            self.handleXdgOpenURL(topic, message.xdgOpenURL)
        else:
            raise ValueError("Unknown message type:", message)

    @abstractmethod
    def handleXdgOpenPath(self, topic: str, message: XdgOpenPath):
        """Override this in derived classes"""
        raise NotImplementedError()

    @abstractmethod
    def handleXdgOpenURL(self, topic: str, message: XdgOpenURL):
        """Override this in derived classes"""
        raise NotImplementedError()
