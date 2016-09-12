#!/bin/sh

echo -e "Please enter the Source mount point"
read s_mnt
echo -e "Please enter the Destination mount point"
read d_mnt
echo -e "Please enter the Tag name"
read in_tag

echo $s_mnt
echo $d_mnt
echo $in_tag

s_check=`df -h | grep -w "$s_mnt" | wc -l`
d_check=`df -h | grep -w "$d_mnt" | wc -l`

echo $s_check
echo $d_check

if [ "$s_check" == 1 ] ; then
	if [ "$d_check" == 1 ]; then
	  echo "Both the mount point present"
	  else
	  echo "$d_mnt mount point not present"	
	fi
  else
  echo "$s_mnt not present"
fi

#echo $s_check
#echo $d_check


: '
if [ $s_mnt in `df -h` ]; then
echo "Mount point $s_mnt present"
else
echo "Source mount point doesnot exists"
fi


echo "$1"
echo "$2"
option="$1"
case $option in 
	-f) FILE="$2"
	echo "Filename is $FILE"
	;;
	-d) DIR="$2"
	

esac



option="${1}" 
case ${option} in 
   -f) FILE="${2}" 
      echo "File name is $FILE"
      ;; 
   -d) DIR="${2}" 
      echo "Dir name is $DIR"
      ;; 
   *)  
      echo "`basename ${0}`:usage: [-f file] | [-d directory]" 
      exit 1 # Command to come out of the program with status 1
      ;; 
esac 
'

