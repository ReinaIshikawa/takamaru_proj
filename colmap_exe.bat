@echo off

call set DATASET_PATH=./assets

call colmap feature_extractor --database_path %DATASET_PATH%/database.db --image_path %DATASET_PATH%/images


call colmap exhaustive_matcher --database_path %DATASET_PATH%/database.db

call mkdir %DATASET_PATH%/sparse

call colmap mapper^
    --database_path %DATASET_PATH%/database.db^
    --image_path %DATASET_PATH%/images^
    --output_path %DATASET_PATH%/sparse

call mkdir %DATASET_PATH%/dense

call colmap image_undistorter^
    --image_path %DATASET_PATH%/images^
    --input_path %DATASET_PATH%/sparse/0^
    --output_path %DATASET_PATH%/dense^
    --output_type COLMAP^
    --max_image_size 2000

call colmap patch_match_stereo^
    --workspace_path %DATASET_PATH%/dense^
    --workspace_format COLMAP^
    --PatchMatchStereo.geom_consistency true

call colmap stereo_fusion^
    --workspace_path %DATASET_PATH%/dense^
    --workspace_format COLMAP^
    --input_type geometric^
    --output_path %DATASET_PATH%/dense/fused.ply

call colmap poisson_mesher^
    --input_path %DATASET_PATH%/dense/fused.ply^
    --output_path %DATASET_PATH%/dense/meshed-poisson.ply

call colmap delaunay_mesher^
    --input_path %DATASET_PATH%/dense^
    --output_path %DATASET_PATH%/dense/meshed-delaunay.ply
