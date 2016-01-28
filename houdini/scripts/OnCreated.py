"""Perform tasks when a Houdini node is created."""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors
import ht.nodes.naming

# =============================================================================
# FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
#    Name: main()
#  Raises: N/A
# Returns: None
#    Desc: Main function.
# -----------------------------------------------------------------------------
def main():
    node = kwargs["node"]

    ht.nodes.colors.colorNode(node)

    if ht.nodes.naming.isNamespacedType(node.type()):
        ht.nodes.naming.setNamespacedFormattedName(node)

# =============================================================================

main()

