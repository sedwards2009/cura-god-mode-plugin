# Copyright (c) 2016 Ultimaker B.V.
# This code is released under the terms of the AGPLv3 or higher.
from UM.Resources import Resources

from UM.View.View import View
from UM.View.GL.OpenGL import OpenGL
from UM.View.Renderer import Renderer

from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.Mesh.MeshBuilder import MeshBuilder

from UM.Math.Color import Color
from UM.Math.Vector import Vector


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
                    renderer.queueNode(scene.getRoot(), mesh=self._getAxisMesh(node))
                    renderer.queueNode(node, shader = self._shader, transparent = True)

                # We also want to draw the axis for group nodes.
                if node.callDecoration("isGroup"):
                    renderer.queueNode(scene.getRoot(), mesh=self._getAxisMesh(node))
                    renderer.queueNode(scene.getRoot(), mesh=node.getBoundingBoxMesh(), mode=Renderer.RenderLines)


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

