def check_unused_nodes(nodes)

def remove_unknown_unused_nodes(nodes):
    """
    Remove unknown/unused nodes from the scene.

    Args:
        scene: The scene object to perform the check on.
    """
    pass

def check_asset_naming_conventions(assets, naming_conventions):
    """
    Check if asset names match the specified naming conventions.

    Args:
        assets: List of assets to check.
        naming_conventions: The naming conventions to compare against.
    """
    pass

def check_node_hierarchy(scene, hierarchy_rules):
    """
    Check if the node hierarchy in the scene follows the specified hierarchy rules.

    Args:
        scene: The scene object to perform the check on.
        hierarchy_rules: The rules for the expected hierarchy.
    """
    pass

def check_reference_errors(scene):
    """
    Check if there are no reference errors in the scene.

    Args:
        scene: The scene object to perform the check on.
    """
    pass

def check_attributes_for_nan(assets):
    """
    Check attributes for NaN (very small decimals) in asset attributes and round to 4 decimal points.

    Args:
        assets: List of assets to check.
    """
    pass

def check_camera_aspect_ratio(camera):
    """
    Check if the camera aperture is in a 16:9 aspect ratio.

    Args:
        camera: The camera object to perform the check on.
    """
    pass

def check_camera_values(camera, allowed_focal_lengths, allowed_f_stops):
    """
    Check if the focal length and f-stop values of the camera are consistent with real-world cameras.

    Args:
        camera: The camera object to perform the check on.
        allowed_focal_lengths: List of allowed focal lengths.
        allowed_f_stops: List of allowed f-stop values.
    """
    pass

def check_set_transform_and_pivot(set_piece):
    """
    Check if the set transform and pivot are at the origin for a set piece.

    Args:
        set_piece: The set piece object to perform the check on.
    """
    pass

def check_set_piece_model_references(sets):
    """
    Check if the most recent version of each set piece model is referenced in sets.

    Args:
        sets: List of sets to check.
    """
    pass