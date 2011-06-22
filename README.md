# Integration Testing Suite

--------------------------------

You have discovered *backfire*, an integration testing suite designed
to be run against Nova.  Backfire can be run against existing Nova
installations to verify the operation of the OpenStack API (currently
limited to API version 1.0 testing, only).

## Usage

    % python ./run_tests.py --username=<username> --api-key=<API key> \
        --nova-url=<authentication URL> --glance-host=<glance host> \
        --glance-port=<glance port>

For ease of use with nova, you can source your novarc and then run
this command:

    % python ./run_tests.py

(All the options in the first command either acquire their defaults
from the environment variables set in novarc or have reasonable
defaults.  To see the defaults, use the --help option.)

## Dependencies

DTest - Installed from PyPi
python-novaclient - Installed from PyPi

## Notes

Ideally, to run the suite, you will need to disable rate limiting on
the nova cluster.  Find the section of the `etc/nova/api-paste.ini`
file labeled "[pipeline:openstackapi10]" and remove "ratelimit" from
the "pipeline".  (Don't forget to add it back after running the
tests.)

You will also need the following information: a username with
administrative privileges; the API key for that user; the
authentication URL for the Nova installation; and the host and port
number of the glance server.

## Options and Arguments

The following additional flags are also recognized:

    --timeout=<timeout>
          Some tests can take a long time to run.  To keep them from
          running forever, a timeout defaulting to 5 minutes is
          applied.  This flag allows the timeout to be adjusted to any
          desired value.  It is an integer specifying the timeout in
          minutes.

    -d <dir>, --directory=<dir>
          Use the tests in <dir>.  By default, the tests in the
          current directory are used.

    -m <max>, --max-threads=<max>
          The maximum number of simultaneous threads is limited to
          <max>.  By default, there is no limit.

    -s <rule>, --skip=<rule>
          Specifies a rule to control which tests are skipped.  For
          instance, "--skip=longtest" will cause marked long-running
          tests to be skipped

    --no-skip
          Specifies that tests which are marked to be skipped will not
          actually be skipped.

    -n, --dry-run
          Prints out a list of the tests discovered, but does not run
          them.

    -D, --debug
          Disables output capturing, causing output to be written out
          immediately.

    --dot=<file> The test dependencies will be output to <file> in a
          format suitable for feeding to GraphViz.  If not paired with
          --dry-run, the output will be color-coded to indicate tests
          that passed, failed, or were skipped.

    --test-image=<image>
          Specifies an image to be used when testing the image portion
          of the API.  By default, uses test_image.img in the current
          directory.

    --flavor=<flavorId>
          Specifies the ID of the flavor to use for building
          instances.  By default, this is 1, which on default Nova
          installations is the "m1.tiny" flavor.

    --image=<imageId>
          Specifies the ID of the image to use for building instances.
          By default, this is 3.

## Creating New Tests

Creating new tests for backfire are fairly easy.  First, determine if
your test belongs in an existing file; for instance, if the test
checks to see if an instance-bashing new action works, you may want to
put it in test_server_actions.py.  If you need to create a new file
for your test, name it "test_<something>.py", so DTest can find it.

If you created a new file, the next step will be to set up your test
class.  Backfire includes two test
classes--`base.BaseIntegrationTest`, which sets up self.os to be an
instance of novaclient.OpenStack(), or `test_servers.BaseServerTest`,
which additionally sets up and boots an instance.  If you're doing
destructive tests, such as testing whether an instance will shut down,
you'll probably need to stick with `base.BaseIntegrationTest` and
build the instance yourself.  Don't forget to tear it down when your
test is done!  Additionally, you should explicitly add a dependency on
`test_servers.ServerCreationTest.test_create_delete_server` on your
tests so your test is not run if the server creation/deletion test
fails.

Now we come to creating actual new tests.  Tests are methods with
names beginning with "test_" (just like the file names) contained
within subclasses of `base.BaseIntegrationTest` or
`test_servers.BaseServerTest`.  They take no arguments, but may be
decorated with various DTest decorators, such as @dtest.attr(),
@dtest.depends(), or particularly @dtest.timed().  (If you use
@dtest.timed(), you should take the value of `base.FLAGS.timeout` and
multiply it by 60, and use some multiple of that for your timeout;
this allows timeouts to be increased or decreased from the command
line.)

Within tests, use the Python `assert` statement or the `dtest.util`
assertion helpers to perform your tests.  You may also be interested
in the `base.BaseIntegrationTest.randName()` method for generating
random names for test data, or the `utils.StatusTracker` class for
tracking an object's state transitions and ensuring they end up in the
correct state.

Once you've created the test, you're set--the base DTest framework
will automatically pick up new tests that conform to the naming and
inheritance rules we've sketched out here.  You can confirm that the
test was picked up by running `run_tests.py` with the --dry-run option
and confirming that the test is listed.

For more information about the classes and functions mentioned here,
check out their doc strings.
