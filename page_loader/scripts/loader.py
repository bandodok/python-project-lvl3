import os
import argparse
from page_loader.page_loader import download


def main():
    parser = argparse.ArgumentParser(description='Download and save pages')
    parser.add_argument('download_path')
    parser.add_argument(
        "-o", "--output", default=os.getcwd(),
        help='output dir (default: "/app")')
    args = vars(parser.parse_args())
    download_path = args['download_path']
    output_path = args['output']
    return print(download(download_path, output_path))


if __name__ == '__main__':
    main()
