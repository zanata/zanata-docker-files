#!/usr/bin/env python
import unittest
from DockerHelper import DockerImage

class DockerImageTestCase(unittest.TestCase):
    def test_init(self):
        latest_image = DockerImage('zanata', 'server', 'latest')
        self.assertEqual(latest_image.tag_param, 'latest')
        self.assertFalse(hasattr(latest_image, 'version'))
        self.assertFalse(hasattr(latest_image, 'prerelease'))
        self.assertFalse(hasattr(latest_image, 'postrelease'))
        self.assertEqual(latest_image.final_tag, 'latest')
        self.assertEqual(latest_image.dockerfile_name, 'zanata-server/Dockerfile')

        vanilla_image = DockerImage('zanata', 'centos-repo-builder', '4.4.3')
        self.assertEqual(vanilla_image.tag_param, '4.4.3')
        self.assertEqual(vanilla_image.version, '4.4.3')
        self.assertFalse(hasattr(vanilla_image, 'prerelease'))
        self.assertFalse(hasattr(vanilla_image, 'postrelease'))
        self.assertEqual(vanilla_image.final_tag, '4.4.3')
        self.assertEqual(vanilla_image.dockerfile_name, 'centos-repo-builder/Dockerfile')

        postrelease_image = DockerImage('zanata', 'fedora-package', '4.4.3-2')
        self.assertEqual(postrelease_image.tag_param, '4.4.3-2')
        self.assertEqual(postrelease_image.version, '4.4.3')
        self.assertFalse(hasattr(postrelease_image, 'prerelease'))
        self.assertEqual(postrelease_image.postrelease, 2)
        self.assertEqual(postrelease_image.final_tag, '4.4.3-2')
        self.assertEqual(postrelease_image.dockerfile_name, 'fedora-package/Dockerfile')

        prerelease_image = DockerImage('zanata', 'server', '4.5.0-alpha-1')
        self.assertEqual(prerelease_image.tag_param, '4.5.0-alpha-1')
        self.assertEqual(prerelease_image.version, '4.5.0')
        self.assertEqual(prerelease_image.prerelease, 'alpha-1')
        self.assertFalse(hasattr(prerelease_image, 'postrelease'))
        self.assertEqual(prerelease_image.final_tag, '4.5.0-alpha-1')
        self.assertEqual(prerelease_image.dockerfile_name, 'zanata-server/Dockerfile')

if __name__ == '__main__':
    unittest.main()
