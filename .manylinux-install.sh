#!/usr/bin/env bash

set -e -x

# Running inside docker
# Set a cache directory for pip. This was
# mounted to be the same as it is outside docker so it
# can be persisted.
export XDG_CACHE_HOME="/cache"
# XXX: This works for macOS, where everything bind-mounted
# is seen as owned by root in the container. But when the host is Linux
# the actual UIDs come through to the container, triggering
# pip to disable the cache when it detects that the owner doesn't match.
# The below is an attempt to fix that, taken from bcrypt. It seems to work on
# Github Actions.
if [ -n "$GITHUB_ACTIONS" ]; then
    echo Adjusting pip cache permissions
    mkdir -p $XDG_CACHE_HOME/pip
    chown -R $(whoami) $XDG_CACHE_HOME
fi
ls -ld /cache
ls -ld /cache/pip

# Compile wheels
cd /io/
for PYBIN in /opt/python/*/bin; do
    if [[ "${PYBIN}" == *"cp27"* ]] || \
       [[ "${PYBIN}" == *"cp35"* ]] || \
       [[ "${PYBIN}" == *"cp36"* ]] || \
       [[ "${PYBIN}" == *"cp37"* ]] || \
       [[ "${PYBIN}" == *"cp38"* ]] || \
       [[ "${PYBIN}" == *"cp39"* ]]; then
        "${PYBIN}/pip" install persistent wheel setuptools
        "${PYBIN}/python" setup.py bdist_wheel
        ls dist
        if [ `uname -m` == 'aarch64' ]; then
            # Running the test suite takes forever in
            # emulation; an early run (using tox, which is also slow)
            # took over an hour to build and then run the 2.7 tests and move on
            # to the 3.5 tests. We still want to run tests, though!
            # We don't want to distribute wheels for a platform that's
            # completely untested. Consequently, we limit it to running
            # in just one interpreter, the last one on the list (which in principle
            # should be the fastest), and we don't install the ZODB extra.
            if [[ "${PYBIN}" == *"cp39"* ]]; then
               "${PYBIN}/pip" install .[test]
               "${PYBIN}/python" -m unittest discover -s BTrees -t .
            fi
        fi
        rm -rf /io/build /io/*.egg-info
    fi
done

# Bundle external shared libraries into the wheels
for whl in dist/BTrees*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done
