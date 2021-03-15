import maya.cmds as mc
import math
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets


def get_maya_window():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaMainWindowPtr), QtWidgets.QWidget)


class LayoutTools(QtWidgets.QWidget):
    OBJECT_NAME = "LayoutTools"

    def __init__(self, parent=None):
        super(LayoutTools, self).__init__(parent)

        self.__sj_time_changed = None
        self.__sj_selection_changed = None
        self.copy_list = None

        self.setObjectName(LayoutTools.OBJECT_NAME)
        self.setWindowTitle('AM Layout Tools')
        self.setParent(parent or get_maya_window())
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.camera = get_camera()
        self.__setup_ui()

    def __setup_ui(self):
        self.__create_widgets()
        self.__modify_widgets()
        self.__create_layouts()
        self.__add_widgets_to_layouts()
        self.__setup_connections()

    def __create_widgets(self):
        self.camera_lbl = QtWidgets.QLabel('Camera')
        self.camera_le = QtWidgets.QLineEdit()
        self.camera_btn = QtWidgets.QPushButton('Refresh')
        self.camera_cb = QtWidgets.QCheckBox('Auto')

        self.focal_lbl = QtWidgets.QLabel('Focal')
        self.focal_spb = QtWidgets.QSpinBox()
        self.focal_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.focal_btn = QtWidgets.QPushButton('Key')

        self.near_lbl = QtWidgets.QLabel('Near')
        self.near_dblSpb = QtWidgets.QDoubleSpinBox()
        self.near_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        self.tools_copy_btn = QtWidgets.QPushButton('Copy')
        self.tools_paste_btn = QtWidgets.QPushButton('Paste')
        self.tools_mpc_btn = QtWidgets.QPushButton('MultiParentConstraint')

        self.tools_tiers_btn = QtWidgets.QPushButton('Tiers')
        self.tools_fibonacciSpiral_btn = QtWidgets.QPushButton('FibonacciSpiral')
        self.tools_wd_btn = QtWidgets.QPushButton('WaveDestroyer')

        self.help_curves_view_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

    def __modify_widgets(self):
        self.camera_le.setReadOnly(1)
        self.camera_le.setText(self.camera.name)

        self.focal_spb.setMinimum(15)
        self.focal_spb.setMaximum(250)
        self.focal_slider.setMinimum(15)
        self.focal_slider.setMaximum(250)

        self.near_slider.setMinimum(1)
        self.near_slider.setMaximum(5000)

        self.focal_slider.setValue(self.camera.focal)
        self.focal_spb.setValue(self.camera.focal)
        self.near_slider.setValue(self.camera.near * 10)
        self.near_dblSpb.setValue(self.camera.near)

    def __create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.camera_layout = QtWidgets.QHBoxLayout()
        self.focal_layout = QtWidgets.QHBoxLayout()
        self.near_layout = QtWidgets.QHBoxLayout()
        self.tools_layout = QtWidgets.QHBoxLayout()
        self.tools_two_layout = QtWidgets.QHBoxLayout()

    def __add_widgets_to_layouts(self):
        [self.camera_layout.addWidget(w) for w in (self.camera_lbl, self.camera_le, self.camera_cb, self.camera_btn)]
        [self.focal_layout.addWidget(w) for w in (self.focal_lbl, self.focal_spb, self.focal_slider, self.focal_btn)]
        [self.near_layout.addWidget(w) for w in (self.near_lbl, self.near_dblSpb, self.near_slider)]
        [self.tools_layout.addWidget(w) for w in (self.tools_copy_btn, self.tools_paste_btn, self.tools_mpc_btn)]
        [self.tools_two_layout.addWidget(w) for w in
         (self.tools_tiers_btn, self.tools_fibonacciSpiral_btn, self.tools_wd_btn)]

        [self.main_layout.addLayout(l) for l in
         (self.camera_layout, self.focal_layout, self.near_layout, self.tools_layout, self.tools_two_layout)]

    def __setup_connections(self):
        self.camera_btn.clicked.connect(self.refresh)
        self.camera_cb.clicked.connect(self.setup_camera_callback)

        self.focal_spb.valueChanged.connect(self.focal_value_spb)
        self.focal_slider.valueChanged.connect(self.focal_value_slider)
        self.focal_btn.clicked.connect(self.key_focal)

        self.near_slider.valueChanged.connect(self.near_value_slider)
        self.near_dblSpb.valueChanged.connect(self.near_value_dblspb)

        self.tools_copy_btn.clicked.connect(self.ui_copy_selected_transform)
        self.tools_paste_btn.clicked.connect(self.ui_paste_selected_transform)
        self.tools_mpc_btn.clicked.connect(self.ui_multi_parent_constraint)

        self.tools_tiers_btn.clicked.connect(self.ui_tiers)
        self.tools_fibonacciSpiral_btn.clicked.connect(self.ui_fibonacci_spiral)
        self.tools_wd_btn.clicked.connect(self.ui_wave_destroyer_inputdialog)

    def setup_camera_callback(self):
        if not self.camera_cb.isChecked() and self.__sj_time_changed and self.__sj_selection_changed:
            mc.scriptJob(k=self.__sj_time_changed, f=True)
            mc.scriptJob(k=self.__sj_selection_changed, f=True)

        elif self.camera_cb.isChecked():
            self.__sj_time_changed = mc.scriptJob(cu=True, kws=False, event=['timeChanged', self.refresh])
            self.__sj_selection_changed = mc.scriptJob(cu=True, kws=False, event=['SelectionChanged', self.refresh])

    def closeEvent(self, event):
        if not self.camera_cb.isChecked() and self.__sj_time_changed and self.__sj_selection_changed:
            mc.scriptJob(k=self.__sj_time_changed, f=True)
            mc.scriptJob(k=self.__sj_selection_changed, f=True)

        if mc.objExists('AM_cameraTools_grp'):
            mc.delete('AM_cameraTools_grp')

    def refresh(self):
        self.camera = get_camera()
        self.camera_le.setText(self.camera.name)
        self.focal_slider.setValue(self.camera.focal)
        self.focal_spb.setValue(self.camera.focal)
        self.near_slider.setValue(self.camera.near * 100)
        self.near_dblSpb.setValue(self.camera.near)

    def focal_value_spb(self, value):
        self.focal_slider.setValue(value)
        self.camera.set_focal(value)

    def focal_value_slider(self, value):
        self.focal_spb.setValue(value)

    def key_focal(self):
        self.camera.key_focal()

    def near_value_dblspb(self, value):
        self.near_slider.setValue(value * 100)
        self.camera.set_near(value)

    def near_value_slider(self, value):
        self.near_dblSpb.setValue(value / 100)

    def ui_copy_selected_transform(self):
        self.copy_list = copy_selected_transform()

    def ui_paste_selected_transform(self):
        paste_selected_transform(self.copy_list[0], self.copy_list[1], self.copy_list[2])

    def ui_multi_parent_constraint(self):
        multi_parent_constraint()

    def ui_tiers(self):
        self.camera.set_tiers()

    def ui_fibonacci_spiral(self):
        self.camera.set_fibonnaci_spiral()

    def ui_wave_destroyer_inputdialog(self):
        key_value, ok = QtWidgets.QInputDialog.getInt(self, 'Number',
                                                      'Put the frame number between last 2 keys of focal (before transfer!):')

        if ok and key_value:
            wave_destroyer(key_value)


class Camera:
    def __init__(self, name, focal, near, panel):
        self.name = name
        self.focal = focal
        self.near = near
        self.panel = panel

    def set_focal(self, value):
        if not mc.listConnections(self.name + '.focalLength', destination=True, plugs=True, type='transform'):
            focal_path = self.name + '.focalLength'
        else:
            focal_path = mc.listConnections(self.name + '.focalLength', destination=True, plugs=True, type='transform')[
                0]

        mc.setAttr(focal_path, value)
        self.focal = value

    def set_near(self, value):
        if not mc.listConnections(self.name + '.nearClipPlane', destination=True, plugs=True, type='transform'):
            near_path = self.name + '.nearClipPlane'
        else:
            near_path = \
                mc.listConnections(self.name + '.nearClipPlane', destination=True, plugs=True, type='transform')[0]

        mc.setAttr(near_path, value)
        self.near = value

    def key_focal(self):
        if not mc.listConnections(self.name + '.focalLength', destination=True, plugs=True, type='transform'):
            focal_path = self.name + '.focalLength'
        else:
            focal_path = mc.listConnections(self.name + '.focalLength', destination=True, plugs=True, type='transform')[
                0]
        mc.setKeyframe(focal_path)

    def set_tiers(self):
        am_grp = 'AM_cameraTools_grp'
        if not mc.objExists(am_grp):
            mc.group(em=True, name='AM_cameraTools_grp')

        cam_grp = self.name + '_grp'
        if not mc.objExists(cam_grp):
            mc.group(em=True, name=self.name + '_grp')
            mc.parent(cam_grp, am_grp)
            mc.parentConstraint(self.name, cam_grp, maintainOffset=False)

        tiers_grp = self.name + '_tiers'
        if not mc.objExists(tiers_grp):
            mc.group(em=True, name=self.name + '_tiers')
            mc.parent(tiers_grp, cam_grp)
            create_tiers(self.name, self.panel)

        else:
            old_sel = mc.ls(selection=True)
            isolate_transform = []
            if mc.listRelatives(mc.ls(type='mesh'), path=True, parent=True):
                isolate_transform = mc.listRelatives(mc.ls(type='mesh'), path=True, parent=True)

            isolate_transform.append(tiers_grp)
            mc.select(isolate_transform)
            currentState = mc.isolateSelect(self.panel, query=True, state=True)

            if currentState == 0:
                mc.isolateSelect(self.panel, state=1)
                mc.isolateSelect(self.panel, addSelected=True)
                mc.setAttr(tiers_grp + '.visibility', 1)
                mc.select(old_sel, r=True)
            else:
                mc.isolateSelect(self.panel, state=0)
                mc.isolateSelect(self.panel, removeSelected=True)
                mc.setAttr(tiers_grp + '.visibility', 0)
                mc.select(old_sel, r=True)

    def set_fibonnaci_spiral(self):
        am_grp = 'AM_cameraTools_grp'
        if not mc.objExists(am_grp):
            mc.group(em=True, name='AM_cameraTools_grp')

        cam_grp = self.name + '_grp'
        if not mc.objExists(cam_grp):
            mc.group(em=True, name=self.name + '_grp')
            mc.parent(cam_grp, am_grp)
            mc.parentConstraint(self.name, cam_grp, maintainOffset=False)

        fibonacci_grp = self.name + '_fibonacci'
        if not mc.objExists(fibonacci_grp):
            mc.group(em=True, name=self.name + '_fibonacci')
            mc.parent(fibonacci_grp, cam_grp)
            create_fibonacci_curve(self.name, self.panel, 15, 16)


# get the current camera ,in this order, selection > sequencer > 2nd camera in list of all cams
# send camera to camera Class

def get_camera():
    sel = mc.ls(selection=True)
    cam_shot = mc.sequenceManager(currentShot=True, query=True)
    cam_list = []
    cam_panel = []

    if sel:
        for c in sel:
            if mc.listRelatives(c, type='camera'):
                cam_list.append(c)

            elif mc.listRelatives(c, type='nurbsCurve') and mc.listRelatives(c, allDescendents=True, type='camera'):
                cam_shape = mc.listRelatives(c, allDescendents=True, type='camera')[0]
                parent_node = mc.listRelatives(cam_shape, parent=True)[0]
                cam_list.append(parent_node)

    if cam_list:
        cam = cam_list[0]

    elif not cam_list and cam_shot:
        if not mc.listRelatives(mc.shot(cam_shot, currentCamera=True, query=True), shapes=True):
            cam = mc.listRelatives(mc.shot(cam_shot, currentCamera=True, query=True), parent=True)[0]
        else:
            cam = mc.shot(cam_shot, currentCamera=True, query=True)

    else:
        all_cam = mc.ls(type='camera')
        cam = mc.listRelatives(all_cam[1], parent=True)[0]

    for p in mc.getPanel(type="modelPanel"):
        if mc.modelPanel(p, query=True, camera=True) == cam:
            cam_panel = p

        elif mc.modelPanel(p, query=True, camera=True) == mc.listRelatives(cam, shapes=True)[0]:
            cam_panel = p

        else:
            continue

    if not cam_panel:
        mc.warning('No Panel with this camera. Put one and refresh')

    camera = Camera(cam, mc.getAttr(cam + '.focalLength'), mc.getAttr(cam + '.nearClipPlane'), cam_panel)
    return camera


def copy_selected_transform():
    sel = mc.ls(selection=True)

    if len(sel) is not 1 and mc.nodeType(sel) != 'transform':
        mc.error('Select one transform')

    else:
        world_translate = mc.xform(sel, worldSpace=True, translation=True, query=True)
        world_rotate = mc.xform(sel, worldSpace=True, rotation=True, query=True)
        world_scale = mc.xform(sel, worldSpace=True, scale=True, query=True)

        return world_translate, world_rotate, world_scale


def paste_selected_transform(world_translate, world_rotate, world_scale):
    sel = mc.ls(selection=True)

    if len(sel) is not 1 and mc.nodeType(sel) != 'transform':
        mc.error('Select one transform')

    else:
        mc.xform(sel, worldSpace=True, translation=world_translate)
        mc.xform(sel, worldSpace=True, rotation=world_rotate)
        mc.xform(sel, worldSpace=True, scale=world_scale)


def multi_parent_constraint():
    sel = mc.ls(selection=True)
    mpc_childrens = sel[:-1]
    mpc_parent = sel[-1]

    if sel:
        for t in sel:
            if mc.nodeType(t) != 'transform' and len(sel) < 3:
                mc.warning('Select 3 transforms mini')

            else:
                for p in mpc_childrens:
                    mc.parentConstraint(mpc_parent, p, mo=True)

                mc.select(mpc_parent, r=True)
    else:
        mc.warning('Select 3 transforms mini')


def wave_destroyer(key_value):
    values_focal_alpha = []
    anim_crv = mc.keyframe(selected=True, name=True, query=True)
    cam = []
    playback = mc.playbackOptions(minTime=True, query=True), mc.playbackOptions(maxTime=True, query=True)

    if anim_crv and len(mc.keyframe(anim_crv, timeChange=True, query=True, selected=True)) == 3:
        cam_focal = mc.listConnections(anim_crv, plugs=True)[0]

        if mc.listConnections(cam_focal, type='camera'):
            cam = mc.listConnections(cam_focal, type='camera')[0]

        else:
            cam = mc.listRelatives(cam_focal.rsplit('.', 1)[0], parent=True)[0]

    if not cam:
        mc.error('Select 3 focal''s keys from graph editor')

    select_time = mc.keyframe(cam_focal, timeChange=True, query=True, selected=True)
    values_focal = mc.keyframe(cam_focal, valueChange=True, selected=True, query=True)

    store_start_keys = mc.keyframe(cam_focal, time=(playback[0], select_time[0] - 1), query=True, timeChange=True,
                                   valueChange=True)
    store_end_keys = mc.keyframe(cam_focal, time=(select_time[-1] + 1, playback[1]), query=True, timeChange=True,
                                 valueChange=True)

    for v in values_focal:
        values = 100 * math.atan(v)
        values_focal_alpha.append(values)

    mc.addAttr(cam, longName='Alpha', attributeType='double', min=80, max=157, keyable=True)
    cam_focal_alpha = cam + '.Alpha'
    mc.setAttr(cam_focal_alpha, keyable=True)

    mc.cutKey(cam_focal)

    mc.setKeyframe(cam_focal_alpha, time=(select_time[0], select_time[0]), value=values_focal_alpha[0],
                   inTangentType='auto', outTangentType='auto')
    mc.setKeyframe(cam_focal_alpha, time=(select_time[-2] + key_value, select_time[-2] + key_value),
                   value=values_focal_alpha[-1], inTangentType='auto', outTangentType='auto')
    mc.setKeyframe(cam_focal_alpha, time=(select_time[-2], select_time[-2]), inTangentType='auto',
                   outTangentType='auto', insert=True)
    mc.keyframe(cam_focal_alpha, edit=True,
                time=(select_time[-2] + key_value, select_time[-2] + key_value), absolute=True,
                timeChange=select_time[-1])
    mc.keyTangent(cam_focal_alpha, inTangentType='auto', outTangentType='auto')

    exp = '%s = tan(%s/100)' % (cam_focal, cam_focal_alpha)
    mc.expression(s=exp)

    mc.bakeResults(cam_focal, simulation=True, time=(select_time[0], select_time[-1]), sampleBy=True,
                   preserveOutsideKeys=True, sparseAnimCurveBake=0)

    if store_start_keys:
        index = 0
        for k in store_start_keys:
            if index < len(store_start_keys):
                mc.setKeyframe(cam_focal, time=(store_start_keys[index], store_start_keys[index]),
                               value=store_start_keys[index + 1])
                index += 2

    if store_end_keys:
        index = 0
        for k in store_end_keys:
            if index < len(store_end_keys):
                mc.setKeyframe(cam_focal, time=(store_end_keys[index], store_end_keys[index]),
                               value=store_end_keys[index + 1])
                index += 2
    mc.keyTangent(cam_focal, inTangentType='auto', outTangentType='auto')
    mc.deleteAttr(cam, attribute='Alpha')


def create_camera_node(camera, plane_for_cam):

    """this fonction ll be create nodes to scaleX and Y plane_for_cam to keep proportions if near_clip and focal are
    changing. this formula ((nearclip * aperture) / focal) work with a plane with 1x1 value and it ll be stick to
    the nearClip"""

    if not mc.objExists('multiplyDivide_focal_' + camera) and not mc.objExists('multiplyDivide_aperture_' + camera):

        # convert inch to mm from aperture's camera (X and Y input)

        multiplyDivide_aperture_node = mc.createNode('multiplyDivide', name='multiplyDivide_aperture_' + camera)
        mc.setAttr(multiplyDivide_aperture_node + '.operation', 1)
        mc.connectAttr(camera + '.horizontalFilmAperture', multiplyDivide_aperture_node + '.input1X')
        mc.connectAttr(camera + '.verticalFilmAperture', multiplyDivide_aperture_node + '.input1Y')
        mc.setAttr(multiplyDivide_aperture_node + '.input2X', 25.4)
        mc.setAttr(multiplyDivide_aperture_node + '.input2Y', 25.4)

        # plane_for_cam ll be on near_clip, add 0.0001 + near_clip value from camera on tz to be sure its always visible

        plusMinus_for_near = mc.createNode('plusMinusAverage', name='plusMinusAverage_near_' + camera)
        mc.setAttr(plusMinus_for_near + '.operation')
        mc.connectAttr(camera + '.nearClipPlane', plusMinus_for_near + '.input1D[0]')
        mc.setAttr(plusMinus_for_near + '.input1D[1]', 0.0001)

        # connect near_clip on first node (Z input)

        mc.connectAttr(plusMinus_for_near + '.output1D', multiplyDivide_aperture_node + '.input1Z')
        mc.setAttr(multiplyDivide_aperture_node + '.input2Z', -1)

        # formula to scale img with nearclip

        multiplyDivide_base_node = mc.createNode('multiplyDivide', name='multiplyDivide_base_' + camera)
        mc.setAttr(multiplyDivide_base_node + '.operation', 1)
        mc.connectAttr(camera + '.nearClipPlane', multiplyDivide_base_node + '.input1X')
        mc.connectAttr(camera + '.nearClipPlane', multiplyDivide_base_node + '.input1Y')
        mc.connectAttr(multiplyDivide_aperture_node + '.output', multiplyDivide_base_node + '.input2')

        # and now, end of formala with focal

        multiplyDivide_focal_node = mc.createNode('multiplyDivide', name='multiplyDivide_focal_' + camera)
        mc.setAttr(multiplyDivide_focal_node + '.operation', 2)
        mc.connectAttr(multiplyDivide_base_node + '.output', multiplyDivide_focal_node + '.input1')
        mc.connectAttr(camera + '.focalLength', multiplyDivide_focal_node + '.input2X')
        mc.connectAttr(camera + '.focalLength', multiplyDivide_focal_node + '.input2Y')

    # connect plane_for_cam to camera

    mc.connectAttr('multiplyDivide_aperture_' + camera + '.outputZ', plane_for_cam + '.translateZ')
    mc.connectAttr('multiplyDivide_focal_' + camera + '.outputX', plane_for_cam + '.scaleX')
    mc.connectAttr('multiplyDivide_focal_' + camera + '.outputY', plane_for_cam + '.scaleY')


def create_tiers(camera, panel):
    old_sel = mc.ls(selection=True)
    tiers_grp = camera + '_tiers'

    top_crv = mc.curve(degree=1, p=[(-0.5, 0.25, 0), (0.5, 0.25, 0)], name=camera + '_top_crv')
    bottom_crv = mc.curve(degree=1, p=[(-0.5, -0.25, 0), (0.5, -0.25, 0)], name=camera + '_bottom_crv')
    left_crv = mc.curve(degree=1, p=[(-0.25, 0.5, 0), (-0.25, -0.5, 0)], name=camera + '_left_crv')
    right_crv = mc.curve(degree=1, p=[(0.25, 0.5, 0), (0.25, -0.5, 0)], name=camera + '_right_crv')

    for curves in top_crv, bottom_crv, left_crv, right_crv:
        mc.parent(curves, tiers_grp)

    matrix_cam = mc.xform(camera, worldSpace=True, matrix=True, query=True)
    mc.xform(tiers_grp, worldSpace=True, matrix=matrix_cam)
    mc.makeIdentity(tiers_grp, apply=True, t=1, r=1, s=1, n=0)

    create_camera_node(camera, tiers_grp)

    isolate_transform = []
    if mc.listRelatives(mc.ls(type='mesh'), path=True, parent=True):
        isolate_transform = mc.listRelatives(mc.ls(type='mesh'), path=True, parent=True)

    isolate_transform.append(tiers_grp)
    mc.select(isolate_transform)

    currentState = mc.isolateSelect(panel, query=True, state=True)
    if currentState == 1:
        mc.isolateSelect(panel, state=0)
        mc.isolateSelect(panel, removeSelected=True)
        mc.isolateSelect(panel, state=1)
        mc.isolateSelect(panel, addSelected=True)
        mc.select(old_sel, r=True)
    else:
        mc.isolateSelect(panel, state=1)
        mc.isolateSelect(panel, addSelected=True)
        mc.select(old_sel, r=True)


def create_fibonacci_curve(camera, panel, iterations, points_per_section):
    """Creates a Fibonacci curve.

    Args:
        iterations (int): number of quarter circles in the created curve
        points_per_section (int): number of segment per quarter of circle

    Returns:
        str: curve maya node
    """
    old_sel = mc.ls(selection=True)
    fibonacci_grp = camera + '_fibonacci'
    # ratio = mc.camera(camera, aspectRatio=True, query=True)
    ratio = (1 + math.sqrt(5)) * 0.5

    all_curves = []

    fib_gen = gen_fib_points(ratio)

    # Create the quarter of circles
    for _ in range(iterations):
        start_point, center_point, end_point = next(fib_gen)
        radius = math.sqrt((start_point[0] - center_point[0]) ** 2 +
                           (start_point[1] - center_point[1]) ** 2)

        ctx = mc.createNode("makeTwoPointCircularArc")
        mc.setAttr(ctx + ".pt1", start_point[0], 0, start_point[1],
                   type='double3')
        mc.setAttr(ctx + ".pt2", end_point[0], 0, end_point[1],
                   type='double3')
        mc.setAttr(ctx + ".directionVector", 0, 1, 0, type='double3')
        mc.setAttr(ctx + ".radius", radius)
        mc.setAttr(ctx + ".sections", points_per_section)

        curve = mc.createNode("nurbsCurve")
        all_curves.append(curve)
        mc.connectAttr(ctx + ".outputCurve", curve + ".create")

        mc.delete(curve, constructionHistory=True)

    # Attach all curves
    mc.attachCurve(all_curves, constructionHistory=False,
                   replaceOriginal=True,
                   keepMultipleKnots=False, method=0, blendBias=0.5,
                   blendKnotInsertion=False, parameter=0.1)
    mc.delete(mc.listRelatives(all_curves[1:], parent=True))
    fibonacci_crv = mc.rename(mc.listRelatives(all_curves[0], parent=True), 'fibonacci')

    matrix_cam = mc.xform(camera, worldSpace=True, matrix=True, query=True)
    mc.xform(fibonacci_grp, worldSpace=True, matrix=matrix_cam)
    mc.makeIdentity(fibonacci_grp, apply=True, t=1, r=0, s=1, n=0)

    # Test

    mc.parent(fibonacci_crv, fibonacci_grp)
    mc.setAttr(fibonacci_grp + '.rx', -90)
    mc.setAttr(fibonacci_crv + '.tx', -0.5)
    mc.setAttr(fibonacci_crv + '.tz', -0.5)

    create_camera_node(camera, fibonacci_crv)

    isolate_transform = []
    if mc.listRelatives(mc.ls(type='mesh'), path=True, parent=True):
        isolate_transform = mc.listRelatives(mc.ls(type='mesh'), path=True, parent=True)

    isolate_transform.append(fibonacci_grp)
    mc.select(isolate_transform)

    currentState = mc.isolateSelect(panel, query=True, state=True)
    if currentState == 1:
        mc.isolateSelect(panel, state=0)
        mc.isolateSelect(panel, removeSelected=True)
        mc.isolateSelect(panel, state=1)
        mc.isolateSelect(panel, addSelected=True)
        mc.select(old_sel, r=True)
    else:
        mc.isolateSelect(panel, state=1)
        mc.isolateSelect(panel, addSelected=True)
        mc.select(old_sel, r=True)


def gen_fib_points(ratio):
    """Generator of the points on the fibonnaci curve.
    Each iteration returns the start point, center point and end point of
    the iteration quarter circle

    Yields:
        list, list, list
    """

    current_point = [0, 0]

    offset = 1.0

    cycle_cpt = 0

    while True:

        end_point = list(current_point)

        xdir = 1 if cycle_cpt in {0, 1} else -1
        ydir = 1 if cycle_cpt in {0, 3} else -1
        end_point[0] = current_point[0] + xdir * offset
        end_point[1] = current_point[1] + ydir * offset

        if cycle_cpt % 2:

            center_point = [current_point[0], end_point[1]]
        else:
            center_point = [end_point[0], current_point[1]]

        yield current_point, center_point, end_point

        current_point = end_point
        offset /= ratio
        cycle_cpt += 1
        cycle_cpt %= 4


def launch():
    if mc.window(LayoutTools.OBJECT_NAME, q=True, exists=True):
        mc.deleteUI(LayoutTools.OBJECT_NAME)

    lt = LayoutTools()
    lt.show()
    return lt


launch()
