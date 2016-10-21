import agsInfluxdb

#agsInfluxdb.sqlWriteInfluxDb()
agsInfluxdb.addBackupPoint(target='test1bp', files=200, size=265412, startTime='2016-10-08 12:17:01', endTime='2016-10-11 12:56:27')
