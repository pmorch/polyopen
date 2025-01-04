import unittest
from pathlib import Path

from polyopen import mounts

# Incomplete version of my current local mounts
dummy_mount_output = """
sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
udev /dev devtmpfs rw,nosuid,relatime,size=16233640k,nr_inodes=4058410,mode=755,inode64 0 0
devpts /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 0 0
tmpfs /run tmpfs rw,nosuid,nodev,noexec,relatime,size=3256728k,mode=755,inode64 0 0
home:/home/peter /home/pmorch/mnt/tmp fuse.sshfs rw,nosuid,nodev,relatime,user_id=1234,group_id=2435 0 0
kosh:/peterp /home/pmorch/mnt/peterp nfs4 rw,relatime,vers=4.2,rsize=1048576,wsize=1048576,namlen=255,soft,proto=tcp,timeo=100,retrans=5,sec=sys,clientaddr=192.168.1.124,local_lock=none,addr=192.168.1.2 0 0
"""


class TestSum(unittest.TestCase):

    def test_list_remote_mounts(self):
        got = mounts.list_remote_mounts(dummy_mount_output)
        expected = [
            (
                "home",
                Path("/home/peter"),
                Path("/home/pmorch/mnt/tmp"),
            )
        ]
        self.assertEqual(got, expected)

    def test_local_path_happy(self):
        got = mounts.find_local_path_from_remote(
            "/home/peter/foobar",
            ["home", "otherhost"],
            mounts=dummy_mount_output,
            warn_if_missing=False,
        )
        self.assertEqual(got, Path("/home/pmorch/mnt/tmp/foobar"))

    def test_local_path_no_matching_mount(self):
        got = mounts.find_local_path_from_remote(
            "/home/peter/foobar",
            ["somehost", "otherhost"],
            mounts=dummy_mount_output,
            warn_if_missing=False,
        )
        self.assertEqual(got, None)

    def test_local_path_outside_mount_point(self):
        got = mounts.find_local_path_from_remote(
            "/some/path/foobar",
            ["home", "otherhost"],
            mounts=dummy_mount_output,
            warn_if_missing=False,
        )
        self.assertEqual(got, None)


if __name__ == "__main__":
    unittest.main()
