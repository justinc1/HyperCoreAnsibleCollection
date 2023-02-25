# -*- coding: utf-8 -*-
# Copyright: (c) 2022, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import vcr
import os


def main_with_vcr(main: callable, *args, **kwargs):
    record_mode = os.environ.get("PYVCR_RECORD_MODE")
    if not record_mode:
        return main(*args, **kwargs)
    if record_mode == 'none':
        # via vcr-stub-server
        return main(*args, **kwargs)

    my_vcr = vcr.VCR(
        serializer='yaml',
        # cassette_library_dir='/tmp',
        record_mode=record_mode,
        match_on=['uri', 'method'],
    )

    cassette = '/tmp/synopsis2.yaml'
    with my_vcr.use_cassette(cassette) as cass:
        return main(*args, **kwargs)


def vcr_enabled():
    record_mode = os.environ.get("PYVCR_RECORD_MODE")
    return bool(record_mode)
