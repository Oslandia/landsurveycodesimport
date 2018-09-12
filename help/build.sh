#!/usr/bin/env bash

GNUMAKE="make"
if [[ "${OSTYPE,,}" =~ bsd* ]] || [[ "$OSTYPE" =~ darwin* ]]; then
    GNUMAKE="gmake"
fi

for LANG in $*
do
    ${GNUMAKE} -e SPHINXOPTS="-D language='${LANG}'" -e BUILDDIR="html/${LANG}" html
done

