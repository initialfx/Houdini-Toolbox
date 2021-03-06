#
# Produced by:
#       Graham Thompson
#       captainhammy@gmail.com
#       www.captainhammy.com
#
# Name: OnCreated.py
#
# Comments: Perform tasks when a Houdini node is created.
# 

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors

node = kwargs["node"]

ht.nodes.colors.colorNode(node)

