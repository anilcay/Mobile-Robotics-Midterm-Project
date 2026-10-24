"""Helpers for building SeraBot link meshes in Blender with bmesh.

Runs inside Blender (imported by the build scripts sent through the bridge).
Each link is one mesh object whose origin is the URDF link frame
(docs/INTERFACES.md section 4.1): X forward, Y left, Z up, metres.
"""

import math
import os
from typing import Iterable, List, Optional, Sequence, Tuple

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

Vec3 = Tuple[float, float, float]


def srgb(r: float, g: float, b: float) -> Vec3:
    """Convert display (sRGB) colour values to the linear values Blender stores."""
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b))


def material(name: str, rgb: Vec3, roughness: float = 0.6,
             metallic: float = 0.0) -> bpy.types.Material:
    """Return a Principled BSDF material with a plain base colour (linear RGB)."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    # Single-sided (glTF doubleSided=false): sensors sitting inside their own housing
    # must not see its inner faces in Gazebo.
    mat.use_backface_culling = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    mat.diffuse_color = (*rgb, 1.0)
    return mat


def transform(loc: Vec3 = (0, 0, 0), rot: Vec3 = (0, 0, 0),
              scale: Vec3 = (1, 1, 1), order: str = 'XYZ') -> Matrix:
    """Location / euler rotation / scale as one matrix."""
    return (Matrix.Translation(Vector(loc)) @ Euler(rot, order).to_matrix().to_4x4()
            @ Matrix.Diagonal((*scale, 1.0)))


class LinkMesh:
    """Accumulates primitives with per-part materials into one bmesh."""

    def __init__(self, name: str):
        self.name = name
        self.bm = bmesh.new()
        self.materials: List[bpy.types.Material] = []

    def _finish(self, verts: Sequence, mat, smooth: bool, matrix: Matrix) -> List:
        bmesh.ops.transform(self.bm, matrix=matrix, verts=list(verts))
        if mat not in self.materials:
            self.materials.append(mat)
        index = self.materials.index(mat)
        faces = {f for v in verts for f in v.link_faces}
        for f in faces:
            f.material_index = index
            f.smooth = smooth
        return list(faces)

    def box(self, size: Vec3, mat, loc: Vec3 = (0, 0, 0), rot: Vec3 = (0, 0, 0),
            bevel: float = 0.0) -> List:
        verts = bmesh.ops.create_cube(self.bm, size=1.0)['verts']
        bmesh.ops.scale(self.bm, vec=Vector(size), verts=verts)
        if bevel > 0:
            edges = list({e for v in verts for e in v.link_edges})
            res = bmesh.ops.bevel(self.bm, geom=verts + edges, offset=bevel, segments=2,
                                  affect='EDGES', profile=0.5)
            verts = list(set(verts) | set(res['verts']))
            verts = [v for v in verts if v.is_valid]
        return self._finish(verts, mat, bevel > 0, transform(loc, rot))

    def cylinder(self, r_bottom: float, r_top: float, depth: float, mat,
                 loc: Vec3 = (0, 0, 0), rot: Vec3 = (0, 0, 0), segments: int = 32,
                 smooth: bool = True) -> List:
        """Cylinder or cone along local Z, centred on loc."""
        verts = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=segments,
                                      radius1=r_bottom, radius2=r_top, depth=depth)['verts']
        return self._finish(verts, mat, smooth, transform(loc, rot))

    def ellipsoid(self, radii: Vec3, mat, loc: Vec3 = (0, 0, 0), rot: Vec3 = (0, 0, 0),
                  segments: int = 24, rings: int = 12, order: str = 'XYZ') -> List:
        verts = bmesh.ops.create_uvsphere(self.bm, u_segments=segments, v_segments=rings,
                                          radius=1.0)['verts']
        return self._finish(verts, mat, True, transform(loc, rot, radii, order))

    def loft(self, rings: Sequence[Tuple[float, Sequence[Tuple[float, float]]]], mat,
             cap_bottom: bool = True, cap_top: bool = True, smooth: bool = True,
             matrix: Optional[Matrix] = None, cap_mat=None) -> List:
        """Skin closed XY outlines placed at increasing Z (same point count each).

        cap_mat, if given, is used for the top cap instead of mat.
        """
        loops = [[self.bm.verts.new((x, y, z)) for x, y in pts] for z, pts in rings]
        n = len(loops[0])
        for a, b in zip(loops, loops[1:]):
            for i in range(n):
                j = (i + 1) % n
                self.bm.faces.new((a[i], a[j], b[j], b[i]))
        bottom = self.bm.faces.new(list(reversed(loops[0]))) if cap_bottom else None
        top = self.bm.faces.new(loops[-1]) if cap_top else None
        verts = [v for loop in loops for v in loop]
        faces = self._finish(verts, mat, smooth, matrix or Matrix.Identity(4))
        for cap in (bottom, top):
            if cap is not None:
                cap.smooth = False
        if top is not None and cap_mat is not None:
            if cap_mat not in self.materials:
                self.materials.append(cap_mat)
            top.material_index = self.materials.index(cap_mat)
        return faces

    def revolve(self, profile: Sequence[Tuple[float, float]], mat, segments: int = 48,
                loc: Vec3 = (0, 0, 0), rot: Vec3 = (0, 0, 0), smooth: bool = True) -> List:
        """Revolve an open (radius, z) profile about local Z; ends on the axis close it."""
        loops = []
        for k in range(segments):
            a = 2 * math.pi * k / segments
            loops.append([self.bm.verts.new((r * math.cos(a), r * math.sin(a), z))
                          for r, z in profile])
        for k in range(segments):
            a, b = loops[k], loops[(k + 1) % segments]
            for i in range(len(profile) - 1):
                quad = (a[i], b[i], b[i + 1], a[i + 1])
                if len({v.co.to_tuple(6) for v in quad}) >= 3:
                    self.bm.faces.new(quad)
        bmesh.ops.remove_doubles(self.bm, verts=[v for loop in loops for v in loop],
                                 dist=1e-7)
        verts = [v for loop in loops for v in loop if v.is_valid]
        return self._finish(verts, mat, smooth, transform(loc, rot))

    def to_object(self, collection: bpy.types.Collection) -> bpy.types.Object:
        """Create (or replace) the mesh object with its origin at the link frame."""
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        old = bpy.data.objects.get(self.name)
        if old is not None:
            bpy.data.objects.remove(old)
        mesh = bpy.data.meshes.get(self.name) or bpy.data.meshes.new(self.name)
        # Clear slots before writing geometry: clearing afterwards drops material indices.
        mesh.materials.clear()
        mesh.clear_geometry()
        self.bm.to_mesh(mesh)
        self.bm.free()
        for mat in self.materials:
            mesh.materials.append(mat)
        obj = bpy.data.objects.new(self.name, mesh)
        collection.objects.link(obj)
        return obj


def rounded_rect(length: float, width: float, radius: float,
                 corner_segments: int = 6) -> List[Tuple[float, float]]:
    """Counter-clockwise rounded rectangle centred on the origin."""
    radius = min(radius, length / 2, width / 2)
    hx, hy = length / 2 - radius, width / 2 - radius
    pts = []
    for cx, cy, start in ((hx, hy, 0), (-hx, hy, 90), (-hx, -hy, 180), (hx, -hy, 270)):
        for k in range(corner_segments + 1):
            a = math.radians(start + 90 * k / corner_segments)
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts


def collection(name: str, clear: bool = True) -> bpy.types.Collection:
    """Return a scene collection, optionally emptied."""
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    if clear:
        for obj in list(coll.objects):
            bpy.data.objects.remove(obj)
    return coll


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objects)


def _select_only(obj: bpy.types.Object) -> None:
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def export_glb(obj: bpy.types.Object, path: str, yup: bool = True) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _select_only(obj)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=yup, export_materials='EXPORT',
                              export_animations=False, export_cameras=False,
                              export_lights=False)
    return path


def export_obj(obj: bpy.types.Object, path: str) -> str:
    """OBJ + MTL with Blender axes kept as-is (Z up, Y forward = identity)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _select_only(obj)
    bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, forward_axis='Y',
                          up_axis='Z', export_materials=True, apply_modifiers=True,
                          export_triangulated_mesh=True, path_mode='STRIP')
    return path
