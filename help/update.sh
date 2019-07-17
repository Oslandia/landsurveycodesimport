#!/usr/bin/env bash

GNUMAKE="make"
if [[ "${OSTYPE,,}" =~ bsd* ]] || [[ "$OSTYPE" =~ darwin* ]]; then
    GNUMAKE="gmake"
fi

${GNUMAKE} gettext

for LANG in $*
do
    sphinx-intl update --locale-dir source/locale -p build/gettext -l ${LANG}
done

