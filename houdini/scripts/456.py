#
# Produced by:
#       Graham Thompson
#       captainhammy@gmail.com
#       www.captainhammy.com
#
# Name: 456.py
#
# Comments: Perform tasks when a .hip file is loaded.
# 

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors

# Houdini Imports
import hou

# Initialize color settings.
ht.nodes.colors.createSessionColorManager()

# Remove an icon cache directory variable if it exists.
hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")

