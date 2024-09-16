import bpy
import bmesh
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ImportStaticX3DOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_x3d.static"
    bl_label = "Import Static"
    filename_ext = ""

    def execute(self, context):
        settings = context.scene.x3d_import_settings
        directory = self.filepath
        file_path = os.path.join(directory, "tmpfile.x3d")
        scale_factor = settings.scale_factor

        if os.path.exists(file_path):
            bpy.ops.import_scene.x3d(filepath=file_path,
                                     axis_forward=settings.axis_forward,
                                     axis_up=settings.axis_up)
            for obj in bpy.context.selected_objects:
                obj.scale = (scale_factor, scale_factor, scale_factor)

            self.report({'INFO'}, f"File {file_path} successfully imported into Blender.")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"File {file_path} not found.")
            return {'CANCELLED'}

class ImportX3DAnimationOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "import_x3d.animation"
    bl_label = "Import Animation"
    filename_ext = ""

    def execute(self, context):
        settings = context.scene.x3d_import_settings
        scale_factor = settings.scale_factor
        start_frame = settings.start_frame_number
        end_frame = settings.end_frame_number
        num_frames = end_frame - start_frame + 1
        directory = os.path.dirname(self.filepath)

        x3d_files = [os.path.join(directory, f"tempfile{i}.x3d") for i in range(
            start_frame, end_frame + 1)]

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        material = settings.shared_material

        if material is None:
            material = bpy.data.materials.new(name="SharedMaterial")
            material.use_nodes = True
            nodes = material.node_tree.nodes
            links = material.node_tree.links

            for node in nodes:
                nodes.remove(node)

            attribute_node = nodes.new(type='ShaderNodeAttribute')
            attribute_node.attribute_name = 'Col'

            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')

            material_output = nodes.new(type='ShaderNodeOutputMaterial')

            links.new(
                attribute_node.outputs['Color'], bsdf.inputs['Base Color'])
            links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = num_frames

        for frame, x3d_file in enumerate(x3d_files, start=1):
            if os.path.exists(x3d_file):
                bpy.ops.import_scene.x3d(filepath=x3d_file,
                                         axis_forward=settings.axis_forward,
                                         axis_up=settings.axis_up)

                imported_objects = bpy.context.selected_objects

                for obj in imported_objects:
                    if obj.type == 'MESH':
                        obj.scale = (scale_factor, scale_factor, scale_factor)
                        obj.data.materials.clear()
                        obj.data.materials.append(material)

                    obj.hide_render = False
                    obj.hide_viewport = False
                    obj.keyframe_insert(data_path="hide_render", frame=frame)
                    obj.keyframe_insert(data_path="hide_viewport", frame=frame)

                    obj.hide_render = True
                    obj.hide_viewport = True
                    if frame > 1:
                        obj.keyframe_insert(
                            data_path="hide_render", frame=frame-1)
                        obj.keyframe_insert(
                            data_path="hide_viewport", frame=frame-1)
                    if frame < num_frames:
                        obj.keyframe_insert(
                            data_path="hide_render", frame=frame+1)
                        obj.keyframe_insert(
                            data_path="hide_viewport", frame=frame+1)
            else:
                self.report({'WARNING'}, f"File {x3d_file} not found.")

        # Configurar la interpolación de los keyframes a constante
        for obj in bpy.data.objects:
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'CONSTANT'

        self.report({'INFO'}, "Import and configuration completed.")
        return {'FINISHED'}