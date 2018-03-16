#!/usr/bin/env python
import unittest
from DockerHelper import DockerTag

class DockerTagTestCase(unittest.TestCase):
    def test_init(self):
        vanilla_tag = DockerTag('4.4.3')
        self.assertEqual(vanilla_tag.version, '4.4.3')
        self.assertFalse(hasattr(vanilla_tag, 'prerelease'))
        self.assertFalse(hasattr(vanilla_tag, 'postrelease'))
        self.assertFalse(hasattr(vanilla_tag, 'extra'))

        postrelease_tag = DockerTag('4.4.3-2')
        self.assertEqual(postrelease_tag.version, '4.4.3')
        self.assertFalse(hasattr(postrelease_tag, 'prerelease'))
        self.assertEqual(postrelease_tag.postrelease, '2')
        self.assertEqual(postrelease_tag.extra, '2')

        prerelease_tag = DockerTag('4.5.0-alpha-1')
        self.assertEqual(prerelease_tag.version, '4.5.0')
        self.assertEqual(prerelease_tag.prerelease, 'alpha-1')
        self.assertFalse(hasattr(prerelease_tag, 'postrelease'))
        self.assertEqual(prerelease_tag.extra, 'alpha-1')

if __name__ == '__main__':
    unittest.main()
