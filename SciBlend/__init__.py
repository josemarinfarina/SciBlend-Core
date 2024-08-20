import bpy
import os
import math
import mathutils
from bpy_extras.io_utils import ImportHelper
import bpy.utils.previews

preview_collection = None


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

        if bpy.context.scene.animation_data and bpy.context.scene.animation_data.action:
            for fcurve in bpy.context.scene.animation_data.action.fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'CONSTANT'

        self.report({'INFO'}, "Import and configuration completed.")
        return {'FINISHED'}


class CreateSharedMaterialOperator(bpy.types.Operator):
    bl_idname = "import_x3d.create_shared_material"
    bl_label = "New Global Material"

    def execute(self, context):
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

        links.new(attribute_node.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])

        context.scene.x3d_import_settings.shared_material = material

        self.report({'INFO'}, "Shared material created and assigned.")
        return {'FINISHED'}


class ApplySharedMaterialOperator(bpy.types.Operator):
    bl_idname = "import_x3d.apply_shared_material"
    bl_label = "Apply Shared Material"

    def execute(self, context):
        material = context.scene.x3d_import_settings.shared_material
        if material is None:
            self.report({'ERROR'}, "No material selected.")
            return {'CANCELLED'}

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj.data.materials.clear()
                obj.data.materials.append(material)

        self.report({'INFO'}, "Material applied to all meshes.")
        return {'FINISHED'}


class RemoveAllShadersOperator(bpy.types.Operator):
    bl_idname = "import_x3d.remove_all_shaders"
    bl_label = "Remove All Shaders"

    def execute(self, context):
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)

        self.report({'INFO'}, "All shaders removed.")
        return {'FINISHED'}


class CreateNullOperator(bpy.types.Operator):
    bl_idname = "import_x3d.create_null"
    bl_label = "Create Null"

    null_type: bpy.props.EnumProperty(
        name="Null Type",
        description="Type of null object to create",
        items=[
            ('PLAIN_AXES', "Plain Axes", ""),
            ('ARROWS', "Arrows", ""),
            ('SINGLE_ARROW', "Single Arrow", ""),
            ('CIRCLE', "Circle", ""),
            ('CUBE', "Cube", ""),
            ('SPHERE', "Sphere", ""),
            ('CONE', "Cone", ""),
            ('IMAGE', "Image", "")
        ],
        default='PLAIN_AXES'
    )

    def execute(self, context):
        bpy.ops.object.empty_add(type=self.null_type)
        self.report({'INFO'}, f"Null of type {self.null_type} created.")
        return {'FINISHED'}


class ParentNullToGeoOperator(bpy.types.Operator):
    bl_idname = "import_x3d.parent_null_to_geo"
    bl_label = "Parent Null to Geo"

    def execute(self, context):
        null_object = next(
            (obj for obj in bpy.context.scene.objects if obj.type == 'EMPTY'), None)

        if not null_object:
            self.report({'ERROR'}, "No null object found.")
            return {'CANCELLED'}

        original_states = {obj: (obj.hide_viewport, obj.hide_render)
                           for obj in bpy.context.scene.objects}

        for obj in bpy.context.scene.objects:
            obj.hide_viewport = False
            obj.hide_render = False

        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj != null_object:
                obj.select_set(True)

        bpy.context.view_layer.objects.active = null_object
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        for obj, (hide_viewport, hide_render) in original_states.items():
            obj.hide_viewport = hide_viewport
            obj.hide_render = hide_render

        self.report({'INFO'}, "Null parented to all geometry.")
        return {'FINISHED'}


class NullToOriginOperator(bpy.types.Operator):
    bl_idname = "import_x3d.null_to_origin"
    bl_label = "Null to Origin"

    def execute(self, context):
        null_object = next(
            (obj for obj in bpy.context.scene.objects if obj.type == 'EMPTY'), None)

        if not null_object:
            self.report({'ERROR'}, "No null object found.")
            return {'CANCELLED'}

        null_object.location = (0, 0, 0)
        self.report({'INFO'}, "Null moved to origin.")
        return {'FINISHED'}


class CreateSceneOperator(bpy.types.Operator):
    bl_idname = "object.create_scene"
    bl_label = "Scene 1"

    def execute(self, context):
        bpy.ops.object.light_add(type='SUN')
        sun = bpy.context.object
        sun.data.energy = 2.0
        sun.rotation_euler = (math.radians(180), 0, 0)

        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("World")
            bpy.context.scene.world = world
        world.use_nodes = False
        world.color = (0, 0, 0)

        bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        bpy.context.scene.use_nodes = True

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'RENDERED'
                        space.shading.use_scene_lights = True
                        space.shading.use_scene_world = True

        bpy.context.space_data.shading.type = 'RENDERED'
        bpy.context.space_data.shading.use_compositor = 'ALWAYS'

        self.report({'INFO'}, "Scene 1 created with sun and EEVEE settings.")
        return {'FINISHED'}


class X3DImportSettings(bpy.types.PropertyGroup):
    start_frame_number: bpy.props.IntProperty(
        name="Start Frame Number",
        description="Number of the first X3D file to import",
        default=1,
        min=1
    )
    end_frame_number: bpy.props.IntProperty(
        name="End Frame Number",
        description="Number of the last X3D file to import",
        default=10,
        min=1
    )
    axis_forward: bpy.props.EnumProperty(
        name="Forward Axis",
        description="Axis that faces forward",
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", "")
        ],
        default='-Z'
    )
    axis_up: bpy.props.EnumProperty(
        name="Up Axis",
        description="Axis that faces up",
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", "")
        ],
        default='Z'
    )
    scale_factor: bpy.props.FloatProperty(
        name="Scale Factor",
        description="Scale factor for imported objects",
        default=1.0,
        min=0.01,
        max=100.0
    )
    shared_material: bpy.props.PointerProperty(
        name="Shared Material",
        type=bpy.types.Material
    )
    null_type: bpy.props.EnumProperty(
        name="Null Type",
        description="Type of null object to create",
        items=[
            ('PLAIN_AXES', "Plain Axes", ""),
            ('ARROWS', "Arrows", ""),
            ('SINGLE_ARROW', "Single Arrow", ""),
            ('CIRCLE', "Circle", ""),
            ('CUBE', "Cube", ""),
            ('SPHERE', "Sphere", ""),
            ('CONE', "Cone", ""),
            ('IMAGE', "Image", "")
        ],
        default='PLAIN_AXES'
    )


class SciBlenderPanel(bpy.types.Panel):
    bl_label = "SciBlend"
    bl_idname = "OBJECT_PT_sci_blender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SciBlend'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        settings = scene.x3d_import_settings

        layout.label(text="Import Static", icon='IMPORT')
        box = layout.box()
        box.operator("import_x3d.static",
                     text="Import Static", icon='FILE_BLEND')

        layout.separator()

        layout.label(text="Import Animation", icon='IMPORT')
        box = layout.box()
        box.prop(settings, "start_frame_number")
        box.prop(settings, "end_frame_number")
        box.prop(settings, "axis_forward")
        box.prop(settings, "axis_up")
        box.prop(settings, "scale_factor")
        box.operator("import_x3d.animation",
                     text="Import Animation", icon='FILE_BLEND')

        layout.separator()

        layout.label(text="Material Management", icon='MATERIAL')
        box = layout.box()
        box.operator("import_x3d.create_shared_material",
                     text="New Global Material", icon='ADD')
        box.prop(settings, "shared_material")
        box.operator("import_x3d.apply_shared_material",
                     text="Apply Shared Material", icon='CHECKMARK')
        box.operator("import_x3d.remove_all_shaders",
                     text="Remove All Shaders", icon='X')

        layout.separator()

        layout.label(text="Object Management", icon='OBJECT_DATAMODE')
        box = layout.box()
        box.operator("object.group_objects",
                     text="Group Cameras").group_type = 'CAMERAS'
        box.operator("object.group_objects",
                     text="Group Lights").group_type = 'LIGHTS'
        box.operator("object.group_objects",
                     text="Group Meshes").group_type = 'MESHES'
        box.operator("object.group_objects",
                     text="Group All Objects").group_type = 'ALL'

        layout.separator()

        layout.label(text="Null Operations", icon='EMPTY_AXIS')
        box = layout.box()
        box.prop(settings, "null_type", text="Null Type")
        box.operator("import_x3d.create_null",
                     text="Create Null", icon='EMPTY_AXIS')
        box.operator("import_x3d.parent_null_to_geo",
                     text="Parent Null to Geo", icon='CONSTRAINT_BONE')
        box.operator("import_x3d.null_to_origin",
                     text="Null to Origin", icon='OBJECT_ORIGIN')

        layout.separator()

        layout.label(text="Rendering", icon='RENDER_STILL')
        box = layout.box()
        box.operator("object.create_scene", text="Scene 1", icon='WORLD_DATA')

        layout.separator()

        layout.label(text="Dynamic Boolean Cutter", icon='MOD_BOOLEAN')
        box = layout.box()
        box.prop(context.scene, "new_cutter_mesh", text="New Boolean")
        box.operator("object.add_mesh_cutter_operator", text="Add Boolean",
                     icon='MESH_CUBE').mesh_type = context.scene.new_cutter_mesh
        box.prop_search(context.scene, "boolean_cutter_object",
                        bpy.data, "objects", text="Cutter Object")
        box.operator("object.boolean_cutter_operator",
                     text="Apply Boolean", icon='MOD_BOOLEAN')
        box.operator("object.boolean_cutter_hide_operator",
                     text="Hide Boolean", icon='HIDE_OFF')


class GroupObjectsOperator(bpy.types.Operator):
    bl_idname = "object.group_objects"
    bl_label = "Group Objects"

    group_type: bpy.props.EnumProperty(
        name="Group Type",
        description="Type of objects to group",
        items=[
            ('CAMERAS', "Cameras", ""),
            ('LIGHTS', "Lights", ""),
            ('MESHES', "Meshes", ""),
            ('ALL', "All", "")
        ],
        default='ALL'
    )

    def execute(self, context):
        if self.group_type == 'CAMERAS':
            group_name = "Cameras"
            objects = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
        elif self.group_type == 'LIGHTS':
            group_name = "Lights"
            objects = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']
        elif self.group_type == 'MESHES':
            group_name = "Meshes"
            objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        else:
            group_name = "AllObjects"
            objects = list(bpy.data.objects)

        if group_name not in bpy.data.collections:
            new_collection = bpy.data.collections.new(group_name)
            bpy.context.scene.collection.children.link(new_collection)
        else:
            new_collection = bpy.data.collections[group_name]

        for obj in objects:
            if obj.name not in new_collection.objects:
                new_collection.objects.link(obj)

        self.report({'INFO'}, f"{self.group_type} grouped successfully.")
        return {'FINISHED'}


class BooleanCutterOperator(bpy.types.Operator):
    bl_idname = "object.boolean_cutter_operator"
    bl_label = "Apply Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cutter_name = context.scene.boolean_cutter_object
        cutter = bpy.data.objects.get(cutter_name)
        if not cutter:
            self.report({'ERROR'}, f"Object named {cutter_name} not found")
            return {'CANCELLED'}

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and obj != cutter:
                bool_mod = obj.modifiers.get("Boolean")
                if not bool_mod:
                    bool_mod = obj.modifiers.new(
                        name="Boolean", type='BOOLEAN')
                bool_mod.operation = 'DIFFERENCE'
                bool_mod.object = cutter

        return {'FINISHED'}


class BooleanCutterHideOperator(bpy.types.Operator):
    bl_idname = "object.boolean_cutter_hide_operator"
    bl_label = "Hide Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cutter_name = context.scene.boolean_cutter_object
        cutter = bpy.data.objects.get(cutter_name)
        if cutter:
            cutter.hide_viewport = True
            cutter.hide_render = True
        else:
            self.report({'ERROR'}, f"Object named {cutter_name} not found")
            return {'CANCELLED'}

        return {'FINISHED'}


class AddMeshCutterOperator(bpy.types.Operator):
    bl_idname = "object.add_mesh_cutter_operator"
    bl_label = "Add Boolean"
    bl_options = {'REGISTER', 'UNDO'}

    mesh_type: bpy.props.EnumProperty(
        name="Mesh Type",
        description="Select a mesh to use as cutter",
        items=[
            ("CUBE", "Cube", "Add a cube"),
            ("SPHERE", "Sphere", "Add a sphere"),
            ("CYLINDER", "Cylinder", "Add a cylinder"),
            ("CONE", "Cone", "Add a cone"),
            ("TORUS", "Torus", "Add a torus")
        ]
    )

    def execute(self, context):
        mesh_type = self.mesh_type

        if mesh_type == 'CUBE':
            bpy.ops.mesh.primitive_cube_add()
        elif mesh_type == 'SPHERE':
            bpy.ops.mesh.primitive_uv_sphere_add()
        elif mesh_type == 'CYLINDER':
            bpy.ops.mesh.primitive_cylinder_add()
        elif mesh_type == 'CONE':
            bpy.ops.mesh.primitive_cone_add()
        elif mesh_type == 'TORUS':
            bpy.ops.mesh.primitive_torus_add()

        cutter = context.active_object
        context.scene.boolean_cutter_object = cutter.name

        return {'FINISHED'}


classes = (
    ImportStaticX3DOperator,
    ImportX3DAnimationOperator,
    CreateSharedMaterialOperator,
    ApplySharedMaterialOperator,
    RemoveAllShadersOperator,
    CreateNullOperator,
    ParentNullToGeoOperator,
    NullToOriginOperator,
    CreateSceneOperator,
    X3DImportSettings,
    SciBlenderPanel,
    GroupObjectsOperator,
    BooleanCutterOperator,
    BooleanCutterHideOperator,
    AddMeshCutterOperator,
)


def register():
    global preview_collection
    preview_collection = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    preview_collection.load("custom_icon", os.path.join(
        icons_dir, "logo.png"), 'IMAGE')

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.x3d_import_settings = bpy.props.PointerProperty(
        type=X3DImportSettings)
    bpy.types.Scene.boolean_cutter_object = bpy.props.StringProperty(
        name="Boolean Cutter Object")
    bpy.types.Scene.new_cutter_mesh = bpy.props.EnumProperty(
        name="New Boolean", items=[
            ("CUBE", "Cube", "Add a cube"),
            ("SPHERE", "Sphere", "Add a sphere"),
            ("CYLINDER", "Cylinder", "Add a cylinder"),
            ("CONE", "Cone", "Add a cone"),
            ("TORUS", "Torus", "Add a torus")
        ])


def unregister():
    global preview_collection
    bpy.utils.previews.remove(preview_collection)

    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.x3d_import_settings
    del bpy.types.Scene.boolean_cutter_object
    del bpy.types.Scene.new_cutter_mesh


if __name__ == "__main__":
    register()
