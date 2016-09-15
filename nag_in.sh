#!/bin/bash

in_user_name="icingauser"
in_pwd="icinga@123"
in_db="arista_disks"
mysql_mnt="/content"
iscsi_mnt="/iscsi_mount"

mysql_size=`influx -username=$in_user_name -password=$in_pwd -execute="select * from drive_info" -database=$in_db -format=column | grep $mysql_mnt | awk '{print $NF}'| tail -n 1`

iscsi_size=`influx -username=$in_user_name -password=$in_pwd -execute="select * from drive_info" -database=$in_db -format=column | grep $iscsi_mnt | awk '{print $NF}'| tail -n 1`

echo $mysql_size
echo $iscsi_size

