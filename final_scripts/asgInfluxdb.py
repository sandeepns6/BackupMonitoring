#!/usr/bin/python
import os,sys, argparse, datetime, sqlite3                   # Importing the required modules
from influxdb import InfluxDBClient     # Importing the influxdb client module
DB_NAME = 'agsbackup'                   # Database name
DB_SERVER = 'localhost'                 # Server Name
DB_PORT = '8086' 			# INFLUX DB PORT
DB_USER = 'icingauser' 			# INFLUX DB USERNAME
DB_PASSWD = 'icinga@123'		# INFLUX DB PASSWORD
DB_MEASUREMENT = 'drive_info'		# MEASUREMENT
client = InfluxDBClient( DB_SERVER, DB_PORT, DB_USER, DB_PASSWD, DB_NAME ) # Influx DB connection
MYDICT =  {}
SQLITE_DB = 'arista.db'                 # SQLITE3 DB
now = datetime.datetime.now()
pointsList = []

# CREATING THE JSON AND PUSHING THE DATA POINTS
def createPoint( MYDICT ):
   jsonCreate = {
                "measurement": DB_MEASUREMENT,
                "tags": {
                    "target": MYDICT['target']
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
    start_dt = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S') 
    end_dt = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')
    diff = (end_dt - start_dt)
    return (diff.days * 24 * 60 * 60) + (diff.seconds / 60)

# FUNCTION THAT CAN BE CALLED FROM DIFFERENT FILE TO PUSH THE DATA POINTS
def addBackupPoint(target, files, size, startTime, endTime):
  MYDICT['duration'] = calTimeDifference(startTime,endTime)
  MYDICT['target'] = target
  MYDICT['files'] = files
  MYDICT['nmbytes'] = size
  MYDICT['startTime'] = (datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')).strftime("%Y-%m-%dT%H:%M:%SZ")
  pointsList.append(createPoint(MYDICT))
  client.write_points( pointsList )

# Function for passing the correct option and get the option values
def getArgs():
    parser = argparse.ArgumentParser(
        description='Script for taking the required data and pushing the influxdb')
    parser.add_argument(
        '-t', '--target', type=str, help='End target')
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
     MYDICT['target'] = row[1]
     MYDICT['files'] = row[2]
     MYDICT['nmbytes'] = row[3]
     MYDICT['duration'] = calTimeDifference( row[4], row[5] )
     MYDICT['startTime'] = (datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')).strftime("%Y-%m-%dT%H:%M:%SZ")
     jsonCreate = createPoint(MYDICT) 
     pointsList.append(jsonCreate)

# Checking whether the lenght of argv
if len(sys.argv) > 1:
    cmdLineArgs = getArgs()
    MYDICT['target'] = cmdLineArgs.target
    MYDICT['files'] = cmdLineArgs.files
    MYDICT['nmbytes'] = cmdLineArgs.nmbytes
    MYDICT['duration'] = cmdLineArgs.duration
    MYDICT['startTime'] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    pointsList.append( createPoint( MYDICT ) )
else:
    sqlWriteInfluxDb()

# CALLING INFLUXDB API TO PUSH THE DATAPOINTS
client.write_points( pointsList )

# UPDATING THE SQLITE RECORDS WITH UPLOADED COLUMN AS 1
conn.execute("update drive_info set uploaded=1 where uploaded=0;")
conn.commit()
