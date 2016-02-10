#!/bin/sh

function tmp_file () {
  TFILE="/tmp/$(basename $0).$$.keytab"
  echo $TFILE
}

TMP=$(tmp_file)
CMD=$(
{
  PRINC=$@
  echo "xst -k $TMP $PRINC"
})
sudo kadmin.local -q "$CMD" 2&> /dev/null
sudo base64 $TMP
sudo rm $TMP