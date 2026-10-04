import unittest
from unittest.mock import patch

from fenix_nightlight.backends.cosmic import CosmicBackend


class CosmicBackendTests(unittest.TestCase):
    def test_capabilities_are_discrete_and_privileged(self):
        backend = CosmicBackend("/usr/local/bin/cosmic-nightlight-helper")
        self.assertFalse(backend.capabilities.smooth_transitions)
        self.assertTrue(backend.capabilities.requires_privilege)
        self.assertTrue(backend.capabilities.may_flicker)

    @patch("fenix_nightlight.backends.cosmic.shutil.which")
    @patch("fenix_nightlight.backends.cosmic.os.geteuid", return_value=1000)
    def test_command_uses_pkexec_for_normal_user(self, _geteuid, which):
        which.side_effect = lambda name: "/usr/bin/pkexec" if name == "pkexec" else None
        backend = CosmicBackend("/usr/local/bin/cosmic-nightlight-helper")
        with patch.object(backend, "_resolved_helper", return_value="/usr/local/bin/cosmic-nightlight-helper"):
            command = backend._command("--temp", "4500", "--brightness", "1.000")
        self.assertEqual(
            command,
            [
                "/usr/bin/pkexec",
                "/usr/local/bin/cosmic-nightlight-helper",
                "--temp",
                "4500",
                "--brightness",
                "1.000",
            ],
        )


if __name__ == "__main__":
    unittest.main()
