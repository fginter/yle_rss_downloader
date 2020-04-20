#!/usr/bin/env python3

import sys
import re
import gzip

from bs4 import BeautifulSoup


# Elements with matching IDs will be deleted from the HTML
DELETE_BY_ID = [
    'sidebar',
    'bottom',
    'fullWidthBottom',
]

# Elements with matching classes will be deleted from the HTML
DELETE_BY_CLASS = [
    'ad-container',
    'component-ad-leiki',
    'overlay',
    'related-links',
    'news-feed',
    'feednav',
    'promo-copy',
    'article-info',
    'article-author',
    'article-tags',
    'img-container',
    'promo-tile-stripe'
]

# Matching tags will have a newline appended
APPEND_NEWLINE = [
    'p',
    'br',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
]

def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('--encoding', default='utf-8')
    ap.add_argument('--html', default=False, action='store_true')
    ap.add_argument('file', nargs='+')
    return ap


def normalize_space(text):
    text = text.strip()
    text = '\n'.join(l for l in text.split('\n') if l and not l.isspace())
    text = re.sub(r'  +', r' ', text)
    text = re.sub(r'\n\n+', r'\n', text)
    return text


def extract_stream(f, fn, options):
    html = f.read()
    soup = BeautifulSoup(html)

    # delete script and style tag content
    for t in soup(['script', 'style']):
        t.decompose()

    # delete content of elements with selected ids
    for t in soup.find_all(id=DELETE_BY_ID):
        t.decompose()
        
    # delete content of elements with selected classes
    for t in soup.find_all(class_=DELETE_BY_CLASS):
        t.decompose()

    # add newlines after appropriate elements
    for t in soup.find_all(APPEND_NEWLINE):
        t.append('\n')
    
    texts = []
    for t in soup.find_all('div', { 'id': 'page-main' }):
        if options.html:
            texts.append(t.prettify())
        else:
            texts.append(t.get_text())
    text = '\n'.join(texts)

    if not options.html:
        text = normalize_space(text)
    print(text)


def extract(fn, options):
    if fn.endswith('.gz'):
        with gzip.open(fn, 'rt', encoding=options.encoding) as f:
            extract_stream(f, fn, options)
    else:
        with open(fn) as f:
            extract_stream(f, fn, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        extract(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
