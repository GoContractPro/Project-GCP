#!/usr/bin/python

# Check total size afterwards: "du -b <filestore>" minux 4096 (size of dir '.')
# Check total size in DB: "select sum(file_size) from ir_attachment"
# UPDATE SQL: 
# update ir_attachment set db_datas = null
# --select count(*) from ir_attachment
# where store_fname is not null 
#

import xmlrpclib

username = 'admin' #the user
pwd = 'P@ssw0rd'      #the password of the user
dbname = 'npg6m'    #the database

# Get the uid
sock_common = xmlrpclib.ServerProxy ('http://localhost:8601/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://localhost:8601/xmlrpc/object')

FILESTORE = 2

def migrate_attachment(att_id):
    # 1. get data
    att = sock.execute(dbname, uid, pwd, 'ir.attachment', 'read', att_id, ['datas','parent_id'])

    dir_id = att['parent_id'][0]
    data = att['datas']

    # 2. Save old storage_id
    dir = sock.execute(dbname, uid, pwd, 'document.directory', 'read', dir_id, ['storage_id'])
    old_storage_id = dir['storage_id'][0]

    if old_storage_id == FILESTORE:
        print "skipping"
        return

    # Set storage to "FileStore"
    sock.execute(dbname, uid, pwd, 'document.directory', 'write', [dir_id], {'storage_id': FILESTORE})

    # Re-Write attachment
    a = sock.execute(dbname, uid, pwd, 'ir.attachment', 'write', [att_id], {'datas': data})

    # Reset storage to "Database"
    sock.execute(dbname, uid, pwd, 'document.directory', 'write', [dir_id], {'storage_id': old_storage_id})


# SELECT attachemnts:
att_ids = sock.execute(dbname, uid, pwd, 'ir.attachment', 'search', [('parent_id','=',1),('store_fname','=',False)])

cnt = len(att_ids)
i = 0
for id in att_ids:
    att = sock.execute(dbname, uid, pwd, 'ir.attachment', 'read', id, ['datas','parent_id'])

    migrate_attachment(id)
    print 'Migrated ID %d (attachment %d of %d)' % (id,i,cnt)
    i = i + 1
#    if i > 10:
#        break

print "done ..."
