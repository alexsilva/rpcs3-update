import argparse
import os
import re
import subprocess
import sys
import tempfile
from urllib import urlretrieve
import shlex
import requests


class Rpcs3(object):
    """Auto updater"""
    site_url = 'https://rpcs3.net/download'

    artifacts_pattern_url = re.compile('(?P<download>https://ci\.appveyor\.com/api/buildjobs/.*?rpcs3-v.*?win64\.7z)')

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

        cmd = '{0.decompress_tool} x "{1:s}" -o"{2:s}" -y'.format(self, safe_archive_path, safe_decomp_path)
        cmd_args = shlex.split(cmd)

        print '=' * 5
        print cmd_args
        print '=' * 5

        subprocess.check_call(cmd_args, shell=False)

    def download(self):
        response = requests.get(self.site_url)

        assert response.status_code == 200, 'response site invalid ({0.status_code})!'.format(response)

        match = self.artifacts_pattern_url.search(response.text)

        assert match is not None, 'download url no match!'

        download_url = match.groupdict()['download']

        # Create directory if none exists
        if not os.path.isdir(self.decompress_path):
            os.makedirs(self.decompress_path)

        if not os.path.isdir(self.download_temp_path):
            os.makedirs(self.download_temp_path)

        last_version = None

        if os.path.isfile(self.download_version_path):
            with open(self.download_version_path, 'r') as fversion:
                last_version = fversion.read().strip('\n ')

        filename = os.path.basename(download_url)

        match = self.pattern.match(filename)

        assert match is not None, 'filename no match!'
        if match:
            version = match.groupdict()['version']

            # is new version (update)
            if last_version is None or version != last_version:
                filepath = os.path.join(self.download_temp_path, filename)

                # Download file
                print "Downloading {}...".format(download_url)
                urlretrieve(download_url, filepath)

                self.decompress(filepath)

                # history version
                with open(self.download_version_path, "w") as fversion:
                    fversion.write(version)


def main(*args):
    parser = argparse.ArgumentParser(description='Rpcs3 settings')
    parser.add_argument("--decompress-path", type=str, required=True)
    parser.add_argument("--decompress-tool", type=str, default='7z')

    args = parser.parse_args(args)

    rpcs3 = Rpcs3(args.decompress_path,
                  args.decompress_tool)

    rpcs3.download()


if __name__ == '__main__':
    main(*sys.argv[1:])
