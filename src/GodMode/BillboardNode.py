# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode

from UM.View.GL.OpenGL import OpenGL

from UM.Mesh.MeshBuilder import MeshBuilder  # To create the billboard quad

from UM.Resources import Resources  # To find shader locations

from UM.Math.Color import Color
from UM.Math.Matrix import Matrix

from UM.Application import Application

class BillboardNode(SceneNode):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self._target_node = node
        self.setCalculateBoundingBox(False)
        mb = MeshBuilder()
        size = 50
        mb.addFaceByPoints(-size / 2, -size / 2, 0, -size / 2, size / 2, 0, size / 2, -size / 2, 0)
        mb.addFaceByPoints(size / 2, size / 2, 0, -size / 2, size / 2, 0, size / 2, -size / 2, 0)

        #mb.addCube(10,10,10)
        self._billboard_mesh = mb.build()
        self._color = Color(0.4, 0.4, 0.4, 1.0)
        self._shader = None
        self._scene = Application.getInstance().getController().getScene()

    def setText(self, text):
        pass

    def render(self, renderer):
        if not self._shader:
            self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "transparent_object.shader"))
            self._shader.setUniformValue("u_diffuseColor", self._color)
            self._shader.setUniformValue("u_opacity", 0.6)
        node_position = self._target_node.getPosition()
        position_matrix = Matrix()
        position_matrix.setByTranslation(node_position)
        camera_orientation = self._scene.getActiveCamera().getOrientation().toMatrix()

        renderer.queueNode(self._scene.getRoot(), shader=self._shader, transparent=True, mesh=self._billboard_mesh.getTransformed(position_matrix.multiply(camera_orientation)), sort=-8)

        return True  # This node does it's own rendering.
