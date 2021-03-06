#!/usr/bin/python
"""This script is a unit test suite for the inline.py module.

It can be executed directly from the command line, or directly using python or
Hython.

If run with regular Python it will attempt to import the hou module.  You must
have the Houdini environments sourced.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# Standard Library Imports
import datetime
import os
import sys
import unittest

def enableHouModule():
    """Set up the environment so that "import hou" works."""

    # Handle dlopen flags so dsos can be loaded correctly.
    if hasattr(sys, "setdlopenflags"):
        import DLFCN

        old_dlopen_flags = sys.getdlopenflags()
        sys.setdlopenflags(old_dlopen_flags | DLFCN.RTLD_GLOBAL)

    # Try to import hou.
    try:
        import hou
    # If it can't find it, make sure it is in the path.
    except ImportError:
        # Python needs to know where the hou module is.
        path = os.path.join(
            os.getenv("HH"),
            "python{0}.{1}".format(sys.version_info[0], sys.version_info[1])
        )

        # Append the path.
        sys.path.append(path)

        # Try again.
        import hou

    finally:
        # Restore old flags.
        if hasattr(sys, "setdlopenflags"):
            sys.setdlopenflags(old_dlopen_flags)

enableHouModule()

# Houdini Imports
import inline

OBJ = hou.node("/obj")

def getObjGeo(nodePath):
    """Get the geometry from the display node of a Geometry object.

    Args:
        nodePath : (str)
            A path to a Geometry object.

    Raises:
        N/A

    Returns:
        hou.Geometry
            The geometry of this object's display node.

    """
    return OBJ.node(nodePath).displayNode().geometry()

def getObjGeoCopy(nodePath):
    """Get a copy of the geometry from the display node of a Geometry object.

    Args:
        nodePath : (str)
            A path to a Geometry object.

    Raises:
        N/A

    Returns:
        hou.Geometry
            A copy of the geometry of this object's display node.

    """
    # Create a new hou.Geometry object.
    geo = hou.Geometry()

    # Get the geometry object's geo.
    sourceGeo = getObjGeo(nodePath)

    # Merge the geo to copy it.
    geo.merge(sourceGeo)

    return geo

class TestInlineCpp(unittest.TestCase):
    """This class implements test cases for the fuctions added through the
    inline.py module.

    """

    def setUp(self):
	pass

    def tearDown(self):
	pass

    def test_getVariable(self):
        hipName = hou.getVariable("HIPNAME")

        self.assertEqual(hipName, os.path.basename(hou.hipFile.path()))

    def test_setVariable(self):
        value = 22
        hou.setVariable("awesome", value)

        self.assertEqual(hou.getVariable("awesome"), 22)

    def test_getVariableNames(self):
        variableNames = hou.getVariableNames()

        self.assertTrue("ACTIVETAKE" in variableNames)

    def test_getDirtyVariableNames(self):
        variableNames = hou.getVariableNames()

        dirtyVariableNames = hou.getVariableNames(dirty=True)

        self.assertNotEqual(variableNames, dirtyVariableNames)

    def test_unsetVariable(self):
        hou.setVariable("tester", 10)
        hou.unsetVariable("tester")

        self.assertTrue(hou.getVariable("tester") is None)

    def test_varChange(self):
        parm = hou.parm("/obj/test_varChange/file1/file")

        string = "something_$VARCHANGE.bgeo"

        parm.set(string)

        path = parm.eval()

        self.assertEqual(path, string.replace("$VARCHANGE", ""))

        hou.setVariable("VARCHANGE", 22)

        hou.varChange()

        newPath = parm.eval()

        # Test the paths aren't the same.
        self.assertNotEqual(path, newPath)

        # Test the update was successful.
        self.assertEqual(newPath, string.replace("$VARCHANGE", "22"))

    def test_expandRange(self):
        values = hou.expandRange("0-5 10-20:2 64 65-66")
        target = (0, 1, 2, 3, 4, 5, 10, 12, 14, 16, 18, 20, 64, 65, 66)

        self.assertEqual(values, target)

    def test_isReadOnly(self):
        geo = getObjGeo("test_isReadOnly")

        self.assertTrue(geo.isReadOnly)

    def test_isReadOnlyFalse(self):
        geo = hou.Geometry()
        self.assertFalse(geo.isReadOnly())

    def test_sortByAttribute(self):
        geo = getObjGeoCopy("test_sortByAttribute")

        attrib = geo.findPrimAttrib("id")

        geo.sortByAttribute(attrib)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sortByAttributeReversed(self):
        geo = getObjGeoCopy("test_sortByAttribute")

        attrib = geo.findPrimAttrib("id")

        geo.sortByAttribute(attrib, reverse=True)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, list(reversed(range(10))))

    def test_sortByAttributeInvalidIndex(self):
        geo = getObjGeoCopy("test_sortByAttribute")

        attrib = geo.findPrimAttrib("id")

        self.assertRaises(
            IndexError,
            geo.sortByAttribute,
            attrib,
            1
        )

    def test_sortByAttributeDetail(self):
        geo = getObjGeoCopy("test_sortByAttribute")

        attrib = geo.findGlobalAttrib("varmap")

        self.assertRaises(
            hou.OperationFailed,
            geo.sortByAttribute,
            attrib
        )

    def test_sortAlongAxisPoints(self):
        geo = getObjGeoCopy("test_sortAlongAxisPoints")

        geo.sortAlongAxis(hou.geometryType.Points, 0)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sortAlongAxisPrims(self):
        geo = getObjGeoCopy("test_sortAlongAxisPrims")

        geo.sortAlongAxis(hou.geometryType.Primitives, 2)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sortByValues(self):
        # TODO: Test this.
        pass

    def test_sortRandomlyPoints(self):
        SEED = 11
        TARGET = [5, 9, 3, 8, 0, 2, 6, 1, 4, 7]

        geo = getObjGeoCopy("test_sortRandomlyPoints")
        geo.sortRandomly(hou.geometryType.Points, SEED)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortRandomlyPrims(self):
        SEED = 345
        TARGET = [4, 0, 9, 2, 1, 8, 3, 6, 7, 5]

        geo = getObjGeoCopy("test_sortRandomlyPrims")
        geo.sortRandomly(hou.geometryType.Primitives, SEED)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_shiftElementsPoints(self):
        OFFSET = -18
        TARGET = [8, 9, 0, 1, 2, 3, 4, 5, 6, 7]

        geo = getObjGeoCopy("test_shiftElementsPoints")
        geo.shiftElements(hou.geometryType.Points, OFFSET)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_shiftElementsPrims(self):
        OFFSET = 6
        TARGET = [4, 5, 6, 7, 8, 9, 0, 1, 2, 3]

        geo = getObjGeoCopy("test_shiftElementsPrims")
        geo.shiftElements(hou.geometryType.Primitives, OFFSET)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_reverseSortPoints(self):
        TARGET = range(10)
        TARGET.reverse()

        geo = getObjGeoCopy("test_reverseSortPoints")
        geo.reverseSort(hou.geometryType.Points)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_reverseSortPrims(self):
        TARGET = range(10)
        TARGET.reverse()

        geo = getObjGeoCopy("test_reverseSortPrims")
        geo.reverseSort(hou.geometryType.Primitives)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByProximityPoints(self):
        TARGET = [4, 3, 5, 2, 6, 1, 7, 0, 8, 9]
        POSITION = hou.Vector3(4, 1, 2)

        geo = getObjGeoCopy("test_sortByProximityPoints")
        geo.sortByProximityToPosition(hou.geometryType.Points, POSITION)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByProximityPrims(self):
        TARGET = [6, 7, 5, 8, 4, 9, 3, 2, 1, 0]
        POSITION = hou.Vector3(3, -1, 2)

        geo = getObjGeoCopy("test_sortByProximityPrims")
        geo.sortByProximityToPosition(hou.geometryType.Primitives, POSITION)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByVertexOrder(self):
        TARGET = range(10)

        geo = getObjGeoCopy("test_sortByVertexOrder")
        geo.sortByVertexOrder()

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByExpressionPoints(self):
        # TODO: Figure out how to test this.  Maybe include inline Python SOP?
        pass

    def test_sortByExpressionPrims(self):
        # TODO: Figure out how to test this.  Maybe include inline Python SOP?
        pass

    def test_createPoint(self):
        geo = hou.Geometry()

        point = geo.createPoint(hou.Vector3(1, 2, 3))

        self.assertEqual(point.position(), hou.Vector3(1, 2, 3))

    def test_createPoints(self):
        geo = hou.Geometry()
        points = geo.createPoints(15)

        self.assertEqual(points, geo.points())

    def test_createPointsInvalidNumber(self):
        geo = hou.Geometry()

        self.assertRaises(
            hou.OperationFailed,
            geo.createPoints,
            -4
        )

    def test_mergePointGroup(self):
        geo = hou.Geometry()
        sourceGeo = getObjGeo("test_mergePointGroup")

        group = sourceGeo.pointGroups()[0]

        geo.mergePointGroup(group)

        self.assertEqual(len(geo.iterPoints()), len(group.points()))

    def test_mergePoints(self):
        geo = hou.Geometry()
        sourceGeo = getObjGeo("test_mergePoints")

        points = sourceGeo.globPoints("0 6 15 35-38 66")

        geo.mergePoints(points)

        self.assertEqual(len(geo.iterPoints()), len(points))

    def test_mergePrimGroup(self):
        geo = hou.Geometry()
        sourceGeo = getObjGeo("test_mergePrimGroup")

        group = sourceGeo.primGroups()[0]

        geo.mergePrimGroup(group)

        self.assertEqual(len(geo.iterPrims()), len(group.prims()))

    def test_mergePrims(self):
        geo = hou.Geometry()
        sourceGeo = getObjGeo("test_mergePrims")

        prims = sourceGeo.globPrims("0 6 15 35-38 66")

        geo.mergePrims(prims)

        self.assertEqual(len(geo.iterPrims()), len(prims))

    def test_varmap(self):
        TARGET = {'test': 'TEST', 'attribute1': 'ATTRIBUTE1', 'that': 'THING'}

        geo = getObjGeo("test_varmap")

        self.assertEqual(geo.varmap(), TARGET)

    def test_setVarmap(self):
        TARGET = {'who': 'WHO', 'attribute2': 'ATTRIBUTE2', 'him': 'HER'}

        geo = hou.Geometry()
        geo.setVarmap(TARGET)

        self.assertEqual(geo.varmap(), TARGET)

    def test_addVariableName(self):
        TARGET = {'attribute1': 'ATTRIBUTE1', 'attribute1': 'TEST'}

        geo = getObjGeoCopy("test_addVariableName")

        attribute = geo.findPointAttrib("attribute1")

        geo.addVariableName(attribute, "TEST")

        self.assertEqual(geo.varmap(), TARGET)

    def test_removeVariableName(self):
        geo = getObjGeoCopy("test_removeVariableName")

        geo.removeVariableName("ATTRIBUTE1")

        self.assertEqual(geo.varmap(), {})

    def test_renameAttributeVertex(self):
        geo = getObjGeoCopy("test_renameAttributeVertex")
        attrib = geo.findVertexAttrib("goodbye")

        new_attrib = attrib.rename("aurevroir")

        self.assertEqual(new_attrib.name(), "aurevroir")

    def test_renameAttributePoint(self):
        geo = getObjGeoCopy("test_renameAttributePoint")
        attrib = geo.findPointAttrib("hello")

        new_attrib = attrib.rename("test")

        self.assertEqual(new_attrib.name(), "test")

    def test_renameAttributeP(self):
        geo = getObjGeoCopy("test_renameAttributePoint")
        attrib = geo.findPointAttrib("P")

        self.assertRaises(
            hou.OperationFailed,
            attrib.rename,
            "test"
        )

    def test_renameAttributePrim(self):
        geo = getObjGeoCopy("test_renameAttributePrim")
        attrib = geo.findPrimAttrib("today")

        new_attrib = attrib.rename("tomorrow")

        self.assertEqual(new_attrib.name(), "tomorrow")

    def test_renameAttributeGlobal(self):
        geo = getObjGeoCopy("test_renameAttributeGlobal")
        attrib = geo.findGlobalAttrib("welcome")

        new_attrib = attrib.rename("getlost")

        self.assertEqual(new_attrib.name(), "getlost")

    def test_findPrimByName(self):
        geo = getObjGeo("test_findPrimByName")

        prim = geo.findPrimByName("piece2")

        self.assertEqual(prim.number(), 2)

    def test_findPrimByNameMatch2(self):
        geo = getObjGeo("test_findPrimByNameMatch2")

        prim = geo.findPrimByName("piece3", match_number=2)

        self.assertEqual(prim.number(), 21)

    def test_findPrimByName(self):
        geo = getObjGeo("test_findPrimByNameOtherName")

        prim = geo.findPrimByName("piece4", "thinger")

        self.assertEqual(prim.number(), 4)

    def test_findAllPrimsByName(self):
        TARGET = [5, 13, 21, 29, 37, 45, 53, 61, 69, 77]

        geo = getObjGeo("test_findAllPrimsByName")

        prims = geo.findAllPrimsByName("piece5")

        values = [prim.number() for prim in prims]

        self.assertEqual(values, TARGET)

    def test_findAllPrimsByNameOtherName(self):
        TARGET = [2, 16, 30, 44, 58, 72]

        geo = getObjGeo("test_findAllPrimsByNameOtherName")

        prims = geo.findAllPrimsByName("piece2", "something")

        values = [prim.number() for prim in prims]

        self.assertEqual(values, TARGET)

    def test_copyPointAttributeValues(self):
        source = getObjGeo("test_copyPointAttributeValues")

        attribs = source.pointAttribs()

        geo = hou.Geometry()

        p1 = geo.createPoint()
        p2 = geo.createPoint()

        p1.copyAttribValues(source.iterPoints()[2], attribs)
        p2.copyAttribValues(source.iterPoints()[6], attribs)

        # Ensure all the attributes got copied right.
        self.assertEqual(len(geo.pointAttribs()), len(attribs))

        # Ensure P got copied right.
        self.assertEqual(p1.position(), hou.Vector3(5, 0, -5))
        self.assertEqual(p2.position(), hou.Vector3(-5, 0, 5))

    def test_copyPrimAttributeValues(self):
        source = getObjGeo("test_copyPrimAttributeValues")

        attribs = source.primAttribs()

        geo = hou.Geometry()

        p1 = geo.createPolygon()
        p2 = geo.createPolygon()

        p1.copyAttribValues(source.iterPrims()[1], attribs)
        p2.copyAttribValues(source.iterPrims()[4], attribs)

        # Ensure all the attributes got copied right.
        self.assertEqual(len(geo.primAttribs()), len(attribs))

        # Ensure P got copied right.
        self.assertEqual(p1.attribValue("prnum"), 1)
        self.assertEqual(p2.attribValue("prnum"), 4)

    def test_pointAdjacentPolygons(self):
        geo = getObjGeo("test_pointAdjacentPolygons")

        TARGET = geo.globPrims("1 2")

        prims = geo.iterPrims()[0].pointAdjacentPolygons()

        self.assertEqual(prims, TARGET)

    def test_edgeAdjacentPolygons(self):
        geo = getObjGeo("test_edgeAdjacentPolygons")

        TARGET = geo.globPrims("2")

        prims = geo.iterPrims()[0].edgeAdjacentPolygons()

        self.assertEqual(prims, TARGET)

    def test_connectedPrims(self):
        geo = getObjGeo("test_connectedPrims")

        TARGET = geo.prims()

        prims = geo.iterPoints()[4].connectedPrims()

        self.assertEqual(prims, TARGET)

    def test_connectedPoints(self):
        geo = getObjGeo("test_connectedPoints")

        TARGET = geo.globPoints("1 3 5 7")

        points = geo.iterPoints()[4].connectedPoints()

        self.assertEqual(points, TARGET)

    def test_referencingVertices(self):
        geo = getObjGeo("test_referencingVertices")

        TARGET = geo.globVertices("0v2 1v3 2v1 3v0")

        verts = geo.iterPoints()[4].referencingVertices()

        self.assertEqual(verts, TARGET)

    def test_pointStringAttribValues(self):
        geo = getObjGeo("test_pointStringAttribValues")
        TARGET = ('point0', 'point1', 'point2', 'point3', 'point4')

        values = geo.pointStringAttribValues("test")

        self.assertTrue(values, TARGET)

    def test_pointStringAttribValuesInvalidAttribute(self):
        geo = getObjGeo("test_pointStringAttribValues")

        self.assertRaises(
            hou.OperationFailed,
            geo.pointStringAttribValues,
            "bad_name"
        )

    def test_pointStringAttribValuesNotString(self):
        geo = getObjGeo("test_pointStringAttribValues")

        self.assertRaises(
            hou.OperationFailed,
            geo.pointStringAttribValues,
            "P"
        )

    def test_setPointStringAttribValues(self):
        TARGET = ('point0', 'point1', 'point2', 'point3', 'point4')

        geo = hou.Geometry()
        geo.createPoints(5)
        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        geo.setPointStringAttribValues("test", TARGET)

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(tuple(vals), TARGET)

    def test_setPointStringAttribValuesInvalidAttribute(self):
        TARGET = ('point0', 'point1', 'point2', 'point3', 'point4')
        geo = hou.Geometry()

        self.assertRaises(
            hou.OperationFailed,
            geo.setPointStringAttribValues,
            "test", TARGET
        )

    def test_setPointStringAttribValuesInvalidAttributeType(self):
        TARGET = ('point0', 'point1', 'point2', 'point3', 'point4')
        geo = hou.Geometry()

        attr = geo.addAttrib(hou.attribType.Point, "test", 1)

        self.assertRaises(
            hou.OperationFailed,
            geo.setPointStringAttribValues,
            "test", TARGET
        )

    def test_setPointStringAttribValuesInvalidAttributeSize(self):
        TARGET = ('point0', 'point1', 'point2', 'point3', 'point4')
        geo = hou.Geometry()
        geo.createPoints(4)
        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        self.assertRaises(
            hou.OperationFailed,
            geo.setPointStringAttribValues,
            "test", TARGET
        )

    def test_setSharedPointStringAttrib(self):
        TARGET = ["point0"]*5
        geo = hou.Geometry()
        geo.createPoints(5)
        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        geo.setSharedPointStringAttrib(attr, "point0")

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, TARGET)

    def test_setSharedPointStringAttribGroup(self):
        TARGET = ["point0"]*5 + [""]*5

        geo = hou.Geometry()

        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        geo.createPoints(5)
        group = geo.createPointGroup("group1")

        for point in geo.points():
            group.add(point)

        geo.createPoints(5)

        geo.setSharedPointStringAttrib(attr, "point0", group)

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, TARGET)

    def test_primStringAttribValues(self):
        geo = getObjGeo("test_primStringAttribValues")
        TARGET = ('prim0', 'prim1', 'prim2', 'prim3', 'prim4')

        values = geo.primStringAttribValues("test")

        self.assertTrue(values, TARGET)

    def test_primStringAttribValuesInvalidAttribute(self):
        geo = getObjGeo("test_primStringAttribValues")

        self.assertRaises(
            hou.OperationFailed,
            geo.primStringAttribValues,
            "bad_name"
        )

    def test_primStringAttribValuesNotString(self):
        geo = getObjGeo("test_primStringAttribValues")

        self.assertRaises(
            hou.OperationFailed,
            geo.primStringAttribValues,
            "notstring"
        )

    def test_setPrimStringAttribValues(self):
        TARGET = ('prim0', 'prim1', 'prim2', 'prim3', 'prim4')

        geo = getObjGeoCopy("test_setPrimStringAttribValues")
        attr = geo.findPrimAttrib("test")

        geo.setPrimStringAttribValues("test", TARGET)

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(tuple(vals), TARGET)

    def test_setPrimStringAttribValuesInvalidAttribute(self):
        TARGET = ('prim0', 'prim1', 'prim2', 'prim3', 'prim4')

        geo = getObjGeoCopy("test_setPrimStringAttribValues")

        self.assertRaises(
            hou.OperationFailed,
            geo.setPrimStringAttribValues,
            "thing", TARGET
        )

    def test_setPrimStringAttribValuesInvalidAttributeType(self):
        TARGET = ('prim0', 'prim1', 'prim2', 'prim3', 'prim4')

        geo = getObjGeoCopy("test_setPrimStringAttribValues")

        self.assertRaises(
            hou.OperationFailed,
            geo.setPrimStringAttribValues,
            "notstring", TARGET
        )

    def test_setPrimStringAttribValuesInvalidAttributeSize(self):
        TARGET = ('prim0', 'prim1', 'prim2', 'prim3')

        geo = getObjGeoCopy("test_setPrimStringAttribValues")

        self.assertRaises(
            hou.OperationFailed,
            geo.setPrimStringAttribValues,
            "test", TARGET
        )

    def test_setSharedPrimStringAttrib(self):
        TARGET = ["value"]*5

        geo = getObjGeoCopy("test_setSharedPrimStringAttrib")

        attr = geo.findPrimAttrib("test")

        geo.setSharedPrimStringAttrib(attr, "value")

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, TARGET)

    def test_setSharedPrimStringAttribGroup(self):
        TARGET = ["value"]*3 + ["", ""]

        geo = getObjGeoCopy("test_setSharedPrimStringAttrib")

        attr = geo.findPrimAttrib("test")

        group = geo.findPrimGroup("group1")

        geo.setSharedPrimStringAttrib(attr, "value", group)

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, TARGET)

    def test_hasEdge(self):
        geo = getObjGeo("test_hasEdge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p1 = geo.iterPoints()[1]

        self.assertTrue(face.hasEdge(p0, p1))

    def test_hasEdgeFail(self):
        geo = getObjGeo("test_hasEdge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p2 = geo.iterPoints()[2]

        self.assertTrue(face.hasEdge(p0, p2))

    def test_sharedEdges(self):
        geo = getObjGeo("test_sharedEdges")

        pr0, pr1 = geo.prims()

        edges = pr0.sharedEdges(pr1)

        pt2 = geo.iterPoints()[2]
        pt3 = geo.iterPoints()[3]

        edge = geo.findEdge(pt2, pt3)

        self.assertEqual(edges, (edge,))


    def test_insertVertex(self):
        geo = getObjGeoCopy("test_insertVertex")

        face = geo.iterPrims()[0]

        pt = geo.createPoint(hou.Vector3(0.5, 0, 0.5))

        face.insertVertex(pt, 2)

        self.assertEqual(face.vertex(2).point(), pt)

    def test_insertVertexNegativeIndex(self):
        geo = getObjGeoCopy("test_insertVertex")

        face = geo.iterPrims()[0]

        pt = geo.createPoint(hou.Vector3(0.5, 0, 0.5))

        self.assertRaises(
            IndexError,
            face.insertVertex,
            pt,
            -1
        )

    def test_insertVertexInvalidIndex(self):
        geo = getObjGeoCopy("test_insertVertex")

        face = geo.iterPrims()[0]

        pt = geo.createPoint(hou.Vector3(0.5, 0, 0.5))

        self.assertRaises(
            IndexError,
            face.insertVertex,
            pt,
            10
        )

    def test_deleteVertex(self):
        geo = getObjGeoCopy("test_deleteVertex")

        face = geo.iterPrims()[0]

        face.deleteVertex(3)

        self.assertEqual(len(face.vertices()), 3)

    def test_deleteVertexNegativeIndex(self):
        geo = getObjGeoCopy("test_deleteVertex")

        face = geo.iterPrims()[0]

        self.assertRaises(
            IndexError,
            face.deleteVertex,
            -1
        )

    def test_deleteVertexInvalidIndex(self):
        geo = getObjGeoCopy("test_deleteVertex")

        face = geo.iterPrims()[0]

        self.assertRaises(
            IndexError,
            face.deleteVertex,
            10
        )

    def test_setPoint(self):
        geo = getObjGeoCopy("test_setPoint")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        face.setPoint(3, pt)

        self.assertEqual(face.vertex(3).point().number(), 4)

    def test_setPointNegativeIndex(self):
        geo = getObjGeoCopy("test_setPoint")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        self.assertRaises(
            IndexError,
            face.setPoint,
            -1,
            pt
        )

    def test_setPointInvalidIndex(self):
        geo = getObjGeoCopy("test_setPoint")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        self.assertRaises(
            IndexError,
            face.setPoint,
            10,
            pt
        )

    def test_baryCenter(self):
        TARGET = hou.Vector3(1.5, 1, -1)
        geo = getObjGeoCopy("test_baryCenter")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.baryCenter(), TARGET)

    def test_primitiveArea(self):
        TARGET = 4.375
        geo = getObjGeoCopy("test_primitiveArea")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.area(), TARGET)

    def test_perimeter(self):
        TARGET = 6.5
        geo = getObjGeoCopy("test_perimeter")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.perimeter(), TARGET)

    def test_reversePrim(self):
        TARGET = hou.Vector3(0, -1, 0)
        geo = getObjGeoCopy("test_reversePrim")

        prim = geo.iterPrims()[0]
        prim.reverse()

        self.assertEqual(prim.normal(), TARGET)

    def test_makeUnique(self):
        TARGET = 28
        geo = getObjGeoCopy("test_makeUnique")

        prim = geo.iterPrims()[4]
        prim.makeUnique()

        self.assertEqual(len(geo.iterPoints()), TARGET)

    def test_primBoundingBox(self):
        TARGET = hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)
        geo = getObjGeoCopy("test_primBoundingBox")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.boundingBox(), TARGET)

    def test_computePointNormals(self):
        geo = getObjGeoCopy("test_computePointNormals")

        geo.computePointNormals()

        self.assertNotEqual(geo.findPointAttrib("N"), None)

    def test_addPointNormalAttribute(self):
        geo = getObjGeoCopy("test_addPointNormalAttribute")

        self.assertNotEqual(geo.addPointNormals(), None)

    def test_addPointVelocityAttribute(self):
        geo = getObjGeoCopy("test_addPointVelocityAttribute")

        self.assertNotEqual(geo.addPointVelocity(), None)

    def test_addColorAttributePoint(self):
        geo = getObjGeoCopy("test_addColorAttribute")

        result = geo.addColorAttribute(hou.attribType.Point)

        self.assertNotEqual(result, None)

    def test_addColorAttributePrim(self):
        geo = getObjGeoCopy("test_addColorAttribute")

        result = geo.addColorAttribute(hou.attribType.Prim)

        self.assertNotEqual(result, None)

    def test_addColorAttributeVertex(self):
        geo = getObjGeoCopy("test_addColorAttribute")

        result = geo.addColorAttribute(hou.attribType.Vertex)

        self.assertNotEqual(result, None)

    def test_addColorAttributePoint(self):
        geo = getObjGeoCopy("test_addColorAttribute")

        self.assertRaises(
            hou.TypeError,
            geo.addColorAttribute,
            hou.attribType.Global
        )

    def test_convex(self):
        geo = getObjGeoCopy("test_convex")

        geo.convex()

        self.assertEqual(len(geo.iterPrims()), 162)

        verts = [vert for prim in geo.prims() for vert in prim.vertices()]
        self.assertEqual(len(verts), 486)

    def test_clip(self):
        geo = getObjGeoCopy("test_clip")

        origin = hou.Vector3(0, 0, 0)

        direction = hou.Vector3(-0.5, 0.6, -0.6)

        geo.clip(origin, direction, 0.5)

        self.assertEqual(len(geo.iterPrims()), 42)

        self.assertEqual(len(geo.iterPoints()), 60)

    def test_clipBelow(self):
        geo = getObjGeoCopy("test_clipBelow")

        origin = hou.Vector3(0, -0.7, -0.9)

        direction = hou.Vector3(-0.6, 0.1, -0.8)

        geo.clip(origin, direction, 0.6, below=True)

        self.assertEqual(len(geo.iterPrims()), 61)

        self.assertEqual(len(geo.iterPoints()), 81)

    def test_clipGroup(self):
        geo = getObjGeoCopy("test_clipGroup")

        group = geo.primGroups()[0]

        origin = hou.Vector3(-1.3, -1.5, 1.2)

        direction = hou.Vector3(0.8, 0.02, 0.5)

        geo.clip(origin, direction, -0.3, group=group)

        self.assertEqual(len(geo.iterPrims()), 74)

        self.assertEqual(len(geo.iterPoints()), 98)

    def test_destroyEmptyPointGroups(self):
        geo = hou.Geometry()

        geo.createPointGroup("empty")

        geo.destroyEmptyGroups(hou.attribType.Point)

        self.assertEqual(len(geo.pointGroups()), 0)

    def test_destroyEmptyPrimGroups(self):
        geo = hou.Geometry()

        geo.createPrimGroup("empty")

        geo.destroyEmptyGroups(hou.attribType.Prim)

        self.assertEqual(len(geo.primGroups()), 0)

    def test_destroyUnusedPoints(self):
        geo = getObjGeoCopy("test_destroyUnusedPoints")

        geo.destroyUnusedPoints()

        self.assertEqual(len(geo.iterPoints()), 20)

    def test_destroyUnusedPointsGroup(self):
        geo = getObjGeoCopy("test_destroyUnusedPointsGroup")

        group = geo.pointGroups()[0]

        geo.destroyUnusedPoints(group)

        self.assertEqual(len(geo.iterPoints()), 3729)

    def test_consolidatePoints(self):
        geo = getObjGeoCopy("test_consolidatePoints")

        geo.consolidatePoints()

        self.assertEqual(len(geo.iterPoints()), 100)

    def test_consolidatePointsDist(self):
        geo = getObjGeoCopy("test_consolidatePointsDist")

        geo.consolidatePoints(3)

        self.assertEqual(len(geo.iterPoints()), 16)

    def test_consolidatePointsGroup(self):
        geo = getObjGeoCopy("test_consolidatePointsGroup")

        group = geo.pointGroups()[0]

        geo.consolidatePoints(group=group)

        self.assertEqual(len(geo.iterPoints()), 212)

    def test_uniquePoints(self):
        geo = getObjGeoCopy("test_uniquePoints")

        geo.uniquePoints()

        self.assertEqual(len(geo.iterPoints()), 324)

    def test_uniquePointsPointGroup(self):
        geo = getObjGeoCopy("test_uniquePointsPointGroup")

        group = geo.pointGroups()[0]
        geo.uniquePoints(group)

        self.assertEqual(len(geo.iterPoints()), 195)

    def test_uniquePointsPrimGroup(self):
        geo = getObjGeoCopy("test_uniquePointsPrimGroup")

        group = geo.primGroups()[0]
        geo.uniquePoints(group)

        self.assertEqual(len(geo.iterPoints()), 195)

    def test_groupBoundingBoxPoint(self):
        TARGET = hou.BoundingBox(-4, 0, -1, -2, 0, 2)

        geo = getObjGeo("test_groupBoundingBoxPoint")

        group = geo.pointGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_groupBoundingBoxPrim(self):
        TARGET = hou.BoundingBox(-5, 0, -4, 4, 0, 5)

        geo = getObjGeo("test_groupBoundingBoxPrim")

        group = geo.primGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_togglePoint(self):
        geo = getObjGeoCopy("test_togglePoint")

        group = geo.pointGroups()[0]
        point = geo.iterPoints()[0]

        group.toggle(point)

        self.assertTrue(group.contains(point))

    def test_togglePrim(self):
        geo = getObjGeoCopy("test_togglePrim")

        group = geo.primGroups()[0]
        prim = geo.iterPrims()[0]

        group.toggle(prim)

        self.assertTrue(group.contains(prim))

    def test_toggleEntriesPoint(self):
        geo = getObjGeoCopy("test_toggleEntriesPoint")

        vals = geo.globPoints(" ".join([str(val) for val in range(1, 100, 2)]))

        group = geo.pointGroups()[0]
        group.toggleEntries()

        self.assertEquals(group.points(), vals)

    def test_toggleEntriesPrim(self):
        geo = getObjGeoCopy("test_toggleEntriesPrim")

        vals = geo.globPrims(" ".join([str(val) for val in range(0, 100, 2)]))

        group = geo.primGroups()[0]
        group.toggleEntries()

        self.assertEquals(group.prims(), vals)

    def test_copyPointGroup(self):
        geo = getObjGeoCopy("test_copyPointGroup")

        group = geo.pointGroups()[0]

        new_group = group.copy("new_group")

        self.assertEquals(group.points(), new_group.points())

    def test_copyPointGroupSameName(self):
        geo = getObjGeoCopy("test_copyPointGroup")

        group = geo.pointGroups()[0]

        self.assertRaises(
            hou.OperationFailed,
            group.copy,
            group.name()
        )

    def test_copyPointGroupExisting(self):
        geo = getObjGeoCopy("test_copyPointGroupExisting")

        group = geo.pointGroups()[-1]

        other_group = geo.pointGroups()[0]

        self.assertRaises(
            hou.OperationFailed,
            group.copy,
            other_group.name()
        )

    def test_copyPrimGroup(self):
        return
        geo = getObjGeoCopy("test_copyPrimGroup")

        group = geo.primGroups()[0]

        new_group = group.copy("new_group")

        self.assertEquals(group.prims(), new_group.prims())

    def test_copyPrimGroupSameName(self):
        return
        geo = getObjGeoCopy("test_copyPrimGroup")

        group = geo.primGroups()[0]

        self.assertRaises(
            hou.OperationFailed,
            group.copy,
            group.name()
        )

    def test_copyPrimGroupExisting(self):
        return
        geo = getObjGeoCopy("test_copyPrimGroupExisting")

        group = geo.primGroups()[-1]

        other_group = geo.primGroups()[0]

        self.assertRaises(
            hou.OperationFailed,
            group.copy,
            other_group.name()
        )

    def test_pointGroupContainsAny(self):
        geo = getObjGeoCopy("test_pointGroupContainsAny")

        group1 = geo.pointGroups()[0]
        group2 = geo.pointGroups()[1]

        self.assertTrue(group1.containsAny(group2))

    def test_pointGroupContainsAnyFalse(self):
        geo = getObjGeoCopy("test_pointGroupContainsAnyFalse")

        group1 = geo.pointGroups()[0]
        group2 = geo.pointGroups()[1]

        self.assertFalse(group1.containsAny(group2))

    def test_primGroupContainsAny(self):
        geo = getObjGeoCopy("test_primGroupContainsAny")

        group1 = geo.primGroups()[0]
        group2 = geo.primGroups()[1]

        self.assertTrue(group1.containsAny(group2))

    def test_primGroupContainsAnyFalse(self):
        geo = getObjGeoCopy("test_primGroupContainsAnyFalse")

        group1 = geo.primGroups()[0]
        group2 = geo.primGroups()[1]

        self.assertFalse(group1.containsAny(group2))

    def test_convertToPointGroup(self):
        geo = getObjGeoCopy("test_convertToPointGroup")

        group = geo.primGroups()[0]

        new_group = group.convertToPointGroup()

        self.assertEqual(len(new_group.points()), 12)

        # Check source group was deleted.
        self.assertEqual(len(geo.primGroups()), 0)

    def test_convertToPointGroupWithName(self):
        geo = getObjGeoCopy("test_convertToPointGroup")

        group = geo.primGroups()[0]

        new_group = group.convertToPointGroup("new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convertToPointGroupNoDestroy(self):
        geo = getObjGeoCopy("test_convertToPointGroup")

        group = geo.primGroups()[0]

        new_group = group.convertToPointGroup(destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    def test_convertToPrimGroup(self):
        geo = getObjGeoCopy("test_convertToPrimGroup")

        group = geo.pointGroups()[0]

        new_group = group.convertToPrimGroup()

        self.assertEqual(len(new_group.prims()), 5)

        # Check source group was deleted.
        self.assertEqual(len(geo.pointGroups()), 0)

    def test_convertToPrimGroupWithName(self):
        geo = getObjGeoCopy("test_convertToPrimGroup")

        group = geo.pointGroups()[0]

        new_group = group.convertToPrimGroup("new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convertToPrimGroupNoDestroy(self):
        geo = getObjGeoCopy("test_convertToPrimGroup")

        group = geo.pointGroups()[0]

        new_group = group.convertToPrimGroup(destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    def test_isInside(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(-1, -1, -1, 1, 1, 1)

        self.assertTrue(bbox1.isInside(bbox2))

    def test_isInsideFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.isInside(bbox2))

    def test_intersects(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(bbox1.intersects(bbox2))

    def test_intersectsFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.intersects(bbox2))

    def test_computeIntersection(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(bbox1.computeIntersection(bbox2))

        self.assertEqual(bbox1.minvec(), hou.Vector3())
        self.assertEqual(bbox1.maxvec(), hou.Vector3(0.5, 0.5, 0.5))

    def test_computeIntersectionFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.computeIntersection(bbox2))

    def test_expandBounds(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.expandBounds(1, 1, 1)

        self.assertEqual(bbox.minvec(), hou.Vector3(-2, -2.75, -4))
        self.assertEqual(bbox.maxvec(), hou.Vector3(2, 2.75, 4))

    def test_addToMin(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.addToMin(hou.Vector3(1, 0.25, 1))

        self.assertEqual(bbox.minvec(), hou.Vector3(0, -1.5, -2))

    def test_addToMax(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.addToMax(hou.Vector3(2, 0.25, 1))

        self.assertEqual(bbox.maxvec(), hou.Vector3(3, 2, 4))

    def test_area(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(bbox.area(), 80)

    def test_volume(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(bbox.volume(), 42)

    def test_parmIsDefault(self):
        node = OBJ.createNode("geo")
        p = node.parm("tx")

        self.assertTrue(p.isDefault())

    def test_parmIsNotDefault(self):
        node = OBJ.createNode("geo")
        p = node.parm("tx")
        p.set(5)

        self.assertFalse(p.isDefault())

    def test_parmTupleIsDefault(self):
        node = OBJ.createNode("geo")
        pt = node.parmTuple("t")

        self.assertTrue(pt.isDefault())

    def test_parmTupleNotIsDefault(self):
        node = OBJ.createNode("geo")
        pt = node.parmTuple("t")
        pt.set((1,2,3))

        self.assertFalse(pt.isDefault())

    def test_getReferencingParms(self):
        node = OBJ.node("test_getReferencingParms")

        parm = node.parm("file1/file")

        self.assertEquals(len(parm.getReferencingParms()), 2)

    def test_isMultiParm(self):
        node = OBJ.node("test_isMultiParm/object_merge")
        parm = node.parm("numobj")

        self.assertTrue(parm.isMultiParm())

        parmTuple = node.parmTuple("numobj")
        self.assertTrue(parmTuple.isMultiParm())

    def test_isMultiParmFalse(self):
        node = OBJ.node("test_isMultiParm/object_merge")
        parm = node.parm("objpath1")

        self.assertFalse(parm.isMultiParm())

        parmTuple = node.parmTuple("objpath1")
        self.assertFalse(parmTuple.isMultiParm())

    def test_getMultiParmInstanceIndex(self):
        TARGET = (1, )

        node = OBJ.node("test_getMultiParmInstanceIndex/object_merge")
        parm = node.parm("objpath1")

        self.assertEqual(parm.getMultiParmInstanceIndex(), TARGET)

    def test_getMultiParmInstanceIndexFail(self):
        TARGET = (1, )

        node = OBJ.node("test_getMultiParmInstanceIndex/object_merge")
        parm = node.parm("numobj")

        self.assertRaises(
            hou.OperationFailed,
            parm.getMultiParmInstanceIndex
        )

    def test_getTupleMultiParmInstanceIndex(self):
        TARGET = (1, )

        node = OBJ.node("test_getMultiParmInstanceIndex/object_merge")
        parmTuple = node.parmTuple("objpath1")

        self.assertEqual(parmTuple.getMultiParmInstanceIndex(), TARGET)

    def test_getTupleMultiParmInstanceIndexFail(self):
        TARGET = (1, )

        node = OBJ.node("test_getMultiParmInstanceIndex/object_merge")
        parmTuple = node.parmTuple("numobj")

        self.assertRaises(
            hou.OperationFailed,
            parmTuple.getMultiParmInstanceIndex
        )

    def test_insertMultiParmItem(self):
        TARGET = "/obj/test_hasEdge"

        node = OBJ.node("test_insertMultiParmItem/object_merge")
        parmTuple = node.parmTuple("numobj")

        parmTuple.insertMultiParmItem(0)

        path = node.evalParm("objpath2")
        self.assertEqual(path, TARGET)

    def test_removeMultiParmItem(self):
        TARGET = "/obj/test_insertVertex"

        node = OBJ.node("test_removeMultiParmItem/object_merge")
        parmTuple = node.parmTuple("numobj")

        parmTuple.removeMultiParmItem(0)

        path = node.evalParm("objpath1")
        self.assertEqual(path, TARGET)

    def test_getMultiParmInstances(self):
        node = OBJ.node("test_getMultiParmInstances/object_merge")

        TARGET = (
            (
                node.parm("enable1"),
                node.parm("objpath1"),
                node.parm("group1"),
                node.parm("expand1")
            ),
            (
                node.parm("enable2"),
                node.parm("objpath2"),
                node.parm("group2"),
                node.parm("expand2")
            )
        )

        parmTuple = node.parmTuple("numobj")

        instances = parmTuple.getMultiParmInstances()

        self.assertEqual(instances, TARGET)

    def test_getMultiParmInstanceValues(self):
        node = OBJ.node("test_getMultiParmInstanceValues/object_merge")

        TARGET = (
            (
                1,
                "/obj/test_hasEdge",
                "group2",
                1
            ),
            (
                1,
                "/obj/test_insertVertex",
                "",
                0
            )
        )

        parmTuple = node.parmTuple("numobj")

        values = parmTuple.getMultiParmInstanceValues()

        self.assertEqual(values, TARGET)

    def test_disconnectAllOutputs(self):
        node = OBJ.node("test_disconnectAllOutputs/file")

        node.disconnectAllOutputs()

        self.assertEqual(len(node.outputs()), 0)

    def test_disconnectAllInputs(self):
        node = OBJ.node("test_disconnectAllInputs/merge")

        node.disconnectAllInputs()

        self.assertEqual(len(node.inputs()), 0)

    def test_nodeInputLabel(self):
        node = OBJ.createNode("geo")
        self.assertEqual(node.inputLabel(0), "parent")

    def test_messageNodes(self):
        node = OBJ.node("test_messageNodes/solver")

        self.assertEqual(len(node.messageNodes()), 1)

    def test_representativeNode(self):
        node = OBJ.createNode("stereocamrig")

        TARGET = node.node("stereo_camera")

        self.assertEqual(node.representativeNode(), TARGET)

    def test_isContainedBy(self):
        node = OBJ.createNode("geo")

        box = node.createNode("box")

        self.assertTrue(box.isContainedBy(node))

    def test_isContainedByFalse(self):
        node = OBJ.createNode("geo")

        self.assertFalse(node.isContainedBy(hou.node("/shop")))

    def test_isEditable(self):
        fur = OBJ.createNode("fur")

        clumps = fur.node("clumps")

        self.assertTrue(clumps.isEditable())

    def test_isEditableFalse(self):
        fur = OBJ.createNode("fur")

        clumps = fur.node("input_skin")

        self.assertFalse(clumps.isEditable())

    def test_isCompiled(self):
        # TODO: Figure out how to test this.
        pass

    def test_getOpReferences(self):
        node = OBJ.node("test_getOpReferences")

        self.assertEqual(len(node.getOpReferences()), 2)

    def test_getOpReferencesRecurse(self):
        node = OBJ.node("test_getOpReferences")

        self.assertEqual(len(node.getOpReferences(True)), 3)

    def test_getOpDependents(self):
        node = OBJ.node("test_getOpDependents/box2")

        self.assertEqual(len(node.getOpDependents()), 1)

    def test_getOpDependentsRecurse(self):
        node = OBJ.node("test_getOpDependents/subnet1")

        self.assertEqual(len(node.getOpDependents()), 0)

        self.assertEqual(len(node.getOpDependents(True)), 1)

    def test_creationTime(self):
        ts = datetime.datetime.now().strftime("%d %m %y %H:%M")
        date = datetime.datetime.strptime(ts, "%d %m %y %H:%M")

        node = OBJ.createNode("geo")

        self.assertEqual(date, node.creationTime())

    def test_modifiedTime(self):
        # TODO Figure out a way to test this that doesn't break randomly.
        pass

    def test_typeSetIcon(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        nodeType.setIcon("SOP_box")

        self.assertEqual(nodeType.icon(), "SOP_box")

    def test_typeSetDefaultIcon(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        nodeType.setIcon("SOP_box")

        nodeType.setDefaultIcon()

        self.assertEqual(nodeType.icon(), "OBJ_geo")

    def test_typeIsPython(self):
        nodeType = hou.nodeType(hou.sopNodeTypeCategory(), "tableimport")

        self.assertTrue(nodeType.isPython())

    def test_typeIsNotPython(self):
        nodeType = hou.nodeType(hou.sopNodeTypeCategory(), "file")

        self.assertFalse(nodeType.isPython())

    def test_typeIsSubnet(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "subnet")

        self.assertTrue(nodeType.isSubnetType())

    def test_typeIsNotSubnet(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")

        self.assertFalse(nodeType.isSubnetType())

    def test_v3ComponentAlong(self):
        v3 = hou.Vector3(1, 2, 3)
        self.assertEqual(
            v3.componentAlong(hou.Vector3(0, 0, 15)),
            3.0
        )

    def test_v3Project(self):
        v3 = hou.Vector3(-1.3, 0.5, 7.6)
        proj = v3.project(hou.Vector3(2.87, 3.1, -0.5))

        result = hou.Vector3(-0.948531, -1.02455, 0.165249)

        self.assertTrue(proj.isAlmostEqual(result))

    def test_v2IsNan(self):
        nan = float('nan')
        v2 = hou.Vector2(nan, 1)

        self.assertTrue(v2.isNan())

    def test_v3IsNan(self):
        nan = float('nan')
        v3 = hou.Vector3(6.5, 1, nan)

        self.assertTrue(v3.isNan())

    def test_v3IsNan(self):
        nan = float('nan')
        v4 = hou.Vector4(-4, 5, -0, nan)

        self.assertTrue(v4.isNan())

    def test_getDual(self):
        TARGET = hou.Matrix3(((0, -3, 2), (3, 0, -1), (-2, 1, 0)))

        v3 = hou.Vector3(1, 2, 3)

        self.assertEqual(v3.getDual(), TARGET)

    def test_m3IdentIsIdentity(self):
        m3 = hou.Matrix3()
        m3.setToIdentity()

        self.assertTrue(m3.isIdentity())

    def test_m3ZeroIsNotIdentity(self):
        m3 = hou.Matrix3()

        self.assertFalse(m3.isIdentity())

    def test_m4IdentIsIdentity(self):
        m4 = hou.Matrix4()
        m4.setToIdentity()

        self.assertTrue(m4.isIdentity())

    def test_m4ZeroIsNotIdentity(self):
        m4 = hou.Matrix4()

        self.assertFalse(m4.isIdentity())

    def test_m4SetTranslates(self):
        translates = hou.Vector3(1,2,3)
        identity = hou.hmath.identityTransform()
        identity.setTranslates(translates)

        self.assertEqual(
            identity.extractTranslates(),
            translates
        )

    def test_buildLookat(self):
        TARGET = hou.Matrix3(
            (
                (0.70710678118654746, -0.0, 0.70710678118654746),
                (0.0, 1.0, 0.0),
                (-0.70710678118654746, 0.0, 0.70710678118654746)
            )
        )

        lookAt = hou.hmath.buildLookat(
            hou.Vector3(0, 0, 1),
            hou.Vector3(1, 0, 0),
            hou.Vector3(0, 1, 0)
        )

        self.assertEqual(lookAt, TARGET)

    def test_buildInstance(self):
        TARGET = hou.Matrix4(
            (
                (
                    1.0606601717798214,
                    -1.0606601717798214,
                    0.0,
                    0.0
                ),
                (
                    0.61237243569579436,
                    0.61237243569579436,
                    -1.2247448713915889,
                    0.0
                ),
                (
                    0.86602540378443882,
                    0.86602540378443882,
                    0.86602540378443882,
                    0.0
                ),
                (
                    -1.0,
                    2.0,
                    4.0,
                    1.0
                )
            )
        )

        mat = hou.hmath.buildInstance(
            hou.Vector3(-1, 2, 4),
            hou.Vector3(1, 1, 1),
            pscale = 1.5,
            up=hou.Vector3(1, 1, -1)
        )

        self.assertEqual(mat, TARGET)

    def test_buildInstanceOrient(self):
        TARGET = hou.Matrix4(
            (
                (
                    0.33212996389891691,
                    0.3465703971119134,
                    -0.87725631768953083,
                    0.0
                ),
                (
                    -0.53068592057761732,
                    0.83754512635379064,
                    0.1299638989169675,
                    0.0
                ),
                (
                    0.77978339350180514,
                    0.42238267148014441,
                    0.46209386281588438,
                    0.0
                ),
                (
                    -1.0,
                    2.0,
                    4.0,
                    1.0
                )
            )
        )

        mat = hou.hmath.buildInstance(
            hou.Vector3(-1, 2, 4),
            orient=hou.Quaternion(0.3, -1.7, -0.9, -2.7)
        )

        self.assertEqual(mat, TARGET)

    def test_isDigitalAsset(self):
        self.assertTrue(OBJ.node("test_isDigitalAsset").isDigitalAsset())

    def test_isNotDigitalAsset(self):
        self.assertFalse(OBJ.node("test_isNotDigitalAsset").isDigitalAsset())

    def test_canCreateDigitalAsset(self):
        self.assertTrue(
            OBJ.node("test_canCreateDigitalAsset").canCreateDigitalAsset()
        )
    def test_cantCreateDigitalAsset(self):
        self.assertFalse(
            OBJ.node("test_cantCreateDigitalAsset").canCreateDigitalAsset()
        )

    def test_metaSource(self):
        TARGET = "Scanned OTL Directories"
        path = hou.expandString("$HH/otls/OPlibSop.otl")

        self.assertEqual(hou.hda.metaSource(path), TARGET)

    def test_getMetaSource(self):
        TARGET = "Scanned OTL Directories"

        node_type = hou.nodeType(hou.sopNodeTypeCategory(), "explodedview")

        self.assertEqual(node_type.definition().metaSource(), TARGET)

    def test_removeMetaSource(self):
        libs = hou.hda.librariesInMetaSource("Current HIP File")

        num_libs = len(libs)
        self.assertTrue(num_libs > 0)

        hou.hda.removeMetaSource("Current HIP File")

        libs = hou.hda.librariesInMetaSource("Current HIP File")
        self.assertTrue(len(libs) < num_libs)

    def test_librariesInMetaSource(self):
        libs = hou.hda.librariesInMetaSource("Scanned OTL Directories")
        self.assertTrue(len(libs) > 0)

    def test_isDummy(self):
        geo = OBJ.createNode("geo")
        subnet = geo.createNode("subnet")

        # Create a new digital asset.
        asset = subnet.createDigitalAsset("dummyop", "Embedded", "Dummy")
        node_type = asset.type()

        # Not a dummy so far.
        self.assertFalse(node_type.definition().isDummy())

        # Destroy the definition.
        node_type.definition().destroy()

        # Now it's a dummy.
        self.assertTrue(node_type.definition().isDummy())

        # Destroy the instance.
        asset.destroy()

        # Destroy the dummy definition.
        node_type.definition().destroy()

if __name__ == '__main__':
    # Load the testing hip file.
    try:
        hou.hipFile.load("test_inline.hip")

    # Catch any load warnings and ignore.
    except hou.LoadWarning:
        pass

    # Run the tests.
    unittest.main()

