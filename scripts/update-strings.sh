#!/usr/bin/env bash
LOCALES=$*

PYTHON_FILES=`ls *.{py,ui}`

for LOCALE in ${LOCALES}
do
  TRANSLATION_FILE="i18n/$LOCALE.ts"
  pylupdate5 -noobsolete ${PYTHON_FILES} -ts ${TRANSLATION_FILE}
done


