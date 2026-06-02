"""Package declared WASI testsuite inputs into a deterministic tarball."""

import argparse
import gzip
import io
import json
import stat
import tarfile
from pathlib import Path
from typing import Any


def _reset_metadata(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def _add_directory_entry(tar: tarfile.TarFile, arcname: str) -> None:
    info = tarfile.TarInfo(arcname.rstrip("/") + "/")
    info.type = tarfile.DIRTYPE
    info.mode = 0o755
    tar.addfile(_reset_metadata(info))


def _normalize_input(info: tarfile.TarInfo) -> tarfile.TarInfo:
    _reset_metadata(info)
    if info.isdir():
        info.mode = 0o755
    elif info.issym():
        info.mode = 0o777
    elif info.isfile():
        info.mode = stat.S_IMODE(info.mode)
    else:
        raise FileNotFoundError(info.name)
    return info


def _add_path(tar: tarfile.TarFile, src: Path, arcname: str) -> None:
    if not (src.is_symlink() or src.is_dir() or src.is_file()):
        raise FileNotFoundError(src)
    tar.add(src, arcname=arcname, recursive=True, filter=_normalize_input)


def _add_manifest(tar: tarfile.TarFile, manifest: dict[str, Any], arcname: str) -> None:
    data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    info = tarfile.TarInfo(arcname)
    info.size = len(data)
    info.mode = 0o644
    tar.addfile(_reset_metadata(info), io.BytesIO(data))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.spec, encoding="utf-8") as file:
        spec = json.load(file)

    root = spec["root"].rstrip("/")
    with open(args.output, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                _add_directory_entry(tar, root)
                entries = [
                    ("manifest", manifest["dst"], manifest)
                    for manifest in spec["manifests"]
                ] + [
                    ("item", item["dst"], item)
                    for item in spec["items"]
                ]
                for kind, dst, entry in sorted(entries, key=lambda item: item[1]):
                    if kind == "manifest":
                        _add_manifest(tar, entry["content"], f"{root}/{dst}")
                    else:
                        _add_path(tar, Path(entry["src"]), f"{root}/{dst}")


if __name__ == "__main__":
    main()
