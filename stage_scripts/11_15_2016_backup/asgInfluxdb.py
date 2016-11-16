#!/usr/bin/python
import os,sys, argparse, datetime, sqlite3                   # Importing the required modules
from influxdb import InfluxDBClient     # Importing the influxdb client module
#DB_NAME = 'ServerStats'                   # Database name
#DB_SERVER = 'serverstats'                 # Server Name
#SQLITE_DB = '/asg_backup/backup.db'       # SQLITE3 DB
#DB_MEASUREMENT = 'asg_backup'		# MEASUREMENT
DB_NAME = 'asgbackup'                   # Database name
DB_SERVER = '10.0.0.22'                 # Server Name
SQLITE_DB = 'arista.db'                 # SQLITE3 DB
DB_MEASUREMENT = 'drive_info'		# MEASUREMENT
client = InfluxDBClient( DB_SERVER, 8086, '', '', DB_NAME ) # Influx DB connection
MYDICT =  {}
now = datetime.datetime.now()
pointsList = []

# CREATING THE JSON AND PUSHING THE DATA POINTS
def createPoint( MYDICT ):
   jsonCreate = {
                "measurement": DB_MEASUREMENT,
                "tags": {
                    "server": MYDICT['server']
                },
                "time": MYDICT['startTime'],
                "fields": {
                    "files": MYDICT['files'],
                    "bytes": MYDICT['nmbytes'],
                    "duration": MYDICT['duration']
                }
        }
   return jsonCreate

# FUNCTION TO CALCULATE THE DURATION
def calTimeDifference( starttime, endtime ):
    start_dt = datetime.datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%SZ') 
    end_dt = datetime.datetime.strptime(endtime, '%Y-%m-%dT%H:%M:%SZ')
    diff = (end_dt - start_dt)
    return (diff.days * 24 * 60 * 60) + (diff.seconds / 60)

# FUNCTION THAT CAN BE CALLED FROM DIFFERENT FILE TO PUSH THE DATA POINTS
def addBackupPoint(server, files, size, startTime, endTime):
  MYDICT['duration'] = calTimeDifference(startTime,endTime)
  MYDICT['server'] = server
  MYDICT['files'] = files
  MYDICT['nmbytes'] = size
  MYDICT['startTime'] = (datetime.datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%SZ')).strftime("%Y-%m-%dT%H:00:00Z")
  pointsList.append(createPoint(MYDICT))
  print pointsList
#  client.write_points( pointsList )

# Function for passing the correct option and get the option values
def getArgs():
    parser = argparse.ArgumentParser(
        description='Script for taking the required data and pushing the influxdb')
    parser.add_argument(
        '-s', '--server', type=str, help='End server')
    parser.add_argument(
        '-f', '--files', type=int, help='Number of files')
    parser.add_argument(
        '-b', '--nmbytes', type=int, help='Number of bytes')
    parser.add_argument(
        '-d', '--duration', type=int, help='Duration')
 
    args = parser.parse_args()
    return args

# Function to push the data to Influx for UPLOADED record in SQLITE3 is 0
def sqlWriteInfluxDb():
  if os.path.isfile( SQLITE_DB ):			# Checking for the SQLITE DB
   conn = sqlite3.connect( SQLITE_DB )
  else:
   print "Error: Database %s not exists" % SQLITE_DB
   sys.exit( 1 )
  cursor = conn.execute("select * from drive_info where NOT uploaded;") # Fetch Sqlite data to cursor
  for row in cursor:
     MYDICT['server'] = row[1]
     MYDICT['files'] = row[2]
     MYDICT['nmbytes'] = row[3]
     MYDICT['duration'] = calTimeDifference( row[4], row[5] )
     MYDICT['startTime'] = (datetime.datetime.strptime(row[4], '%Y-%m-%dT%H:%M:%SZ')).strftime("%Y-%m-%dT%H:00:00Z")
     jsonCreate = createPoint(MYDICT) 
     pointsList.append(jsonCreate)
     # UPDATING THE SQLITE RECORDS WITH UPLOADED COLUMN AS 1
     conn.execute("update drive_info set uploaded=1 where uploaded=0;")
     conn.commit()

# Checking whether the lenght of argv
if len(sys.argv) > 1:
    cmdLineArgs = getArgs()
    MYDICT['server'] = cmdLineArgs.server
    MYDICT['files'] = float(cmdLineArgs.files)
    MYDICT['nmbytes'] = float(cmdLineArgs.nmbytes)
    MYDICT['duration'] = float(cmdLineArgs.duration)
    MYDICT['startTime'] = now.strftime("%Y-%m-%dT%H:00:00Z")
    pointsList.append( createPoint( MYDICT ) )
else:
    sqlWriteInfluxDb()

#print pointsList
 CALLING INFLUXDB API TO PUSH THE DATAPOINTS
client.write_points( pointsList )


