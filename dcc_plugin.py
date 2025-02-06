bl_info = {
    "name": "DCC Integration Plugin",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > DCC Plugin",
    "description": "Send object transforms to a local server",
    "category": "Development",
}

import bpy
import requests

# Define available endpoints
ENDPOINTS = [
    ("transform", "All Transforms", "Send position, rotation, and scale"),
    ("translation", "Position Only", "Send only position data"),
    ("rotation", "Rotation Only", "Send only rotation data"),
    ("scale", "Scale Only", "Send only scale data"),
    ("file-path", "File Path", "Return the file/project path"),
]

# Operator to submit the data to the server
class OBJECT_OT_SendTransform(bpy.types.Operator):
    bl_idname = "object.send_transform"
    bl_label = "Submit Transform"
    bl_description = "Send the selected object's transform data to the server"

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object selected.")
            return {'CANCELLED'}
        
        # Retrieve transform data
        transform_data = {
            "position": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
        }
        
        # Determine selected endpoint from the UI property
        endpoint = context.scene.dcc_plugin_endpoint

        # Build the URL (adjust the host/port as necessary)
        url = f"http://localhost:5000/{endpoint}"
        
        try:
            response = requests.post(url, json=transform_data)
            self.report({'INFO'}, f"Server responded with status code: {response.status_code}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to connect to server: {e}")
        
        return {'FINISHED'}

# UI Panel for the plugin
class DCC_PT_PluginPanel(bpy.types.Panel):
    bl_label = "DCC Plugin"
    bl_idname = "DCC_PT_plugin_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DCC Plugin'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        # Object selection & display of transform controls
        if obj:
            layout.label(text=f"Selected: {obj.name}")
            col = layout.column(align=True)
            col.prop(obj, "location", text="Position")
            col.prop(obj, "rotation_euler", text="Rotation")
            col.prop(obj, "scale", text="Scale")
        else:
            layout.label(text="No active object selected.")

        # Dropdown to select the endpoint
        layout.prop(context.scene, "dcc_plugin_endpoint", text="Server Endpoint")

        # Submit button
        layout.operator("object.send_transform")

# Register properties, classes, and add the addon to Blender
def register():
    bpy.utils.register_class(OBJECT_OT_SendTransform)
    bpy.utils.register_class(DCC_PT_PluginPanel)
    bpy.types.Scene.dcc_plugin_endpoint = bpy.props.EnumProperty(
        name="Endpoint",
        description="Select server function to use",
        items=ENDPOINTS,
        default="transform",
    )

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_SendTransform)
    bpy.utils.unregister_class(DCC_PT_PluginPanel)
    del bpy.types.Scene.dcc_plugin_endpoint

if __name__ == "__main__":
    register()
