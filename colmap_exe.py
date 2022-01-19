from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import subprocess

class ColmapCommands():
    def __init__(self, basedir, match_type):
        self.basedir = basedir
        self.match_type = match_type

        self.feature_extractor_args = [
            'colmap', 'feature_extractor', 
                '--database_path',  os.path.join(self.basedir, 'database.db'), 
                '--image_path',     os.path.join(self.basedir, 'images'),
                # '--ImageReader.single_camera', '1',
                # '--SiftExtraction.use_gpu', '0',
        ]

        self.matcher_args = [
            'colmap', self.match_type, 
                '--database_path',  os.path.join(self.basedir, 'database.db'), 
        ]

        self.mapper_args = [
            'colmap', 'mapper',
                '--database_path',  os.path.join(self.basedir, 'database.db'),
                '--image_path',     os.path.join(self.basedir, 'images'),
                '--output_path',    os.path.join(self.basedir, 'sparse'), 
                # --export_path changed to --output_path in colmap 3.6
                '--Mapper.num_threads', '16',
                '--Mapper.init_min_tri_angle', '4',
                '--Mapper.multiple_models', '0',
                '--Mapper.extract_colors', '0',
        ]
            
        self.image_undistorter_args = [
            'colmap', 'image_undistorter',
                '--image_path',     os.path.join(self.basedir, 'images'),
                '--input_path',     os.path.join(self.basedir, 'sparse','0'),
                '--output_path',    os.path.join(self.basedir, 'dense'),
                '--output_type',    'COLMAP',
                '--max_image_size', '2000',
        ]

        self.patch_match_stereo_args = [
            'colmap', 'patch_match_stereo',
                '--workspace_path',     os.path.join(self.basedir, 'dense'),
                '--workspace_format',   'COLMAP',
                '--PatchMatchStereo.geom_consistency', 'true',
        ]

        self.stereo_fusion_args = [
            'colmap', 'stereo_fusion',
                '--workspace_path',     os.path.join(self.basedir, 'dense'),
                '--workspace_format',   'COLMAP',
                '--input_type',         'geometric',
                '--output_path',        os.path.join(self.basedir, 'dense', 'fused.ply'), 
        ]

        self.poisson_mesher_args =[
            'colmap', 'poisson_mesher',
                '--input_path',     os.path.join(self.basedir, 'dense', 'fused.ply'),
                '--output_path',    os.path.join(self.basedir, 'dense', 'meshed-poisson.ply'),
        ]

        self.delaunay_mesher_args = [
            'colmap', 'delaunay_mesher',
                '--input_path',     os.path.join(self.basedir, 'dense'),
                '--output_path',    os.path.join(self.basedir, 'dense', 'meshed-delaunay.ply'),
        ]

    def run_all_colmap(self):
        logfile_name = os.path.join(self.basedir, 'colmap_output.txt')
        logfile = open(logfile_name, 'w')

        feat_output = ( subprocess.check_output(self.feature_extractor_args, shell=True, universal_newlines=True) )
        logfile.write(feat_output)
        print('Features extracted')

        match_output = ( subprocess.check_output(self.matcher_args, shell=True, universal_newlines=True) )
        logfile.write(match_output)
        print('Features matched')
        
        os.makedirs(os.path.join(self.basedir, 'sparse'), exist_ok=True)

        map_output = ( subprocess.check_output(self.mapper_args, shell=True, universal_newlines=True) )
        logfile.write(map_output)
        print('Sparse map created')

        os.makedirs(os.path.join(self.basedir, 'dense'), exist_ok=True)

        undistortion_output = ( subprocess.check_output(self.image_undistorter_args, shell=True, universal_newlines=True) )
        logfile.write(undistortion_output)
        # undistortion_output = subprocess.run(self.image_undistorter_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # print(f'returncode: {undistortion_output.returncode},stdout: {undistortion_output.stdout},stderr: {undistortion_output.stderr}')
        print('image undistorted')
 
        patch_match_stereo_output =  ( subprocess.check_output(self.patch_match_stereo_args, shell=True, universal_newlines=True) )
        logfile.write(patch_match_stereo_output)
        print('patch match stereo')

        fusion_output = ( subprocess.check_output(self.stereo_fusion_args, shell=True, universal_newlines=True) )
        logfile.write(fusion_output)
        # fusion_output = subprocess.run(self.stereo_fusion_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # print(f'returncode: {fusion_output.returncode},stdout: {fusion_output.stdout},stderr: {fusion_output.stderr}')
        print('image fused')

        poisson_output = ( subprocess.check_output(self.poisson_mesher_args, shell=True,universal_newlines=True))
        logfile.write(poisson_output)
        # poisson_output = subprocess.run(self.poisson_mesher_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # print(f'returncode: {poisson_output.returncode},stdout: {poisson_output.stdout},stderr: {poisson_output.stderr}')
        print('poisson mesh created')

        delaunay_output = ( subprocess.check_output(self.delaunay_mesher_args, shell=True, universal_newlines=True) )
        logfile.write(delaunay_output)
        # delaunay_output = subprocess.run(self.poisson_mesher_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # print(f'returncode: {delaunay_output.returncode},stdout: {delaunay_output.stdout},stderr: {delaunay_output.stderr}')
        print('delaunay mesh created')

        logfile.close()
        print( 'Finished running COLMAP, see {} for logs'.format(logfile_name) )

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', action='store', type = str, default='./data',
                        help = 'root directory of the dataset')
    parser.add_argument('--match_type', action='store', type = str,
                        help = 'feature matching type', 
                        default = 'exhaustive_matcher',
                        choices=['exhaustive_matcher', 'sequential_matcher', 'spatial_matcher','transitive_matcher', 'vocab_tree_matcher'])
    args = parser.parse_args()
    colmap_cmds = ColmapCommands(args.base_dir, args.match_type)
    colmap_cmds.run_all_colmap()