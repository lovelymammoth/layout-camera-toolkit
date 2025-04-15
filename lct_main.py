import os
import maya.cmds as cmds
import maya.mel as mel
from PySide6 import QtWidgets, QtGui, QtUiTools

DIR_PATH = os.path.dirname(__file__)
IMG_PATH = DIR_PATH + "/img/lct_cover.jpg"
UI_PATH = DIR_PATH + "/lct_UI.ui"


class LctScene:
    def __init__(self):
        # LOAD UI
        self.wg_util = QtUiTools.QUiLoader().load(UI_PATH)

        # CONNECT buttons with function

        self.wg_util.btn_create_camera.clicked.connect(self.press_create_camera)
        self.wg_util.btn_look_thru.clicked.connect(self.push_look_thru)
        self.wg_util.btn_cycle_cam.clicked.connect(self.push_cycle_cam)
        self.wg_util.btn_frustum.clicked.connect(self.push_frustum)
        self.wg_util.btn_aim.clicked.connect(self.push_aim)
        self.wg_util.btn_change_lense.clicked.connect(self.push_change_lense)
        self.wg_util.btn_active_camera.clicked.connect(self.push_active_camera)
        self.wg_util.btn_previous_cam_view.clicked.connect(self.push_previous_camera_view)
        self.wg_util.btn_next_cam_view.clicked.connect(self.push_next_camera_view)
        self.wg_util.btn_create_focus.clicked.connect(self.push_create_focus)
        self.wg_util.btn_delete.clicked.connect(self.push_delete)

        # ADD pixmap image
        pixmap = QtGui.QPixmap(IMG_PATH)
        self.wg_util.cover.setPixmap(pixmap)

        # SHOW UI
        self.wg_util.show()


    # FUNCTIONS

    # CREATE CAMERA BUTTON
    def press_create_camera(self):
        # CHECK Aim at selected object
        check_aim = self.wg_util.chb_aim.isChecked()
        sel_obj = cmds.ls(selection=True)
        if check_aim and not sel_obj:
            cmds.inViewMessage(statusMessage="No selected object to look at!\nPlease select an object or uncheck 'Look At Selection'.", fade=True, position='midCenterBot')
            cmds.warning("No selected object to look at! Please select an object or uncheck 'Look At Selection'.")
            return

        # SET camera name
        camera_name = str(self.wg_util.text_camera_name.text())
        if camera_name == "":
            camera_name = "lct"

        # CREATE NEW CAMERA
        new_camera = cmds.camera(name=camera_name + '_cam', displayFilmGate=True, displayGateMask=True)

        # GET camera position preference
        camera_position = self.wg_util.cbx_camera_at.currentText()

        # CHECK Frustum
        check_frustum = self.wg_util.chb_frustum.isChecked()
        if check_frustum:
            cmds.setAttr(new_camera + '.displayCameraFrustum', 1)

        # CHECK DoF
        check_dof = self.wg_util.chb_dof.isChecked()
        if check_dof:
            cmds.setAttr(new_camera[1] + '.depthOfField', 1)
            cmds.setAttr(new_camera[1] + '.aiEnableDOF', 1)

        # SET focal length
        lense = float(self.wg_util.cbx_lense.currentText())
        cmds.setAttr(new_camera[1] + '.focalLength', lense)

        viewport_camera_position = [6.0, 5.45, -6.0]
        viewport_camera_rotation = [-34.2, 134, 0]

        #SET new camera position
        if camera_position == "Current view":
            # GET active camera position
            viewport_camera = cmds.lookThru(query=True)
            viewport_camera = viewport_camera.replace("Shape", "")
            cmds.lookThru(new_camera[0])
            cmds.matchTransform([new_camera[0], viewport_camera], pos=True, rot=True)
        else:
            cmds.setAttr(new_camera[0] + ".translate", viewport_camera_position[0], viewport_camera_position[1], viewport_camera_position[2])
            cmds.setAttr(new_camera[0] + ".rotate", viewport_camera_rotation[0], viewport_camera_rotation[1], viewport_camera_rotation[2])

        # CREATE focus target
        focus_loc_target = []
        check_create_focus_target = self.wg_util.chb_focus_target.isChecked()
        if check_create_focus_target and check_dof:

            # Target Focus Locator
            focus_loc_target = cmds.spaceLocator(name=new_camera[0] + '_focus_target')

            if check_aim:
                target_position = cmds.xform(sel_obj[0], q=True, t=True, ws=True)
                cmds.setAttr(focus_loc_target[0] + ".translate", target_position[0], target_position[1], target_position[2])
            else:
                target_position = [0,0,0]
                cmds.setAttr(focus_loc_target[0] + ".translate", target_position[0], target_position[1], target_position[2])
            
            # CONNECT camera to locator with distanceBetween
            distance = cmds.createNode("distanceBetween", name=new_camera[0] + "_distanceBetween")
            cmds.connectAttr(new_camera[1] + ".worldMatrix[0]", distance + ".inMatrix1")
            cmds.connectAttr(focus_loc_target[0] + ".worldMatrix[0]", distance + ".inMatrix2")
            cmds.connectAttr(distance + ".distance", new_camera[1] + ".focusDistance")
            cmds.connectAttr(distance + ".distance", new_camera[1] + ".aiFocusDistance")

            cmds.select(focus_loc_target)

            # BONUS: change target's colour (Attribute Editor -> Drawing Overrides -> Color [index] -> 13)
            cmds.setAttr(focus_loc_target[0] + "Shape.overrideEnabled", True)
            cmds.setAttr(focus_loc_target[0] + "Shape.overrideColor", 13)

        # CENTER view to selection
        if check_aim:
            if focus_loc_target:
                cmds.viewLookAt()
            else:
                cmds.select(sel_obj)
                cmds.viewLookAt()
            # SET Near and Far Clip Plane automatically
            #cmds.viewClipPlane(acp=True) 


        # MESSAGE
        cmds.inViewMessage(statusMessage="New camera created: " + new_camera[0], fade=True, position='midCenterBot')

    # CAMERA MANAGER *****************************

    # LOOK THROUGH SELECTED CAMERA
    def push_look_thru(self):
        persp_cameras = cmds.listCameras(p=True)
        selected_camera = cmds.ls(selection=True, showType=True)[0]
        if selected_camera in persp_cameras:
            cmds.lookThru(selected_camera)
            cmds.inViewMessage(statusMessage=selected_camera, fade=True, position='midCenter')
        else:
            cmds.warning('No camera selected')


    # CYCLE THROUGH SELECTED
    def push_cycle_cam(self):
        current_camera = cmds.lookThru(query=True)
        camera_type = cmds.camera(current_camera, query=True, orthographic=True)
        persp_cameras = cmds.listCameras(perspective=True)
        if not camera_type:                                 # See if camera is perspective
            nr = persp_cameras.index(current_camera)
            count = len(persp_cameras) - 1
            if current_camera == persp_cameras[count]:
                nr = 0
                cmds.lookThru(persp_cameras[nr])
            else:
                nr = nr + 1
                cmds.lookThru(persp_cameras[nr])
        else:
            nr = 0
            cmds.lookThru (persp_cameras[nr])
        mel.eval ('print ("Camera: " + `lookThru -q`)')
        check_select_camera_cyclcing = self.wg_util.chb_select_camera_cycling.isChecked()
        if check_select_camera_cyclcing:
            cmds.select(persp_cameras[nr])
        cmds.inViewMessage(statusMessage=persp_cameras[nr], fade=True, position='midCenter')

        

    # TURN ON/OFF FRUSTUM
    def push_frustum(self):
        persp_cameras = cmds.listCameras(perspective=True)
        selected_camera = cmds.ls(persp_cameras ,selection=True)
        if selected_camera:
            check_frustum = cmds.getAttr(selected_camera[0] +".displayCameraFrustum")
            if check_frustum:
                cmds.setAttr(selected_camera[0] + ".displayCameraFrustum", 0)
                cmds.setAttr(selected_camera[0] + ".displayCameraNearClip", 0)
                cmds.setAttr(selected_camera[0] + ".displayCameraFarClip", 0)
            else:
                cmds.viewClipPlane(acp=True) 
                cmds.setAttr(selected_camera[0] + ".displayCameraFrustum", 1)
                cmds.setAttr(selected_camera[0] + ".displayCameraNearClip", 1)
                cmds.setAttr(selected_camera[0] + ".displayCameraFarClip", 1)
        else:
            cmds.warning('No camera selected!')

    # AIM AT SELECTION
    def push_aim(self):
        sel_obj = cmds.ls(selection=True)
        if not sel_obj:
            cmds.inViewMessage(statusMessage="No selected object to look at!.", fade=True, position='midCenterBot')
            cmds.warning("No selected object to look at!.")
            return
        else:
            cmds.viewLookAt()

    # CHANGE LENSE
    def push_change_lense(self):
        current_camera = cmds.lookThru(query=True)
        current_lense = cmds.getAttr(current_camera + ".focalLength")
        new_lense = float(self.wg_util.cbx_new_lense.currentText())
        if not new_lense == current_lense:
            cmds.setAttr(current_camera + '.focalLength', new_lense)
        else:
            cmds.warning("This lense is already applied")

    # SELECT ACTIVE CAMERA
    def push_active_camera(self):
        current_camera = cmds.lookThru(query=True)
        cmds.select(current_camera)

    # UNDO CAMERA VIEW
    def push_previous_camera_view(self):
        current_camera = cmds.lookThru(query=True)
        cmds.viewSet(previousView=True)

    def push_next_camera_view(self):
        current_camera = cmds.lookThru(query=True)
        cmds.viewSet(nextView=True)


    def push_create_focus(self):
        camera = cmds.lookThru(q=True)
        target = cmds.ls(sl=True)
        check_connection = cmds.connectionInfo(camera + ".focusDistance", isDestination=True)
        if camera == 'persp':
            cmds.warning("'persp' camera is invalid. You must select a different camera.")
            return
        else:
            if check_connection:
                cmds.warning("There is a target already connected.")
                return
            else:
                cmds.setAttr(camera + ".depthOfField",1)
                cmds.setAttr(camera + ".aiEnableDOF", 1)
                distance = cmds.createNode('distanceBetween', name='lct_cam_distanceBetween')
                loc = cmds.spaceLocator(name=camera + "_focus_target")
                if target:
                    cmds.matchTransform(loc[0], target[0])
                cmds.connectAttr(camera + ".worldMatrix[0]", distance + ".inMatrix1")
                cmds.connectAttr(loc[0] + ".worldMatrix[0]", distance + ".inMatrix2")
                cmds.connectAttr(distance + ".distance", camera + ".focusDistance")
                cmds.inViewMessage(staticMessage="Focus target created: " + str(loc))

    def push_delete(self):
        camera = cmds.ls(sl=True)
        print(camera)
        persp_cameras = cmds.listCameras(perspective=True)
        print(persp_cameras)
        if camera[0] in persp_cameras:
            if not 'persp' == camera:
                cmds.confirmDialog(title='Confirm Delete Camera', message='Are you sure?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
                cmds.delete(camera[0], s=True)
                loc = cmds.objExists(camera[0] + "_focus_target")
                if loc:
                    cmds.delete(camera[0] + "_focus_target", s=True)
            else:
                cmds.warning("Can't delete 'persp' camera.")
        else:
            cmds.warning("No camera selected.")


# DCC Start
def start():
    global lct
    lct = LctScene()

start()

