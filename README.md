# Integration Testing Suite

--------------------------------

You have discovered an integration testing suite designed to be run
against Nova.  This test suite can be run against existing Nova
installations to verify the operation of the OpenStack API, currently
limited to API version 1.0 only.

## Usage

    % python ./run_tests.py --username=<username> --api-key=<API key> \
        --nova-url=<authentication URL> --glance-host=<glance host> \
        --glance-port=<glance port>

For ease of use with nova, you can source your novarc and then run the
above command with substitutions:

    % python ./run_tests.py --username=$NOVA_USERNAME --api-key=$NOVA_API_KEY \
        --nova-url=$NOVA_URL --glance-host=<glance host> \
        --glance-port=<glance port>

## Dependencies

DTest - Installed from PyPi

## Notes

Ideally, to run the suite, you will need to disable rate limiting on
the cluster.  Find the section of the etc/nova/api-paste.ini file
labeled "[pipeline:openstackapi10]" and remove "ratelimit" from the
"pipeline".  (Don't forget to add it back after running the tests.)

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

    --dot=<file>
          When using DTest for testing (by supplying --use_dtest), the
          test dependencies are output to <file> in a format suitable
          for feeding to GraphViz.  If not paired with --dry_run, the
          output will be color-coded to indicate tests that passed,
          failed, or were skipped.

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
