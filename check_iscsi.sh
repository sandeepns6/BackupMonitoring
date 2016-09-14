###################################################################
# Owner: Praveen Kumar G
# Date: 13-07-2016
# Purpose: To monitor 2 mount points and there subfolders, to verify where the DB backup is done correctly.
# Last Modified: 15-09-2016
# Version: 1.0.1
####################################################################

#!/bin/sh

# Taking the inputs from the users
echo -e "Please enter the Source mount point"; read s_mnt
echo -e "Please enter the Destination mount point" ; read d_mnt
echo -e 'Please enter the Tag name ex: iscsi'; read in_tag

# Variable Declaration
#script_loc='/arista_scripts/final_scripts_14_09_'
script_loc='/arista_scripts'                                   # Scripts stored location
content_file="$script_loc/out.txt";touch $content_file          # Content files
influx_file="$script_loc/influx.txt"                            # Influx DB data upload file
iscsi_target='iqn.2006-01.com.openfiler:tsn.3af9bd6b7b5b'       # Target IQN
db_name='arista_disks'                                          # Database name
s_check=`df -h | grep -w "$s_mnt" | wc -l`                      # Checking for the source drive
d_check=`df -h | grep -w "$d_mnt" | wc -l`                      # Checking for the Destination drive.
stat=""

# Declaration of function To check whether the ISCSI mount point is available
iscsi_stat=`iscsiadm -m session | grep $iscsi_target`
check_mounted_iscsi() {
if [ "$iscsi_stat" ]
then
  echo "ISCSI target Available"
  stat='Mounted'
  return 1
  else
  echo "ISCSI target not available"
  stat='Unmounted'
  return 0
fi
}

# Declaration of function to check whether both the mount points are present
check_iscsi() {
if [ "$s_check" == 1 ] ; then
        if [ "$d_check" == 1 ]; then
          echo -e "Both the mount point present\nPushing the data to influxdb....."
          return 1
          else
          echo "$d_mnt mount point not present"
          return 0
        fi
else
 echo "$s_mnt mount point not present"
 return 0
fi
}

# Declaration of function to push the data to influx db
push_check_data(){
> $content_file
curl -i -XPOST "http://localhost:8086/write?db=$db_name" -u icingauser:icinga@123 --data-binary @"$influx_file" > $content_file
out_put_stat=`cat $content_file | grep HTTP/1.1 | awk '{print $2}'`
if [[ "$out_put_stat" -ge 200 && "$out_put_stat" -le 300 ]];then
 echo "Data uploaded to Influxdb"
else
 echo "Error while uploading the data to influxdb"
fi
}

# Delaration of Function to check the size and push the data to influx db
check_data_db() {
scsi_siz=`du -s $s_mnt`                         # Getting the size of the Source folder
mysql_siz=`du -s $d_mnt`                        # Getting the size of the Destination folder
tmp_scsi=`echo $scsi_siz | awk '{print $1}'`
tmp_mysql=`echo $mysql_siz | awk '{print $1}'`

> $influx_file
echo "drive_info,iscsi_stat=$stat,disk_type=mysql,mount_point=$s_mnt value=$tmp_scsi" >> $influx_file
echo "drive_info,iscsi_stat=$stat,disk_type=iscsi,mount_point=$d_mnt value=$tmp_mysql" >> $influx_file
push_check_data $db_name $content_file
return 1
}

check_mounted_iscsi $iscsi_stat; mount_stat=$?                  # Calling the function with parameter
if [ "$mount_stat" == 1 ]; then
  check_iscsi $s_check $d_check
  iscsi_mount_point_status=$?
else
  exit 1
fi

#echo $iscsi_mount_point_status

if [ "$iscsi_mount_point_status" == 1 ]; then
 check_data_db $s_mnt $d_mnt;upload_stat=$?
else
 exit 1
fi
