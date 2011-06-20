# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from glance import client

import adaptor
import base
import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('test_image', 'test_image.img',
                    'Image to use for basic image tests')


class ImageTest(base.BaseIntegrationTest):
    """Test that the images portion of the API works as expected."""

    _image_id = None
    _image_name = None

    @classmethod
    def setUpClass(cls):
        """Set up image tests by adding a known image."""

        # Set up the _image_name
        cls._image_name = cls.randName()

        # Let's open the test image
        with open(FLAGS.test_image, 'rb') as img:
            # Get a glance connection
            c = client.Client(FLAGS.glance_host, FLAGS.glance_port)

            # Set up metadata for the image
            meta = {
                'name': cls._image_name,
                'type': 'machine',
                'is_public': True
                }

            # Upload the image
            new_meta = c.add_image(meta, img)

            # Save the identifier
            cls._image_id = new_meta['id']

    @classmethod
    def tearDownClass(cls):
        """Clean up left-over images."""

        # For safety, make sure we have an image identifier...
        if cls._image_id is None:
            return

        # Get a glance connection
        c = client.Client(FLAGS.glance_host, FLAGS.glance_port)

        # Delete the image
        c.delete_image(cls._image_id)

    def test_list(self):
        """Test that images can be listed."""

        # See if we can retrieve the list of images
        images = self.os.images.list()

        # Do we have a list?
        adaptor.assert_not_equal(len(images), 0)

        # Let's see if our test image is in the list
        foundimg = False
        for img in images:
            if img.id == self._image_id:
                adaptor.assert_equal(img.name, self._image_name)
                adaptor.assert_equal(img.status, 'ACTIVE')
                foundimg = True

        # Did we actually find the image we were looking for?
        adaptor.assert_true(foundimg)

    def test_get(self):
        """Test that we can get the details of a given image."""

        # Let's try to get our test image
        img = self.os.images.get(self._image_id)

        # Check that all the details match
        adaptor.assert_equal(img.id, self._image_id)
        adaptor.assert_equal(img.name, self._image_name)
        adaptor.assert_equal(img.status, 'ACTIVE')
