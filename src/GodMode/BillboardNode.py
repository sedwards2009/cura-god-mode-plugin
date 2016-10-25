# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.Scene.SceneNode import SceneNode

from UM.View.GL.OpenGL import OpenGL

from UM.Mesh.MeshBuilder import MeshBuilder  # To create the billboard quad

from UM.Resources import Resources  # To find shader locations

from UM.Math.Matrix import Matrix

from UM.Application import Application

from PyQt5.QtGui import QImage, QPainter, QColor, QFont, QTextDocument
from PyQt5.QtCore import Qt, QRectF

class BillboardNode(SceneNode):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self._target_node = node
        self.setCalculateBoundingBox(False)

        self._billboard_mesh = self._createBillboardQuad(50)

        self._shader = None
        self._scene = Application.getInstance().getController().getScene()
        self._template = ""
        self._display_data = {}
        self._texture_width = 256
        self._texture_height = 256

    def _createBillboardQuad(self, size):
        mb = MeshBuilder()
        mb.addFaceByPoints(-size / 2, -size / 2, 0, -size / 2, size / 2, 0, size / 2, -size / 2, 0)
        mb.addFaceByPoints(size / 2, size / 2, 0, -size / 2, size / 2, 0, size / 2, -size / 2, 0)

        # Set UV coordinates so a texture can be created
        mb.setVertexUVCoordinates(0, 0, 1)
        mb.setVertexUVCoordinates(1, 0, 0)
        mb.setVertexUVCoordinates(4, 0, 0)
        mb.setVertexUVCoordinates(2, 1, 1)
        mb.setVertexUVCoordinates(5, 1, 1)
        mb.setVertexUVCoordinates(3, 1, 0)

        return mb.build()

    def setTemplate(self, template):
        self._template = template
        self._shader = None  # Force update next render tick.

    def setDisplayData(self, display_data):
        self._display_data = display_data
        self._shader = None  # Force update next render tick.

    #   Convenience function to fill the billboard template with the data
    def _getFilledTemplate(self, display_data, template):
        filled_template = template
        for entry in display_data:
            filled_template = filled_template.replace("{%s}" % entry, display_data[entry])

        return filled_template

    def render(self, renderer):
        if not self._shader:
            # We now misuse the platform shader, as it actually supports textures
            self._shader = OpenGL.getInstance().createShaderProgram(Resources.getPath(Resources.Shaders, "platform.shader"))
            self._texture = OpenGL.getInstance().createTexture()
            document = QTextDocument()
            document.setHtml(self._getFilledTemplate(self._display_data, self._template))

            blarg = QImage(self._texture_width, self._texture_height, QImage.Format_ARGB32)
            blarg.fill(Qt.white)
            painter = QPainter(blarg)
            document.drawContents(painter, QRectF(0., 0., self._texture_width, self._texture_height))
            painter.end()
            self._texture.setImage(blarg)

            #self._texture.load(Resources.getPath(Resources.Images, "cura.png"))
            self._shader.setTexture(0, self._texture)

        node_position = self._target_node.getPosition()
        position_matrix = Matrix()
        position_matrix.setByTranslation(node_position)
        camera_orientation = self._scene.getActiveCamera().getOrientation().toMatrix()

        renderer.queueNode(self._scene.getRoot(), shader=self._shader, transparent=True, mesh=self._billboard_mesh.getTransformed(position_matrix.multiply(camera_orientation)), sort=-8)

        return True  # This node does it's own rendering.
