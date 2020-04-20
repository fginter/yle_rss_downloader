#!/usr/bin/env python3

import sys
import os
import re

from itertools import count
from logging import warning


NEWDOC_RE = re.compile(r'^###C: new article')
TIME_RE = re.compile(r'###C: timestamp = (\d+-\d+-\d+)T(\d+):(\d+):(\d+)')
URL_RE = re.compile(r'###C: url = https://yle.fi/.*/(\S+)(?:\?origin=rss|\.txt)')


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('outdir')
    return ap


def output_filename(date, hour, min_, sec, url_id, options):
    timestr = '{}-{}-{}-{}'.format(date, hour, min_, sec)
    fn = os.path.join(options.outdir, '{}--{}.txt'.format(timestr, url_id))
    if os.path.exists(fn):
        warning('output file {} exists'.format(fn))
    return fn
        
    
def convert(fn, options):
    out, url_id = None, None
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip()
            if l.startswith('###C:'):
                if NEWDOC_RE.match(l):
                    if out is not None:
                        out.close()
                        out, url_id = None, None
                elif URL_RE.match(l):
                    url_id = URL_RE.match(l).group(1)
                elif TIME_RE.match(l):
                    date, hour, min_, sec = TIME_RE.match(l).groups()
                    assert out is None
                    assert url_id is not None
                    ofn = output_filename(
                        date, hour, min_, sec, url_id, options)
                    out = open(ofn, 'wt')
            else:
                if l and not l.isspace():
                    print(l, file=out)
    if out is not None:
        out.close()
        out = None


def main(argv):
    args = argparser().parse_args(argv[1:])
    convert(args.file, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
