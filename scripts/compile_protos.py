import os

import grpc_tools.protoc


def find_proto_files():
    proto_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "../proto"))

    return [
        os.path.join(proto_dir, filename)
        for filename in os.listdir(proto_dir)
        if filename.endswith(".proto")
    ]


def get_output_dir():
    return os.path.join(os.path.dirname(__file__), "../src/doxa_competition", "proto")


def get_root_path():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def main():
    proto_files = find_proto_files()
    output_dir = get_output_dir()

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    root = get_root_path()
    args = [
        "protoc",
        f"-I{root}",
        f"--python_betterproto_out={output_dir}",
    ] + proto_files
    grpc_tools.protoc.main(args)

    print("Success!")


if __name__ == "__main__":
    main()
