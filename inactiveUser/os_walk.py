# Copyright (c) 2017 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import os

userList = ['dsilla-ext', 'gayathri-ext']
p4confPath = []
for user in userList:
   path = '/home/' + user
   for dirpath, subdirs, files in os.walk(path):
      for x in files:
         if x == 'p4conf':
            p4confPath.append(dirpath)
            print dirpath

