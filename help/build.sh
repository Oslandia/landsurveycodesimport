#!/bin/sh
gmake -e SPHINXOPTS="-D language='fr'" -e BUILDDIR="fr" html
gmake -e SPHINXOPTS="-D language='en'" -e BUILDDIR="en" html
