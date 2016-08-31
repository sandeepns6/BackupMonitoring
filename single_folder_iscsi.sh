#copied

###################################################################
# Owner: Praveen Kumar G
# Date: 13-07-2016
# Purpose: To monitor 2 mount points and there subfolders, to verify where the DB backup is done correctly.
# Version: 1.0.0
####################################################################

#!/bin/bash

# Declaration
scsi_drive='/iscsi_mount'       # Destination location
mysql_drive='/content'      # Source folder that contains the MYSql backups
script_loc='/arista_scripts' # Scripts stored location
content_file="$script_loc/out.txt" # Content files
influx_file="$script_loc/influx.txt" # Influx DB data upload file


iscsi_target='iqn.2006-01.com.openfiler:tsn.3af9bd6b7b5b'
#iscsi_target='iqn.2008-09.com.example:server.target1' # ISCSI Iqn
db_name='arista_disks' # Influx DB name

# To check whether the ISCSI mount point is available
iscsi_stat=`iscsiadm -m session | grep $iscsi_target`
if [ "$iscsi_stat" ]
then
stat='Mounted'
echo "ISCSI drive mounted successfully"
else
stat='Unmounted'
echo "ISCSI drive not available"
fi

scsi_siz=`du -s $scsi_drive`
mysql_siz=`du -s $mysql_drive`

tmp_scsi=`echo $scsi_siz | awk '{print $1}'`
tmp_mysql=`echo $mysql_siz | awk '{print $1}'`

#echo $tmp_scsi
#echo $tmp_mysql

> $influx_file
echo "drive_info,host=`hostname`,iscsi_stat=$stat,disk_type=iscsi value=$tmp_scsi" >> $influx_file
echo "drive_info,host=`hostname`,iscsi_stat=$stat,disk_type=mysql value=$tmp_mysql" > $influx_file

curl -i -XPOST "http://localhost:8086/write?db=$db_name" -u icingauser:icinga@123 --data-binary @"$influx_file" > $content_file

out_put_stat=`cat $content_file | grep HTTP/1.1 | awk '{print $2}'`

if [[ "$out_put_stat" -ge 200 && "$out_put_stat" -le 300 ]]
then
echo "Data uploaded to Influxdb"
else
echo "Error while uploading the data to influxdb"
fi

