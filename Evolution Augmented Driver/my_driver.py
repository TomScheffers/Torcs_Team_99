from pytocl.driver import Driver
from pytocl.car import State, Command


class MyDriver(Driver):
    print("test")
    # Override the `drive` method to create your own driver
    ...
    # def drive(self, carstate: State) -> Command:
    #     # Interesting stuff
    #     command = Command(...)
    #     return command
