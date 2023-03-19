#!/usr/bin/python3

import argparse
import re
from pathlib import Path
from shutil import copyfile
from tempfile import NamedTemporaryFile

CLIENT_SEARCH_PATTERN = r'^client[0-9]+'
NETWORKS_SEARCH_PATTERN = 'networks'

# assuming that the input file already contains a client service named "client1"
# and assuming that it defines the anchor "client_config"
# then this function generates n clients (starting from <base_clients> onwards)
def gen_n_client_templates(n: int, base_clients: int):
    assert isinstance(n, int), 'n must be a positive integer'
    if n <= 0:
        raise ValueError(f'The number of client templates to generate must be positive, not {n}')
    return [
        f'  client{i}:\n'
        f'    <<: *client_config\n'
        f'    container_name: client{i}\n'
        f'    environment:\n'
        f'      - CLI_ID={i}\n\n'
        for i in range(base_clients + 1, n+base_clients+1)]

# appends client configs inbetween already existing client configurations and the network section of the yaml base file
# it is expected of the file to contain at least one client configuration to replicate
# the function avoids reading the whole config file into memory by creating a temporary file and then copying its contents to the original
# effectively overriding the contents of the original file
def add_clients_to_file(n_clients: int, filepath: str):
    current_file_pos = 0
    file_client_configs = 0
    filepath = Path(filepath).resolve()
    # scoped open files (equivalent to c++ raii)
    with (
            filepath.open('r+') as compose_file, 
            NamedTemporaryFile(mode="w", dir=str(filepath.parent)) as destination_file
        ):
        client_pattern = re.compile(CLIENT_SEARCH_PATTERN)

        for line in compose_file:
            current_file_pos += len(line)
            if client_pattern.search(line.lstrip()):
                file_client_configs += 1
            # if the file contains the network section
            # we stop copying contents so as to write the new client configs at the services section 
            # before the network section
            elif line.startswith(NETWORKS_SEARCH_PATTERN):
                # set the position of the file to the line previous to the start of the network section
                compose_file.seek(current_file_pos - len(line))
                break
            destination_file.file.writelines(line)
        if file_client_configs == 0:
            raise ValueError("At least one client expected")

        # write the client configs into the temporary file
        destination_file.file.writelines(gen_n_client_templates(n=n_clients, base_clients=file_client_configs))
        for line in compose_file:
            destination_file.file.writelines(line)

        # flush the buffered contents into the file
        destination_file.flush()
        # override the file
        copyfile(destination_file.name, str(filepath))

def main(n_clients: str, filepath: str):
    try:
        n_clients = int(n_clients)
        add_clients_to_file(n_clients, filepath)
    except (OSError, ValueError) as e:
        print(e)
        return
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--n_clients",
                        required=True,
                        default=None,
                        help="Number of client configurations to generate")
    parser.add_argument("-f", "--filepath",
                        required=True,
                        default=None,
                        help="Path to docker compose file")
    args = parser.parse_args()
    main(**vars(args))