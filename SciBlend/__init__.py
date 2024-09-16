import bpy
import os
import bpy.utils.previews

from .operators.import_operators import ImportStaticX3DOperator, ImportX3DAnimationOperator, ImportVTKAnimationOperator
from .operators.material_operators import CreateSharedMaterialOperator, ApplySharedMaterialOperator, RemoveAllShadersOperator
from .operators.object_operators import (
    CreateNullOperator, ParentNullToGeoOperator, NullToOriginOperator, CreateSceneOperator,
    BooleanCutterOperator, BooleanCutterHideOperator,
    AddMeshCutterOperator, GroupObjectsOperator, DeleteHierarchyOperator
)

preview_collection = None

class X3DImportSettings(bpy.types.PropertyGroup):
    scale_factor: bpy.props.FloatProperty(
        name="Scale Factor",
        description="Scale factor for imported objects",
        default=1.0,
        min=0.01,
        max=100.0
    )
    axis_forward: bpy.props.EnumProperty(
        name="Forward",
        items=[
            ('X', "X Forward", ""),
            ('Y', "Y Forward", ""),
            ('Z', "Z Forward", ""),
            ('-X', "-X Forward", ""),
            ('-Y', "-Y Forward", ""),
            ('-Z', "-Z Forward", ""),
        ],
        default='Y',
    )
    axis_up: bpy.props.EnumProperty(
        name="Up",
        items=[
            ('X', "X Up", ""),
            ('Y', "Y Up", ""),
            ('Z', "Z Up", ""),
            ('-X', "-X Up", ""),
            ('-Y', "-Y Up", ""),
            ('-Z', "-Z Up", ""),
        ],
        default='Z',
    )
    shared_material: bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Shared Material"
    )
    start_frame_number: bpy.props.IntProperty(
        name="Start Frame",
        description="Start frame for animation import",
        default=1,
        min=1
    )
    end_frame_number: bpy.props.IntProperty(
        name="End Frame",
        description="End frame for animation import",
        default=100,
        min=1
    )

class SciBlendPanel(bpy.types.Panel):
    bl_label = "SciBlend"
    bl_idname = "OBJECT_PT_sciblend"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SciBlend'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.x3d_import_settings

        box = layout.box()
        box.label(text="Import", icon='IMPORT')
        box.operator("import_x3d.static", text="Import Static X3D", icon='IMPORT')
        box.operator("import_x3d.animation", text="Import X3D Animation", icon='SEQUENCE')
        box.operator("import_vtk.animation", text="Import VTK Animation", icon='SEQUENCE')

        box = layout.box()
        box.label(text="Settings", icon='SETTINGS')
        box.prop(settings, "scale_factor")
        box.prop(settings, "axis_forward")
        box.prop(settings, "axis_up")
        box.prop(settings, "start_frame_number")
        box.prop(settings, "end_frame_number")

        box = layout.box()
        box.label(text="Material", icon='MATERIAL')
        box.prop(settings, "shared_material")
        box.operator("import_x3d.create_shared_material", text="New Global Material", icon='ADD')
        box.operator("import_x3d.apply_shared_material", text="Apply Shared Material", icon='CHECKMARK')
        box.operator("import_x3d.remove_all_shaders", text="Remove All Shaders", icon='X')

        box = layout.box()
        box.label(text="Object Operations", icon='OBJECT_DATAMODE')
        box.operator("import_x3d.create_null", text="Create Null", icon='EMPTY_AXIS')
        box.operator("import_x3d.parent_null_to_geo", text="Parent Null to Geo", icon='OBJECT_DATAMODE')
        box.operator("import_x3d.null_to_origin", text="Null to Origin", icon='EMPTY_AXIS')
        box.operator("object.center_null_to_origin", text="Center Null to Origin", icon='EMPTY_AXIS')
        box.operator("object.group_objects", text="Group Objects", icon='GROUP')

        box = layout.box()
        box.label(text="Render Presets", icon='RENDER_STILL')
        box.operator("object.create_scene", text="Create Scene", icon='SCENE_DATA')

        box = layout.box()
        box.label(text="Boolean Operations", icon='MOD_BOOLEAN')
        box.prop(context.scene, "new_cutter_mesh", text="New Boolean")
        box.operator("object.add_mesh_cutter_operator", text="Add Boolean", icon='ADD')
        box.operator("object.boolean_cutter_operator", text="Apply Boolean", icon='MOD_BOOLEAN')
        box.operator("object.boolean_cutter_hide_operator", text="Hide Boolean", icon='HIDE_ON')

        box = layout.box()
        box.label(text="Organize Geometry", icon='OUTLINER')
        
        row = box.row()
        row.prop(context.scene, "group_type", text="")
        row.operator("object.group_objects", text="Group Objects", icon='GROUP')
        
        box.operator("object.delete_hierarchy", text="Delete Hierarchy", icon='X')

classes = (
    ImportStaticX3DOperator,
    ImportX3DAnimationOperator,
    ImportVTKAnimationOperator,  
    CreateSharedMaterialOperator,
    ApplySharedMaterialOperator,
    RemoveAllShadersOperator,
    CreateNullOperator,
    ParentNullToGeoOperator,
    NullToOriginOperator,
    CreateSceneOperator,
    X3DImportSettings,
    SciBlendPanel,
    BooleanCutterOperator,
    BooleanCutterHideOperator,
    AddMeshCutterOperator,
    GroupObjectsOperator,
    DeleteHierarchyOperator,
)

def register():
    global preview_collection
    preview_collection = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    preview_collection.load("custom_icon", os.path.join(icons_dir, "logo.png"), 'IMAGE')

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.x3d_import_settings = bpy.props.PointerProperty(type=X3DImportSettings)
    bpy.types.Scene.boolean_cutter_object = bpy.props.StringProperty(name="Boolean Cutter Object")
    bpy.types.Scene.new_cutter_mesh = bpy.props.EnumProperty(
        name="New Boolean",
        items=[
            ("CUBE", "Cube", "Add a cube"),
            ("SPHERE", "Sphere", "Add a sphere"),
            ("CYLINDER", "Cylinder", "Add a cylinder"),
            ("CONE", "Cone", "Add a cone"),
            ("TORUS", "Torus", "Add a torus")
        ]
    )
    bpy.types.Scene.group_type = bpy.props.EnumProperty(
        name="Group Type",
        items=[
            ('MESHES', "Meshes", "Group all mesh objects"),
            ('CAMERAS', "Cameras", "Group all camera objects"),
            ('LIGHTS', "Lights", "Group all light objects"),
            ('ALL', "All", "Group all objects"),
        ],
        default='MESHES'
    )

def unregister():
    global preview_collection
    bpy.utils.previews.remove(preview_collection)

    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.x3d_import_settings
    del bpy.types.Scene.boolean_cutter_object
    del bpy.types.Scene.new_cutter_mesh
    del bpy.types.Scene.group_type

if __name__ == "__main__":
    register()

bl_info = {
    "name": "SciBlend",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > SciBlend",
    "description": "Scientific visualization tools for Blender",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
