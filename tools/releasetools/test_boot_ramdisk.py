"""Regressions for boot reconstruction during release signing of SAR builds."""

import os
import struct
import tempfile
import unittest

import common


class BootRamdiskTest(unittest.TestCase):
  def build_image(self, info, partition="boot"):
    with tempfile.TemporaryDirectory() as root:
      boot = os.path.join(root, partition.upper())
      ramdisk = os.path.join(boot, "RAMDISK")
      os.makedirs(ramdisk)
      with open(os.path.join(boot, "kernel"), "wb") as output:
        output.write(b"test kernel")
      with open(os.path.join(ramdisk, "init"), "wb") as output:
        output.write(b"test first-stage init")
      image = common.GetBootableImage(partition + ".img", partition + ".img",
                                     root, partition.upper(), info)
      self.assertEqual(b"ANDROID!", image.data[:8])
      return struct.unpack_from("<I", image.data, 16)[0]

  def test_legacy_sar_stays_ramdiskless(self):
    self.assertEqual(0, self.build_image({"system_root_image": "true"}))

  def test_sar_first_stage_survives_reconstruction(self):
    self.assertGreater(self.build_image({"system_root_image": "true",
                                        "boot_ramdisk_with_system_root": "true"}), 0)

  def test_standard_boot_still_has_ramdisk(self):
    self.assertGreater(self.build_image({"system_root_image": "false"}), 0)

  def test_recovery_still_has_ramdisk(self):
    self.assertGreater(self.build_image({"system_root_image": "true"}, "recovery"), 0)


if __name__ == "__main__":
  unittest.main()
