#!/usr/bin/env bash
LOCALES=$*

PYTHON_FILES=" "
for f in $(find . -name "*.py" -o -name "*.ui"); do
	PYTHON_FILES+=$f
	PYTHON_FILES+=" "
done

for LOCALE in ${LOCALES}
do
  TRANSLATION_FILE="i18n/$LOCALE.ts"
  pylupdate5 -noobsolete ${PYTHON_FILES} -ts ${TRANSLATION_FILE}
done


