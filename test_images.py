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

from dtest import util as dtutil
from glance import client
import glance.common.exception
import novaclient

import base

FLAGS = base.FLAGS


class ImageTest(base.BaseIntegrationTest):
    """Test that the images portion of the API works as expected."""

    _image_id = None
    _image_name = None

    @classmethod
    def setUpClass(cls):
        """Set up image tests by adding a known image."""

        # Set up the _image_name
        cls._image_name = cls.randName(prefix="base-image")

        new_meta = cls.create_glance_image(file_name=FLAGS.test_image,
                                         image_name=cls._image_name)

        cls._image_id = new_meta['id']

    @classmethod
    def tearDownClass(cls):
        """Clean up left-over images."""

        # For safety, make sure we have an image identifier...
        if cls._image_id is None:
            return

        # Delete the image
        c = cls.get_glance_connection()
        c.delete_image(cls._image_id)

    def test_list(self):
        """Test that images can be listed."""

        # See if we can retrieve the list of images
        images = self.os.images.list()

        # Do we have a list?
        dtutil.assert_not_equal(len(images), 0)

        # Let's see if our test image is in the list
        foundimg = False
        for img in images:
            if img.id == self._image_id:
                dtutil.assert_equal(img.name, self._image_name)
                dtutil.assert_equal(img.status, 'ACTIVE')
                foundimg = True

        # Did we actually find the image we were looking for?
        dtutil.assert_true(foundimg)

    def test_get(self):
        """Test that we can get the details of a given image."""

        # Let's try to get our test image
        img = self.os.images.get(self._image_id)

        # Check that all the details match
        dtutil.assert_equal(img.id, self._image_id)
        dtutil.assert_equal(img.name, self._image_name)
        dtutil.assert_equal(img.status, 'ACTIVE')

    def test_get_nonexistent(self):
        """Test that a get request for a nonexistant id fails"""

        img_id = FLAGS.nonexistent_image
        # test via nova client
        dtutil.assert_raises(novaclient.exceptions.NotFound,
                             self.os.images.get, img_id)

        # test via glance client
        dtutil.assert_raises(glance.common.exception.NotFound,
                             self.glance_connection.get_image, img_id)

    def test_create_and_delete(self):
        """Test that an image can be created and deleted."""

        name = self.randName(prefix="create_delete_image_")

        # Create a new image
        new_meta = self.create_glance_image(file_name=FLAGS.test_image,
                                          image_name=name)

        # Verify it exists and the values are correct
        img = self.os.images.get(new_meta['id'])
        dtutil.assert_equal(img.id, new_meta['id'])
        dtutil.assert_equal(img.name, new_meta['name'])
        dtutil.assert_equal(img.status, 'ACTIVE')

        # Delete the image
        self.glance_connection.delete_image(new_meta['id'])

        # Verify it cannot be retrieved
        dtutil.assert_raises(novaclient.exceptions.NotFound,
                             self.os.images.get, new_meta['id'])

    def test_delete_nonexistent(self):
        """Test that a delete request for a nonexistant id fails"""

        img_id = FLAGS.nonexistent_image

        dtutil.assert_raises(glance.common.exception.NotFound,
                             self.glance_connection.delete_image, img_id)
