from collections.abc import Callable, Iterable, Mapping
import sys
from threading import Thread
from time import sleep
from typing import Any
import os
import filecmp
import shutil
from pathlib import Path
from datetime import datetime;


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

        self.logger = Logger(self.logs_path)

        # Start the synching.
        self.start_sync()

    def start_sync(self) -> None:
        """ This method will start the synching process. """

        updater = Updater(self.source_path, self.replica_path, self.logs_path, self.sync_interval, self.logger)
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

    def __init__(self, source_path, replica_path, logs_path, sync_interval, logger):
        Thread.__init__(self)

        self.source_path = source_path
        self.replica_path = replica_path
        self.logs_path = logs_path
        self.sync_interval = sync_interval
        self.logger = logger

        self.daemon = True

    def run(self) -> None:
        self.sync_and_sleep()

    def sync_and_sleep(self) -> None:
        while True:
            self.sync_files()
            self.logger.log_sync_complete()
            sleep(self.sync_interval)

    def sync_files(self) -> None: # TODO

        files_visited = set()
        dirs_visited = set()
        dirs_copied = set()

        # Iterate over source to add and update files
        for root, dirs, files in os.walk(self.source_path):
            # Check if this root needs to be checked
            # (this is useful if the directories have a lot of files, there could be a condition to only run this snippet if wanted)
            replica_root_equivalent = root.replace(self.source_path, self.replica_path)
            tree = replica_root_equivalent.split(os.sep)
            found = False
            for i in range(len(tree)-1):
                i = None if i == 0 else -i # If i == 0, it turns to None and tree[:None] will be the entire list. After, the list is iteratively trimmed.

                test = os.path.join(*tree[:i])
                if test in dirs_copied:
                    found = True
                    break
            if found: continue

            dirs_visited.add(root)

            # Add and update files
            self.add_update_files(files, root, files_visited)
                
            # Add directories    
            self.add_dirs(dirs, root, dirs_copied, dirs_visited)

        # Iterate over replica to remove files and dirs not visited on source
        for root, dirs, files in os.walk(self.replica_path):
            # Check if this root needs to be checked
            # (this is useful if the directories have a lot of files, there could be a condition to only run this snippet if wanted)
            found = False
            tree = root.split(os.sep)
            for i in range(len(tree)-1):
                i = None if i == 0 else -i # If i == 0, it turns to None and tree[:None] will be the entire list. After, the list is iteratively trimmed.

                test = os.path.join(*tree[:i])
                if test in dirs_copied:
                    found = True
                    break
            if found: continue

            # Remove files that have not been previously visited
            self.remove_files(files, root, files_visited)

            # Remove dirs that have not been previsouly visited
            self.remove_dirs(dirs, root, dirs_visited)
                
    def add_update_files(self, files: list, root: str, files_visited: set):
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(root.replace(self.source_path, self.replica_path), file)
            files_visited.add(replica_file)

            # If source_file is not in replica/file is different from replica's, copy-paste it.
            if not os.path.exists(replica_file):
                shutil.copyfile(source_file, replica_file)
                self.logger.log_file_creation(replica_file, datetime.now())
                continue

            # If file is different from replica's, replace it.
            if not filecmp.cmp(source_file, replica_file, shallow=False):
                shutil.copyfile(source_file, replica_file)
                self.logger.log_file_update(replica_file, datetime.now())

    def add_dirs(self, dirs: list, root: str, dirs_copied: set, dirs_visited: set):
        for dir in dirs:
            source_dir = os.path.join(root, dir)
            replica_dir = os.path.join(root.replace(self.source_path, self.replica_path), dir)
            dirs_visited.add(replica_dir)

            # If dir is not in replica, create it.
            if not os.path.exists(replica_dir):
                shutil.copytree(source_dir, replica_dir)
                dirs_copied.add(replica_dir)
                self.logger.log_dir_tree_creation(replica_dir, datetime.now())

    def remove_files(self, files: list, root: str, files_visited: list) -> None:
        for file in files:
            replica_file = os.path.join(root, file)

            # If the file has not been visited in source, remove it.
            if replica_file not in files_visited:
                os.remove(replica_file)
                self.logger.log_file_deletion(replica_file, datetime.now())

    def remove_dirs(self, dirs: list, root: str, dirs_visited: set) -> None:
        for dir in dirs:
            replica_dir = os.path.join(root, dir)

            # If the directory has not been visited in source, remove it.
            if replica_dir not in dirs_visited:
                shutil.rmtree(replica_dir)
                self.logger.log_dir_deletion(replica_dir, datetime.now())
            

class Logger:

    def __init__(self, logs_path):
        self.logs_path = logs_path

    def log_file_creation(self, new_file_path: str, timestamp: datetime) -> None: # TODO
        with open(self.logs_path, 'a') as file:
            file.write(str(timestamp) + f": Created file \"{new_file_path}\"\n")
        print("Created file: ", new_file_path)

    def log_file_deletion(self, deleted_file_path: str, timestamp: datetime) -> None: # TODO
        with open(self.logs_path, 'a') as file:
            file.write(str(timestamp) + f": Deleted file \"{deleted_file_path}\"\n")
        print("Deleted file: ", deleted_file_path)

    def log_file_update(self, updated_file_path: str, timestamp: datetime) -> None: # TODO
        with open(self.logs_path, 'a') as file:
            file.write(str(timestamp) + f": Updated file \"{updated_file_path}\"\n")
        print("Updated file: ", updated_file_path)

    def log_dir_tree_creation(self, new_dir_path: str, timestamp: datetime) -> None: # TODO
        with open(self.logs_path, 'a') as file:
            file.write(str(timestamp) + f": Copied directory \"{new_dir_path}\"\n")
        print("Copied tree directory: ", new_dir_path)

    def log_dir_deletion(self, deleted_dir_path: str, timestamp: datetime) -> None: # TODO
        with open(self.logs_path, 'a') as file:
            file.write(str(timestamp) + f": Deleted directory \"{deleted_dir_path}\"\n")
        print("Deleted directory: ", deleted_dir_path)

    def log_sync_complete(self) -> None:
        print("SYNC COMPLETE")




def maina():
    ct = datetime.now()
    print(type(ct))

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