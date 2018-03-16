#!/usr/bin/env python
import unittest
from DockerHelper import DockerTag

class DockerTagTestCase(unittest.TestCase):
    def test_init(self):
        latest_tag = DockerTag('latest')
        self.assertEqual(latest_tag.orig_name, 'latest')
        self.assertFalse(hasattr(latest_tag, 'version'))
        self.assertFalse(hasattr(latest_tag, 'prerelease'))
        self.assertFalse(hasattr(latest_tag, 'postrelease'))
        self.assertFalse(hasattr(latest_tag, 'extra'))
        self.assertEqual(latest_tag.name, 'latest')

        vanilla_tag = DockerTag('4.4.3')
        self.assertEqual(vanilla_tag.orig_name, '4.4.3')
        self.assertEqual(vanilla_tag.version, '4.4.3')
        self.assertFalse(hasattr(vanilla_tag, 'prerelease'))
        self.assertFalse(hasattr(vanilla_tag, 'postrelease'))
        self.assertFalse(hasattr(vanilla_tag, 'extra'))
        self.assertEqual(vanilla_tag.name, '4.4.3')

        postrelease_tag = DockerTag('4.4.3-2')
        self.assertEqual(postrelease_tag.orig_name, '4.4.3-2')
        self.assertEqual(postrelease_tag.version, '4.4.3')
        self.assertFalse(hasattr(postrelease_tag, 'prerelease'))
        self.assertEqual(postrelease_tag.postrelease, 2)
        self.assertEqual(postrelease_tag.extra, '2')
        self.assertEqual(postrelease_tag.name, '4.4.3-2')

        prerelease_tag = DockerTag('4.5.0-alpha-1')
        self.assertEqual(prerelease_tag.orig_name, '4.5.0-alpha-1')
        self.assertEqual(prerelease_tag.version, '4.5.0')
        self.assertEqual(prerelease_tag.prerelease, 'alpha-1')
        self.assertFalse(hasattr(prerelease_tag, 'postrelease'))
        self.assertEqual(prerelease_tag.extra, 'alpha-1')
        self.assertEqual(prerelease_tag.name, '4.5.0-alpha-1')

if __name__ == '__main__':
    unittest.main()
