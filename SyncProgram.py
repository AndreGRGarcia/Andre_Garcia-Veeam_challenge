from collections.abc import Callable, Iterable, Mapping
import sys
from threading import Thread
from time import sleep
from typing import Any
import os
import filecmp
import shutil
from pathlib import Path


class Syncher:

    allowed_keys = {'source_path', 'replica_path', 'logs_path', 'sync_interval'}

    source_path = "."
    replica_path = ""
    logs_path = ""
    sync_interval = "10"

    def __init__(self, **kwargs):
        # Update the attributes of object Syncher.
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in self.allowed_keys)
        
        # Check if the sync_interval given is a number.
        if not self.sync_interval.isdigit():
            print("\"sync_interval\" must be an integer number in seconds!")
            exit(1)
        self.sync_interval = int(self.sync_interval)

        # Start the synching.
        self.start_sync()

    def start_sync(self) -> None:
        """ This method will start the synching process. """

        updater = Updater(self.source_path, self.replica_path, self.logs_path, self.sync_interval)
        updater.start()

        sleep(1)

        while True:
            response = input("Type \"help\" to see available commands.\n")
            match response:
                case "q" | "Q" | "quit" | "Quit" | "exit" | "Exit" | "close" | "Close":
                    print("Goodbye!")
                    exit(0)
                case "help":
                    print("")
                    print("[HELP PAGE]")
                    print("\"q\": Quit.")
                    print("\"help\": Show this list")
                    print("")
                case _:
                    print("Not a recognized command!")


class Updater(Thread):

    def __init__(self, source_path, replica_path, logs_path, sync_interval):
        Thread.__init__(self)

        self.source_path = source_path
        self.replica_path = replica_path
        self.logs_path = logs_path
        self.sync_interval = sync_interval

        self.daemon = True

    def run(self) -> None:
        self.sync_and_sleep()

    def sync_and_sleep(self) -> None:
        while True:
            self.sync_files()
            sleep(self.sync_interval)

    def sync_files(self) -> None: # TODO
        
        for root, dirs, files in os.walk(self.source_path):
            for file in files:
                source_file = os.path.join(root, file)
                replica_file = os.path.join(root.replace(self.source_path, self.replica_path), file)
                

                # If source_file is not in replica/file is different from replica's, copy-paste it.
                if not os.path.exists(replica_file) or not filecmp.cmp(source_file, replica_file, shallow=False): # TODO
                    shutil.copyfile(source_file, replica_file)

                
                # If file is different from replica's, replace it.
                if filecmp.cmp(source_file, replica_file, shallow=False): # TODO
                    shutil.copyfile(source_file, replica_file)
                
                    
            for dir in dirs: # TODO
                # If dir is not in replica, create it
                if not os.path.exists(os.path.join(root, dir)): # TODO
                    pass
        

            

        



def main():

    args = {}
    if len(sys.argv) > 1:
        args = dict([arg.split('=', maxsplit=1) for arg in sys.argv[1:]])
        #print(args)

    if "replica_path" not in args.keys() or "logs_path" not in args.keys():
        print("Syncher needs, at least, arguments \"replica_path\" and \"logs_path\" to work!")
        exit(1)

    s = Syncher(**args)


if __name__ == "__main__":
    main()