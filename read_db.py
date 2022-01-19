from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import os
import sys
import pandas as pd
import sqlite3


IS_PYTHON3 = sys.version_info[0] >= 3

def blob_to_array(blob, dtype, shape=(-1,)):
    if IS_PYTHON3:
        return np.fromstring(blob, dtype=dtype).reshape(*shape)
    else:
        return np.frombuffer(blob, dtype=dtype).reshape(*shape)

def show_table_name(save_dir):
    conn = sqlite3.connect(os.path.join(save_dir, 'database.db'))
    sql = """SELECT name FROM sqlite_master WHERE TYPE='table'"""
    c = conn.cursor()
    table_list = []
    for t in c.execute(sql):
        # print(t)
        table_list.append(t[0])

    c.close()
    return table_list

def get_cameras_from_db(save_dir):
    table_list = show_table_name(save_dir)
    conn = sqlite3.connect(os.path.join(save_dir, 'database.db'))
    c = conn.cursor()
    sql = """SELECT * FROM 'cameras'"""
    c.execute(sql)
    fetched = c.fetchall()
    print(type(fetched))
    for ft in fetched:
        print(ft)
    conn.close()
    return fetched


def get_images_from_db(save_dir):
    conn = sqlite3.connect(os.path.join(save_dir, 'database.db'))
    c = conn.cursor()
    sql = """SELECT name FROM 'images'"""
    c.execute(sql)
    fetched = c.fetchall()
    print(type(fetched))
    for ft in fetched:
        print(ft)
    conn.close()
    return fetched

def get_geometries_from_db(save_dir):
    conn = sqlite3.connect(os.path.join(save_dir, 'database.db'))
    c = conn.cursor()
    sql = """SELECT pair_id FROM 'two_view_geometries'"""
    c.execute(sql)
    fetched = c.fetchall()
    print(type(fetched))
    for ft in fetched:
        print(ft)
    conn.close()
    return fetched

def get_cameras_from_bin(save_dir):
    file_name =os.path.join(save_dir, 'sparse', '0', 'cameras.bin')
    with open (file_name, 'rb') as f:
        f = f.read()
        decoded = blob_to_array(f, dtype=np.uint32)
        print(decoded)

def get_images_from_bin(save_dir):
    file_name =os.path.join(save_dir, 'sparse', '0', 'images.bin')
    with open (file_name, 'rb') as f:
        f = f.read()
        # print(f)
        decoded = blob_to_array(f, dtype=np.uint32)
        print(decoded)

def get_points3D_from_bin(save_dir):
    file_name =os.path.join(save_dir, 'sparse', '0', 'points3D.bin')
    with open (file_name, 'rb') as f:
        f = f.read()
        decoded = blob_to_array(f, dtype=np.uint32)
        print(decoded)



if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', action='store', type = str, default='./data',
                        help = 'root directory of the dataset')
    args = parser.parse_args()
    _ = show_table_name(args.base_dir)
    # get_cameras_from_db(args.base_dir)
    # get_images_from_db(args.base_dir)
    # get_geometries_from_db(args.base_dir)
    # get_cameras_from_bin(args.base_dir)
    get_images_from_bin(args.base_dir)
    # get_points3D_from_bin(args.base_dir)
    
    # connect(os.path.join('C:','User','ryo','m1','gerrard-hall','gerrard-hall')