import re
import warnings
from pathlib import Path


def read_raw_mounts():
    mounts = Path("/proc/mounts")
    if not mounts.exists():
        raise RuntimeError(f"{mounts} doesn't exist")
    return mounts.read_text()


def list_remote_mounts(mounts):
    lines = mounts.strip().split("\n")

    # https://stackoverflow.com/questions/18122123
    # Format of /proc/mounts
    # The 1st column specifies the device that is mounted.
    # The 2nd column reveals the mount point.
    # The 3rd column tells the file-system type.

    remote_mounts = []
    for line in lines:
        parts = line.split()
        device, mount_point, type, *_ = parts
        if type != "fuse.sshfs" and not re.match(r"^nfs\d$", type):
            continue
        device_parts = device.split(":")
        if len(device_parts) != 2:
            raise RuntimeError("Expected exactly two device parts")
        host, _hostpath = device_parts
        hostpath = Path(_hostpath)
        if not hostpath.is_absolute():
            continue
        remote_mounts.append(
            (
                host,
                hostpath,
                Path(mount_point),
            )
        )
    return remote_mounts


def find_local_path_from_remote(
    remote_path: str,
    publisher_hostnames: list[str],
    # Provide mounts to test
    mounts: str = None,
    warn_if_missing: bool = True,
) -> Path | None:
    remote_path_path = Path(remote_path)
    if mounts is None:
        mounts = read_raw_mounts()
    remote_mounts = list_remote_mounts(mounts)
    for publisher_hostname in publisher_hostnames:
        for remote_mount in remote_mounts:
            host, hostpath, mount_point = remote_mount
            if publisher_hostname != host:
                continue
            try:
                relative = remote_path_path.relative_to(hostpath)
            except Exception:
                continue
            local_path = mount_point / relative
            if warn_if_missing and not local_path.exists():
                warnings.warn(f"{local_path} doesn't exist", RuntimeWarning)
            return local_path
    return None


if __name__ == "__main__":
    print(find_local_path_from_remote("/home/peter/work", ["home"]))
