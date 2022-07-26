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


bl_info = {
"name": "cyaFileBrowser",
"author": "Takehito Tsuchiya",
"version": (0, 0.1),
"blender": (2, 93, 5),
"location" : "CYA",
"description": "File Browser",
"category": "Object"}


#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------



from email.policy import default
import bpy
from bpy.types import ( PropertyGroup ,Operator, UIList)
import imp
import subprocess
from bpy.app.handlers import persistent

import json
import os

from bpy.props import(
    PointerProperty,
    IntProperty,
    StringProperty,
    CollectionProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty
    )

from . import utils
from . import cmd

imp.reload(utils)
imp.reload(cmd)


#---------------------------------------------------------------------------------------
#シーンが開かれたときと保存した時、自動でリロードする
#---------------------------------------------------------------------------------------
@persistent
def cyascenemanager_handler(dummy):

    cmd.setproject(1)


#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_Props_OA(PropertyGroup):
    copy_target : EnumProperty(items= (('work', '', '','EVENT_W',1),('backup', '', '','EVENT_B',2),('onedrive', '', '','EVENT_O',3)  ))
    switch_path : EnumProperty(items= (('work', '', '','EVENT_W',1),('backup', '', '','EVENT_B',2),('onedrive', '', '','EVENT_O',3)),update = cmd.switch_path)

    # copy_target : EnumProperty(items= (('svn', '', '','EVENT_S',0),('work', '', '','EVENT_W',1),('backup', '', '','EVENT_B',2),('onedrive', '', '','EVENT_O',3)  ))
    # switch_path : EnumProperty(items= (('svn', '', '','EVENT_S',0),('work', '', '','EVENT_W',1),('backup', '', '','EVENT_B',2),('onedrive', '', '','EVENT_O',3)),update = cmd.switch_path)


    #svn_root : StringProperty(name="svn root",  default=r'D:\Prj\B01\Assets' )
    work_root : StringProperty(name="work root", default= r'E:\data\project\YKS')
    backup_root : StringProperty(name="backup root", default= r'E:\data\project\YKSBuckup')
    onedrive_root : StringProperty(name="onedrive root", default= r'E:\data\OneDrive\projects\YKS')
    #gdrive_root : StringProperty(name="gdrive root", default= r'G:\共有ドライブ\fs_yakushi\Art')

    svn_dir : StringProperty(name="svn dir")
    work_dir : StringProperty(name="work dir")
    backup_dir : StringProperty(name="backup dir")
    onedrive_dir : StringProperty(name="onedrive dir")
    #gdrive_dir : StringProperty(name="gdrive dir")

    current_root :StringProperty(name="current root")
    relative_path :StringProperty(name="relative_path")


    #UI用プロパティ
    current_dir : StringProperty(name = "" , update = cmd.path_update)
    selected_file : StringProperty(name = "")
    add_work : BoolProperty(default=False)

    sortmode : StringProperty()
    root_Path : EnumProperty(items = cmd.update_rootpath , name = '')

    #Option
    import_obj_scale : FloatProperty(default=1.0 , name = 'import scale')
    import_obj_apply : BoolProperty( name = 'apply trans')

    #full_path :StringProperty(name="path")


#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_UL_uilist(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:


            layout.prop(item, "bool_val", text = "")


            #ファイルタイプによってアイコンを変える
            if item.filetype == 'blend':
                ic = 'FILE_BLEND'
                mode = item.filetype

            elif item.filetype == 'image':
                ic = 'FILE_IMAGE'
                mode = item.filetype

            elif item.filetype == 'dir':
                ic = 'FILE_FOLDER'
                mode = item.filetype

            elif item.filetype == 'fbx':
                ic = 'EVENT_F'
                mode = item.filetype

            elif item.filetype == 'obj':
                ic = 'EVENT_O'
                mode = item.filetype


            else:
                ic = 'FILE_BLANK'
                mode = 'file'


            l = layout.operator( "cyascenemanager.select_icon",text="", icon=ic, emboss=False)
            l.mode = mode
            l.name = item.name

            #layout.prop(item, "name", text="", emboss=False, icon_value=icon)
            #layout.prop(item, "date", text="", emboss=False)

            layout.prop(item, "name", text="", emboss=False, icon_value=icon)
            row = layout.row()
            row.alignment = 'RIGHT'
            row.prop(item, "date", text="", emboss=False)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_PT_scenemanager(utils.panel):
    bl_label ='File Browser'
    bl_category = "CYA"
    bl_idname = "CYAFILEBROWSER_PT_Main"
    #bl_space_type = "NODE_EDITOR"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        ui_list = context.window_manager.cyascenemanager_list
        prop = bpy.context.scene.cyascenemanager_oa

        layout=self.layout

        row = layout.row(align=False)
        col = row.column()

        box = col.box()
        row = box.row()
        row.operator("cyascenemanager.go_up_dir", text = '' , icon= 'FILE_PARENT')
        row.operator("cyascenemanager.open_file", icon = 'FILE')
        row.operator("cyascenemanager.open_explorer", text = '' , icon= 'FILE_FOLDER')
        row.operator("cyascenemanager.reload" , icon  ='FILE_REFRESH' ).mode=0
        row.operator("cyascenemanager.reload" , icon  ='HOME' ).mode=1

        row.prop(prop,"switch_path", expand=True)
        row.operator("cyascenemanager.copytools", icon='COPYDOWN')


        col = box.column()
        #col.prop(props, "modifier_type" , icon='RESTRICT_VIEW_OFF')

        row1 = col.row()
        row1.prop(prop,"root_Path")
        row1.operator("cyascenemanager.reload_rootpath" , icon  ='HOME' )


        col.prop(prop,"current_dir")

        row = col.row()
        row.template_list("CYASCENEMANAGER_UL_uilist", "", ui_list, "itemlist", ui_list, "active_index", rows=8)
        col1 = row.column()
        col1.operator("cyascenemanager.sort_file", icon = 'SORTALPHA').mode =  'name'
        col1.operator("cyascenemanager.sort_file", icon = 'SORTTIME').mode =  'time'

        #col1.operator("cyascenemanager.sort_file", icon = 'ARROW_LEFTRIGHT').mode =  ''

        row = col.row()
        row.prop(prop,"selected_file")
        row.operator("cyascenemanager.save_file", icon = 'FILE_NEW')




class CYASCENEMANAGER_Props_item(PropertyGroup):
    name : StringProperty()
    bool_val : BoolProperty()
    filetype : StringProperty()
    date : StringProperty()

bpy.utils.register_class(CYASCENEMANAGER_Props_item)


#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_Props_list(PropertyGroup):
    active_index : IntProperty( update = cmd.selection_changed )
    itemlist : CollectionProperty(type=CYASCENEMANAGER_Props_item)#アイテムプロパティの型を収めることができるリストを生成


#---------------------------------------------------------------------------------------
#コピーツール
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_MT_copytools(Operator):
    bl_idname = "cyascenemanager.copytools"
    bl_label = "Copy Tools"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return{'FINISHED'}

    def draw(self, context):
        prop = bpy.context.scene.cyascenemanager_oa

        layout=self.layout

        box = layout.box()
        box.label(text="Copy Move")
        col = box.column()
        row = col.row()
        row.prop(prop,"copy_target", expand=True)

        row = col.row()
        row.operator("cyascenemanager.move", text = 'copy').mode = 'copy'
        row.operator("cyascenemanager.move", text = 'move').mode = 'move'
        row.operator("cyascenemanager.save_as_work" , icon = 'COPYDOWN')

        row = col.row()
        row.operator("cyascenemanager.load_textures" )

        row.prop(prop,"add_work" )
        row.operator("cyascenemanager.apply", icon='EVENT_A')


        box = layout.box()
        box.label(text="Option")
        box.prop(prop,"import_obj_scale" )
        box.prop(prop,"import_obj_apply" )





#---------------------------------------------------------------------------------------
#Blenderファイルオープン
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_MT_fileopen(Operator):
    bl_idname = "cyascenemanager.fileopen"
    bl_label = "file open"
    #msg : StringProperty()
    msg: StringProperty(
        name = "msg",
        description = "msg",
        default = ''
    )

    confirm : EnumProperty(
        name="Confirm",
        items= [
            ('Yes',"Yes",''),
            ('No',"No",''),
        ],
    )

    filename : StringProperty()
    mode : StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if self.confirm == 'Yes':
            if self.mode == 'blend':
                cmd.open_file_icon_clicked(self.filename,self.mode)

            if self.mode == 'fbx':
                print('fbx')
                cmd.open_file_icon_clicked(self.filename,self.mode)

            if self.mode == 'obj':
                print('obj')
                cmd.open_file_icon_clicked(self.filename,self.mode)


        return{'FINISHED'}

    def draw(self, context):
        prop = bpy.context.scene.cyascenemanager_oa

        self.layout.label(text= self.msg )

        if self.mode == 'fbx':
            self.layout.label(text= 'チェックがついていれば複数インポート' )

        self.layout.label(text= self.filename )
        self.layout.prop(self, "confirm", expand=True)



#---------------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_OT_save_as_work(Operator):
    """現在ひらいているシーンをバックアップする"""
    bl_idname = "cyascenemanager.save_as_work"
    bl_label = ""

    def execute(self, context):
        cmd.save_backup()
        return {'FINISHED'}

class CYASCENEMANAGER_OT_load_textures(Operator):
    bl_idname = "cyascenemanager.load_textures"
    bl_label = "load_textures"
    def execute(self, context):
        print("sssss")
        cmd.load_textures()
        return {'FINISHED'}

class CYASCENEMANAGER_OT_move(Operator):
    bl_idname = "cyascenemanager.move"
    bl_label = "move"
    mode : StringProperty()

    def execute(self, context):
        cmd.move(self.mode)
        return {'FINISHED'}

class CYASCENEMANAGER_OT_open_file(Operator):
    bl_idname = "cyascenemanager.open_file"
    bl_label = ""

    def execute(self, context):
        cmd.open_file()
        return {'FINISHED'}

class CYASCENEMANAGER_OT_save_file(Operator):
    bl_idname = "cyascenemanager.save_file"
    bl_label = ""

    def execute(self, context):
        cmd.save_file()
        return {'FINISHED'}

#---------------------------------------------------------------------------------------
#
#ディレクトリ操作
#
#---------------------------------------------------------------------------------------

class CYASCENEMANAGER_OT_reload(Operator):
    """リロード"""
    bl_idname = "cyascenemanager.reload"
    bl_label = ""
    mode : IntProperty()

    def execute(self, context):
        cmd.setproject(self.mode)
        return {'FINISHED'}


#１階層上に上る
class CYASCENEMANAGER_OT_go_up_dir(Operator):
    bl_idname = "cyascenemanager.go_up_dir"
    bl_label = ""

    def execute(self, context):
        cmd.go_up_dir()
        return {'FINISHED'}


#リストのアイコンを選択した時の処理　ディレクトリかファイルか
class CYASCENEMANAGER_OT_select_icon(Operator):
    bl_idname = "cyascenemanager.select_icon"
    bl_label = ""
    mode : StringProperty()
    name : StringProperty()

    def execute(self, context):

        if self.mode == 'dir':
            cmd.select_icon(self.mode,self.name)

        elif self.mode == 'blend':
            msg = 'Blendファイルを開きます(escでキャンセル)'
            bpy.ops.cyascenemanager.fileopen('INVOKE_DEFAULT',msg = msg , filename = self.name ,mode =self.mode)

        elif self.mode == 'fbx':
            msg = 'fbxファイルをインポートします(escでキャンセル)'
            bpy.ops.cyascenemanager.fileopen('INVOKE_DEFAULT',msg = msg , filename = self.name ,mode =self.mode)

        elif self.mode == 'obj':
            msg = 'objファイルをインポートします(escでキャンセル)'
            bpy.ops.cyascenemanager.fileopen('INVOKE_DEFAULT',msg = msg , filename = self.name ,mode =self.mode)


        return {'FINISHED'}


class CYASCENEMANAGER_OT_blend(Operator):
    bl_idname = "cyascenemanager.blend"
    bl_label = ""


class CYASCENEMANAGER_OT_open_explorer(Operator):
    bl_idname = "cyascenemanager.open_explorer"
    bl_label = ""

    def execute(self, context):
        prop = bpy.context.scene.cyascenemanager_oa
        subprocess.Popen(["explorer", prop.current_dir ], shell=True)
        return {'FINISHED'}


class CYASCENEMANAGER_OT_reload_rootpath(Operator):
    """リロード"""
    bl_idname = "cyascenemanager.reload_rootpath"
    bl_label = ""

    def execute(self, context):
        cmd.reload_rootpath()
        return {'FINISHED'}


#---------------------------------------------------------------------------------------
#
#ファイルのソート
#
#---------------------------------------------------------------------------------------

class CYASCENEMANAGER_OT_sort_file(Operator):
    bl_idname = "cyascenemanager.sort_file"
    bl_label = ""
    mode : StringProperty()


    def execute(self, context):
        cmd.sort_file(self.mode)
        return {'FINISHED'}





#---------------------------------------------------------------------------------------
#
#プロジェクトのプロパティリスト
#
#---------------------------------------------------------------------------------------
class CYASCENEMANAGER_TestProps_OA(bpy.types.PropertyGroup):
    # work_root : StringProperty(name="work root", default= r'E:\data\project\YKS')
    # backup_root : StringProperty(name="backup root", default= r'E:\data\project\YKSBuckup')
    # onedrive_root : StringProperty(name="onedrive root", default= r'E:\data\OneDrive\projects\YKS')

    projectname : StringProperty()
    work_root : StringProperty()
    backup_root : StringProperty()
    onedrive_root : StringProperty()




bpy.utils.register_class(CYASCENEMANAGER_TestProps_OA)


classes = (
    CYASCENEMANAGER_Props_OA,
    CYASCENEMANAGER_UL_uilist,
    CYASCENEMANAGER_Props_list,
    CYASCENEMANAGER_PT_scenemanager,
    CYASCENEMANAGER_OT_save_as_work,
    CYASCENEMANAGER_OT_reload,
    CYASCENEMANAGER_OT_move,
    #CYASCENEMANAGER_OT_switch_work,
    #CYASCENEMANAGER_OT_switch_backup,
    CYASCENEMANAGER_OT_open_file,
    CYASCENEMANAGER_OT_save_file,
    #CYASCENEMANAGER_OT_save_onedrive,

    CYASCENEMANAGER_OT_select_icon,
    CYASCENEMANAGER_OT_blend,
    CYASCENEMANAGER_OT_go_up_dir,
    CYASCENEMANAGER_OT_open_explorer,

    CYASCENEMANAGER_OT_load_textures,
    CYASCENEMANAGER_MT_copytools,

    CYASCENEMANAGER_MT_fileopen,
    CYASCENEMANAGER_OT_sort_file,

    CYASCENEMANAGER_OT_reload_rootpath,
#     CYASCENEMANAGER_PT_materialtools,
#     CYASCENEMANAGER_OT_assign_vertex_color,
#     CYASCENEMANAGER_OT_convert_vertex_color,
#     CYASCENEMANAGER_OT_pick_vertex_color
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cyascenemanager_oa = PointerProperty(type=CYASCENEMANAGER_Props_OA)
    bpy.types.WindowManager.cyascenemanager_list = PointerProperty(type=CYASCENEMANAGER_Props_list)

    bpy.app.handlers.load_post.append(cyascenemanager_handler)
    #bpy.app.handlers.save_post.append(cyascenemanager_handler)


    #プロジェクトのプロパティを登録
    bpy.types.Scene.cyascenemanager_proj = bpy.props.CollectionProperty(type=CYASCENEMANAGER_TestProps_OA)



    # json_path = r'E:\data\OneDrive\projects\_lib\Blender\CyaFileBrowserData.json'

    # if os.path.exists( json_path ):
    #     with open( json_path , 'r') as fp:
    #         DATA = json.load(fp)

    # print("---------------DATA-------------------")

    # for d in DATA:
    #     print(d["projectname"])
    #     newCustomItem = bpy.context.scene.cyascenemanager_proj.add()
    #     newCustomItem.projectname = d["projectname"]




def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cyascenemanager_oa
    del bpy.types.WindowManager.cyascenemanager_list
    del bpy.types.Scene.cyascenemanager_proj

    bpy.app.handlers.load_post.remove(cyascenemanager_handler)
    #bpy.app.handlers.save_post.remove(cyascenemanager_handler)


