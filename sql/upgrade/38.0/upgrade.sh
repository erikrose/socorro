#!/bin/bash
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#please see README

set -e

CURDIR=$(dirname $0)
DBNAME=$1
: ${DBNAME:="breakpad"}
VERSION=38.0

#echo '*********************************************************'
#echo 'support functions'
#psql -f ${CURDIR}/support_functions.sql $DBNAME

echo '*********************************************************'
echo 'add uuid column to extensions'
echo 'bug 731598'
python add_uuid_to_extensions.py

#change version in DB
psql -c "SELECT update_socorro_db_version( '$VERSION' )" $DBNAME

echo "$VERSION upgrade done"

exit 0
