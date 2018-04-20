import argparse
import os
import re
import subprocess
import argparse
import sys
import tempfile
from urllib import urlretrieve

import requests


class Rpcs3(object):
    # xml with list of files
    artifacts_url = 'https://ci.appveyor.com/api/buildjobs/98bl186yleb2w65e/artifacts'
    pattern = re.compile("^rpcs3-v(?P<version>.*?)_win64\.7z$", re.I)

    def __init__(self, decompress_path, decompress_tool='7z'):
        self.decompress_path = decompress_path
        #
        self.decompress_tool = decompress_tool

        # Downloaded version history
        self.download_version_path = os.path.join(self.decompress_path, "_download_version.txt")

        # Download the file to this folder
        self.download_temp_path = os.path.join(tempfile.gettempdir(), 'rpcs3-download')

    def decompress(self, archive_path):
        safe_decomp_path = self.decompress_path.strip('"\'')
        safe_archive_path = archive_path.strip('"\'')

        print safe_archive_path
        print safe_decomp_path

        cmd = '{0.decompress_tool} e "{1:s}" -o"{2:s}" -y'.format(self, safe_archive_path, safe_decomp_path)

        print cmd

        subprocess.check_call(cmd)

    def download(self):
        response = requests.get(self.artifacts_url)

        assert response.status_code == 200, 'invalid request!'

        # Create directory if none exists
        if not os.path.isdir(self.decompress_path):
            os.makedirs(self.decompress_path)

        if not os.path.isdir(self.download_temp_path):
            os.makedirs(self.download_temp_path)

        last_version = None

        if os.path.isfile(self.download_version_path):
            with open(self.download_version_path, 'r') as fversion:
                last_version = fversion.read().strip('\n ')

        for el in response.json():
            filename = el['fileName']
            match = self.pattern.match(filename)
            if match:
                version = match.groupdict()['version']

                # is new version (update)
                if last_version is None or version != last_version:
                    with open(self.download_version_path, "w") as fversion:
                        fversion.write(version)

                    filepath = os.path.join(self.download_temp_path, filename)
                    file_url = self.artifacts_url + "/" + filename

                    # Download file
                    print "Downloading {}...".format(file_url)
                    urlretrieve(file_url, filepath)

                    self.decompress(filepath)


def main(*args):
    parser = argparse.ArgumentParser(description='Rpcs3 settings')
    parser.add_argument("--decompress-path", type=str, required=True)
    parser.add_argument("--decompress-tool", type=str, default='7z')

    args = parser.parse_args(args)

    rpcs3 = Rpcs3(args.decompress_path,
                  args.decompress_tool)

    rpcs3.download()


if __name__ == '__main__':
    main(*sys.argv)
