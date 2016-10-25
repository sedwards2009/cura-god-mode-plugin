# Copyright (c) 2016 Ultimaker B.V.
# This code is released under the terms of the AGPLv3 or higher.
from UM.Math.Color import Color
from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Resources import Resources
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator
from UM.View.GL.OpenGL import OpenGL
from UM.View.Renderer import Renderer
from UM.View.View import View
from .BillboardDecorator import BillboardDecorator

import re

import numpy


##  The godview shows debug information about the scene and it's nodes.
class GodView(View):
    XAxisColor = Color(1.0, 0.0, 0.0, 1.0)
    YAxisColor = Color(0.0, 0.0, 1.0, 1.0)
    ZAxisColor = Color(0.0, 1.0, 0.0, 1.0)

    axis_width = 0.5
    axis_height = 20

    def __init__(self):
        super().__init__()
        self._shader = None

    def beginRendering(self):
        # Convenience setup
        scene = self.getController().getScene()
        renderer = self.getRenderer()

        if not self._shader:
            self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "color.shader"))
            self._shader.setUniformValue("u_color", Color(32, 32, 32, 170))

        for node in DepthFirstIterator(scene.getRoot()):
            if not node.render(renderer):
                # For now we only render nodes that indicate that they need rendering.
                if node.getMeshData():
                    # Render origin of this node.
                    renderer.queueNode(scene.getRoot(), mesh = self._getAxisMesh(node))

                    # Render transparent MeshData
                    renderer.queueNode(node, shader = self._shader, transparent = True)

                    # Check if node already has a billboard node. If not, add it.
                    billboard_node = node.callDecoration("getBillboard")
                    if not billboard_node:
                        billboard_decorator = BillboardDecorator()
                        node.addDecorator(billboard_decorator)
                        billboard_node = billboard_decorator.getBillboard()
                        billboard_node.setTemplate("<html><H1>{name}</H1> {matrix}</html>")

                    # Update the displayed data on the billboard.
                    data = self._matrixToHtml(node.getWorldTransformation())
                    billboard_node.setDisplayData({"name": node.getName(), "matrix": data})

                # Handle group nodes
                if node.callDecoration("isGroup"):
                    # Render origin of this node.
                    renderer.queueNode(scene.getRoot(), mesh=self._getAxisMesh(node))
                    # Render bounding box of this node
                    renderer.queueNode(scene.getRoot(), mesh=node.getBoundingBoxMesh(), mode=Renderer.RenderLines)

    def _matrixToHtml(self, matrix):
        data = re.sub('[\[\]]', '', numpy.array_str(matrix.getData()))
        data = data.replace("\n", "<br>")
        return data

    def endRendering(self):
        pass

    def _getAxisMesh(self, node):
        mb = MeshBuilder()
        mb.addCube(
            width=self.axis_width,
            height=self.axis_height,
            depth=self.axis_width,
            color=self.YAxisColor,
            center = Vector(0, self.axis_height / 2, 0)
        )
        mb.addCube(
            width=self.axis_width,
            height=self.axis_width,
            depth=self.axis_height,
            color=self.ZAxisColor,
            center=Vector(0, 0, self.axis_height / 2)
        )
        mb.addCube(
            width=self.axis_height,
            height=self.axis_width,
            depth=self.axis_width,
            color=self.XAxisColor,
            center=Vector(self.axis_height / 2, 0, 0)
        )
        return mb.build().getTransformed(node.getWorldTransformation())

