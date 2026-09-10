bl_info = {
    "name": "BlendTrace",
    "author": "BlendTrace contributors",
    "version": (0, 2, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > BlendTrace",
    "description": "Shows an offline modeling timeline with a semantic viewport cursor",
    "category": "3D View",
}

import bpy
import blf
import gpu
from bpy.props import BoolProperty, CollectionProperty, IntProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader


_EXPLANATIONS = {
    "Move": "移动对象或几何元素的位置。",
    "Translate": "移动对象或几何元素的位置。",
    "Resize": "缩放对象或几何元素。",
    "Scale": "缩放对象或几何元素。",
    "Rotate": "旋转对象或几何元素。",
    "Extrude": "从选中的几何元素向外延伸，生成新的几何。",
    "Inset": "在选中面内部创建一圈新的边界。",
    "Bevel": "给边或顶点增加倒角，使转折更柔和。",
    "Loop Cut": "添加环切线，便于控制模型结构与形状。",
    "Subdivide": "把已有几何细分成更多面。",
    "Delete": "删除当前选中的对象或几何元素。",
    "Duplicate": "复制当前对象或几何元素。",
    "Add Cube": "添加一个立方体基础体。",
    "Add UV Sphere": "添加一个 UV 球体基础体。",
    "Add Cylinder": "添加一个圆柱体基础体。",
}

_draw_handle = None


def explain(label: str) -> str:
    for key, text in _EXPLANATIONS.items():
        if key.casefold() in label.casefold():
            return text
    return "记录了一个 Blender 操作。可结合当前对象与上下文理解这一步的作用。"


def _wrap(text: str, width: int = 34):
    if not text:
        return [""]
    return [text[i : i + width] for i in range(0, len(text), width)]


def _tag_redraw_view3d():
    try:
        wm = bpy.context.window_manager
        for window in wm.windows:
            screen = window.screen
            if not screen:
                continue
            for area in screen.areas:
                if area.type == "VIEW_3D":
                    area.tag_redraw()
    except (AttributeError, ReferenceError, RuntimeError):
        pass


def _draw_semantic_cursor():
    """Draw an in-viewport teaching cursor at the active object's origin.

    Privacy/safety boundary: this reads only Blender runtime state already visible
    in the current scene. It does not read OS mouse coordinates, files, clipboard,
    network resources, credentials, or external applications.
    """
    try:
        context = bpy.context
        wm = context.window_manager
        if not getattr(wm, "bt_show_cursor", True):
            return
        if not getattr(wm, "bt_recording", False):
            return
        if not getattr(wm, "bt_items", None):
            return

        region = context.region
        rv3d = context.region_data
        obj = context.active_object
        if region is None or rv3d is None or obj is None:
            return

        screen_pos = view3d_utils.location_3d_to_region_2d(
            region, rv3d, obj.matrix_world.translation
        )
        if screen_pos is None:
            return

        x = float(screen_pos.x)
        y = float(screen_pos.y)
        if x < 0 or y < 0 or x > region.width or y > region.height:
            return

        # A small semantic cursor: ring + pointer stem. It marks the object being
        # discussed; it is not a captured or mirrored system mouse cursor.
        radius = 11.0
        segments = 28
        ring = []
        import math

        for i in range(segments + 1):
            angle = (i / segments) * math.tau
            ring.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))

        stem = [(x + 8.0, y - 8.0), (x + 24.0, y - 24.0)]
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        gpu.state.blend_set("ALPHA")
        gpu.state.line_width_set(2.0)

        shader.bind()
        shader.uniform_float("color", (1.0, 1.0, 1.0, 0.92))
        batch_for_shader(shader, "LINE_STRIP", {"pos": ring}).draw(shader)
        batch_for_shader(shader, "LINES", {"pos": stem}).draw(shader)

        gpu.state.line_width_set(1.0)
        gpu.state.blend_set("NONE")

        active_index = int(getattr(wm, "bt_active_index", -1))
        if 0 <= active_index < len(wm.bt_items):
            label = wm.bt_items[active_index].label
            font_id = 0
            blf.size(font_id, 13)
            blf.position(font_id, x + 30.0, y - 30.0, 0)
            blf.color(font_id, 1.0, 1.0, 1.0, 0.95)
            blf.draw(font_id, label[:64])
    except (AttributeError, ReferenceError, RuntimeError, TypeError, ValueError):
        # Drawing failure must never modify the scene or block normal Blender use.
        return


class BT_TraceItem(PropertyGroup):
    label: StringProperty(name="Operation")
    explanation: StringProperty(name="Explanation")
    object_name: StringProperty(name="Object")


class BT_OT_tracker(Operator):
    bl_idname = "blendtrace.tracker"
    bl_label = "BlendTrace Background Tracker"
    bl_options = {"INTERNAL"}

    _timer = None

    def modal(self, context, event):
        wm = context.window_manager

        if not getattr(wm, "bt_tracker_running", False):
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER" and wm.bt_recording:
            try:
                stack = wm.undo_stack
                active = stack.active if stack else None
                active_index = stack.active_index if stack and active else -1

                if active and active_index != wm.bt_last_undo_index:
                    item = wm.bt_items.add()
                    item.label = active.name or "Unnamed operation"
                    item.explanation = explain(item.label)
                    obj = context.active_object
                    item.object_name = obj.name if obj else "—"

                    wm.bt_last_undo_index = active_index
                    wm.bt_active_index = len(wm.bt_items) - 1
                    _tag_redraw_view3d()
            except (AttributeError, ReferenceError, RuntimeError):
                pass

        return {"PASS_THROUGH"}

    def execute(self, context):
        wm = context.window_manager
        if wm.bt_tracker_running:
            return {"CANCELLED"}

        wm.bt_tracker_running = True
        self._timer = wm.event_timer_add(0.35, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer is not None:
            try:
                wm.event_timer_remove(self._timer)
            except (ReferenceError, RuntimeError):
                pass
            self._timer = None
        wm.bt_tracker_running = False
        _tag_redraw_view3d()


class BT_OT_start(Operator):
    bl_idname = "blendtrace.start"
    bl_label = "Start Recording"
    bl_description = "Start local operation recording"

    def execute(self, context):
        wm = context.window_manager

        try:
            stack = wm.undo_stack
            wm.bt_last_undo_index = stack.active_index if stack and stack.active else -1
        except (AttributeError, ReferenceError, RuntimeError):
            wm.bt_last_undo_index = -1

        wm.bt_recording = True
        if not wm.bt_tracker_running:
            bpy.ops.blendtrace.tracker("INVOKE_DEFAULT")
        _tag_redraw_view3d()
        self.report({"INFO"}, "BlendTrace recording started")
        return {"FINISHED"}


class BT_OT_stop(Operator):
    bl_idname = "blendtrace.stop"
    bl_label = "Stop Recording"
    bl_description = "Stop local operation recording"

    def execute(self, context):
        context.window_manager.bt_recording = False
        _tag_redraw_view3d()
        self.report({"INFO"}, "BlendTrace recording stopped")
        return {"FINISHED"}


class BT_OT_clear(Operator):
    bl_idname = "blendtrace.clear"
    bl_label = "Clear"
    bl_description = "Clear the local trace list"

    def execute(self, context):
        wm = context.window_manager
        wm.bt_items.clear()
        wm.bt_active_index = 0
        _tag_redraw_view3d()
        return {"FINISHED"}


class BT_UL_trace_list(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        row = layout.row(align=True)
        row.label(text=f"{index + 1:02d}")
        row.label(text=item.label, icon="DOT")


class BT_PT_panel(Panel):
    bl_label = "BlendTrace"
    bl_idname = "BT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendTrace"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        row = layout.row(align=True)
        if wm.bt_recording:
            row.operator("blendtrace.stop", text="Stop", icon="PAUSE")
        else:
            row.operator("blendtrace.start", text="Start Recording", icon="REC")
        row.operator("blendtrace.clear", text="Clear", icon="TRASH")

        layout.prop(wm, "bt_show_cursor", text="Semantic Cursor", icon="RESTRICT_VIEW_OFF")
        layout.label(text="Local only • No network", icon="LOCKED")
        layout.separator()

        layout.template_list(
            "BT_UL_trace_list",
            "",
            wm,
            "bt_items",
            wm,
            "bt_active_index",
            rows=6,
        )

        if 0 <= wm.bt_active_index < len(wm.bt_items):
            item = wm.bt_items[wm.bt_active_index]
            box = layout.box()
            box.label(text=item.label, icon="INFO")
            box.label(text=f"Object: {item.object_name}")
            col = box.column(align=True)
            for line in _wrap(item.explanation):
                col.label(text=line)

        layout.separator()
        layout.label(text="v0.2.0 • offline semantic cursor")


classes = (
    BT_TraceItem,
    BT_OT_tracker,
    BT_OT_start,
    BT_OT_stop,
    BT_OT_clear,
    BT_UL_trace_list,
    BT_PT_panel,
)


def register():
    global _draw_handle

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.bt_items = CollectionProperty(type=BT_TraceItem)
    bpy.types.WindowManager.bt_active_index = IntProperty(default=0)
    bpy.types.WindowManager.bt_recording = BoolProperty(default=False)
    bpy.types.WindowManager.bt_tracker_running = BoolProperty(default=False)
    bpy.types.WindowManager.bt_last_undo_index = IntProperty(default=-1)
    bpy.types.WindowManager.bt_show_cursor = BoolProperty(
        name="Semantic Cursor",
        description="Show a local viewport teaching cursor at the active object's origin",
        default=True,
        update=lambda self, context: _tag_redraw_view3d(),
    )

    if _draw_handle is None:
        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_semantic_cursor, (), "WINDOW", "POST_PIXEL"
        )


def unregister():
    global _draw_handle

    try:
        bpy.context.window_manager.bt_recording = False
        bpy.context.window_manager.bt_tracker_running = False
    except (AttributeError, ReferenceError, RuntimeError):
        pass

    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, "WINDOW")
        except (ReferenceError, RuntimeError):
            pass
        _draw_handle = None

    for prop in (
        "bt_show_cursor",
        "bt_last_undo_index",
        "bt_tracker_running",
        "bt_recording",
        "bt_active_index",
        "bt_items",
    ):
        if hasattr(bpy.types.WindowManager, prop):
            delattr(bpy.types.WindowManager, prop)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    _tag_redraw_view3d()


if __name__ == "__main__":
    register()
