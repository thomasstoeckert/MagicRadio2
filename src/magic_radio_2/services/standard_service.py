from abc import ABC, abstractmethod

class StandardService(ABC):
    @abstractmethod
    def start_service(self):
        pass
    
    @abstractmethod
    def stop_service(self):
        pass