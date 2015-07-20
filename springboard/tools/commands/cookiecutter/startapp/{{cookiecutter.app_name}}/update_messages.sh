#!/bin/bash
find . -name '*.mo' -delete
package_name={{cookiecutter.app_name}}
mkdir -p ${package_name}/locale

python setup.py extract_messages -o ${package_name}/locale/${package_name}.pot

for locale in "$@"
do
    if [ ! -f "${package_name}/locale/${locale}/LC_MESSAGES/messages.po" ]; then
        python setup.py init_catalog -i ${package_name}/locale/${package_name}.pot -d ${package_name}/locale -l ${locale}
    fi
done

python setup.py update_catalog -i ${package_name}/locale/${package_name}.pot -d ${package_name}/locale
python setup.py compile_catalog -d ${package_name}/locale
