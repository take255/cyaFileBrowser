# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import imp
import utils


from bpy.types import(
    AddonPreferences
    )


from bpy.props import(
    StringProperty,
    )

bl_info = {
"name": "cyaFileBrowser",
"author": "Takehito Tsuchiya",
"version": (0, 01),
"blender": (2, 93, 5),
"location" : "CYA",
"description": "File Browser",
"category": "Object"}

# LIBPATH = r"E:\data\OneDrive\projects\_lib\Blender"
# ADDONPATH =r"G:\共有ドライブ\fs_yakushi\Art\Character\Library\Blender_Addon\cyatools.ZIP"

#---------------------------------------------------------------------------------------
#UI
#---------------------------------------------------------------------------------------
class CYAFILEBROWSER_PT_Main(utils.panel):
    bl_label ='SUB Tools'
    bl_category = "CYA"
    bl_idname = "CYAFILEBROWSER_PT_Main"
    #bl_space_type = "NODE_EDITOR"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        #props = bpy.context.scene.cyatoolssub_oa
        layout=self.layout

        box = layout.box()
        box.label( text = 'display toggle' )

        # row1 = box.row()
        # box2 = row1.box()

        # row2 = box2.row()
        # row2.prop(props, "const_bool" , icon='CONSTRAINT')#コンストレインのON、OFF
        # row2.prop(props, "showhide_bool" , icon='EMPTY_DATA')#選択した子供のみ表示


        # box2.prop(props, "focus_bool")


        # box1 = row1.box()
        # box1.label( text = 'collection' )

        # row1 = box1.row()
        # row1.prop(props, "showhide_collection_bool" , icon='GROUP')
        # row1.operator( "cyatoolssub.preserve_collections" , icon = 'IMPORT')
        # row1.operator( "cyatoolssub.collections_hide" )

        # #CC3パイプラインツール
        # box = layout.box()
        # box.label( text = 'CC3 pipeline' )
        # row1 = box.row()

        # row1.operator( "cyatoolssub.collect_textures" )
        # row1.operator( "cyatoolssub.save_textures" )
        # row1.operator( "cyatoolssub.save_uv" )
        # row1.operator( "cyatoolssub.load_uv" )


classes = (
    CYAFILEBROWSER_PT_Main,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

