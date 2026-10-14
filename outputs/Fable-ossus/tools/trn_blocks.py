"""Chunk writers for the .trn pieces the Ossus prototype did not need: flora, radial and bitmap families, the
filters (height, fractal, slope, bitmap), flora/radial affectors, exclusion, polyline boundaries and roads with
height data. Our own code (Fable, 14 Oct 2026). Field order follows Core3-dev src/terrain/** (what the server
reads) and the stock 0014 files byte for byte (checked with Fable-planet-test/tools/trn_read.py on every stock
planet; the one chunk where the stock files carry more than Core3 reads, FBIT, is written stock-length).
Reuses the prototype's building blocks from ../../Fable-planet-test/tools/trn_write.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'Fable-planet-test', 'tools'))
from trn_iff import Writer, chunk, form  # noqa: E402
from trn_write import (affector_environment, affector_height_constant, affector_height_fractal,  # noqa: E402,F401
                       affector_shader_constant, boundary_circle, boundary_rect, environment_family, fractal,
                       header_chunk, ihdr, layer, maps_form, shader_family)


# ---------------------------------------------------------------- families

def flora_family(fid, name, rgb, density, children, floats_on_water=0):
    """FFAM (FGRP 0008). children: (appearance, weight, align_to_terrain, displacement, period, sway, scale,
    min_scale, max_scale); the stock values are 1/0.1/0.5/1/0/1/1 for a tree."""
    w = Writer().i32(fid).cstr(name).u8(rgb[0]).u8(rgb[1]).u8(rgb[2]).f32(density).u32(floats_on_water).i32(len(children))
    for c in children:
        app, weight, align, disp, period, sway, scale, mn, mx = c
        w.cstr(app).f32(weight).u32(align).f32(disp).f32(period).u32(sway).i32(scale).f32(mn).f32(mx)
    return chunk('FFAM', w.bytes())


def tree(appearance, weight=1.0, align=0, displacement=0.0, period=0.0, sway=0, scale=1, min_scale=0.9, max_scale=1.2):
    return (appearance, weight, align, displacement, period, sway, scale, min_scale, max_scale)


def radial_family(fid, name, rgb, density, children):
    """RFAM (RGRP 0003). children: (shader, weight, distance, min_width, max_width, maintain_aspect, min_height,
    max_height, align_to_terrain, var9)."""
    w = Writer().i32(fid).cstr(name).u8(rgb[0]).u8(rgb[1]).u8(rgb[2]).f32(density).i32(len(children))
    for c in children:
        sh, weight, dist, mnw, mxw, aspect, mnh, mxh, align, v9 = c
        w.cstr(sh).f32(weight).f32(dist).f32(mnw).f32(mxw).i32(aspect).f32(mnh).f32(mxh).i32(align).u32(v9)
    return chunk('RFAM', w.bytes())


def radial(shader, weight=1.0, distance=30.0, min_width=1.0, max_width=1.5, aspect=1, min_height=1.0, max_height=1.5, align=0):
    return (shader, weight, distance, min_width, max_width, aspect, min_height, max_height, align, 0)


def bitmap_family(bid, name, tga):
    """MFAM in the second MGRP (bitmaps): DATA id, name, file (a greyscale TGA in the client archives)."""
    return form('MFAM', chunk('DATA', Writer().i32(bid).cstr(name).cstr(tga).bytes()))


# ---------------------------------------------------------------- filters

def filter_height(name, lo, hi, feather_type=1, feather=0.3):
    return form('FHGT', form('0002', ihdr(True, name), chunk('DATA', Writer().f32(lo).f32(hi).i32(feather_type).f32(feather).bytes())))


def filter_fractal(name, fractal_id, lo, hi, feather_type=3, feather=0.3, scale=1.0):
    parm = Writer().i32(fractal_id).i32(feather_type).f32(feather).f32(lo).f32(hi).f32(scale).bytes()
    return form('FFRA', form('0005', ihdr(True, name), form('DATA', chunk('PARM', parm))))


def filter_slope(name, min_deg, max_deg, feather_type=0, feather=0.2):
    """Client only: Core3's FilterSlope contributes no height transform (Fable-planet-test README, 3b)."""
    return form('FSLP', form('0002', ihdr(True, name), chunk('DATA', Writer().f32(min_deg).f32(max_deg).i32(feather_type).f32(feather).bytes())))


def filter_bitmap(name, bitmap_id, lo=0.0, hi=1.0, feather_type=0, feather=0.0, gain=0.0):
    """24 bytes like the stock/MTG files (Core3 reads the first 20; the last float is the gain the client uses)."""
    parm = Writer().i32(bitmap_id).i32(feather_type).f32(feather).f32(lo).f32(hi).f32(gain).bytes()
    return form('FBIT', form('0000', ihdr(True, name), form('DATA', chunk('PARM', parm))))


# ---------------------------------------------------------------- affectors

def _flora_affector(tag, version, name, family_id, op=1, remove_all=0, feather_type=0, feather=1.0):
    data = Writer().i32(family_id).i32(op).i32(remove_all).i32(feather_type).f32(feather).bytes()
    return form(tag, form(version, ihdr(True, name), chunk('DATA', data)))


def affector_flora_collidable(name, family_id, **kw):
    return _flora_affector('AFSC', '0004', name, family_id, **kw)


def affector_flora_non_collidable(name, family_id, **kw):
    return _flora_affector('AFSN', '0004', name, family_id, **kw)


def affector_radial_near(name, family_id, **kw):
    return _flora_affector('AFDN', '0002', name, family_id, **kw)


def affector_radial_far(name, family_id, **kw):
    return _flora_affector('AFDF', '0002', name, family_id, **kw)


def affector_exclude(name):
    return form('AEXC', form('0000', ihdr(True, name), chunk('DATA', b'')))


def affector_road(name, points, segments, width, family_id, feather_type=3, feather=0.15, feather_shader=3,
                  feather_shader_distance=0.15):
    """AROA 0005 with HDTA height data. points: [(x, y), ...] the road's control points; segments: one list of
    (x, z, y) per leg, each starting at the leg's first control point (Segment::hasInitialCoordinate matches the
    rectangle's start point exactly), with z = the road surface height Core3 and the client use."""
    sgmts = [chunk('SGMT', b''.join(Writer().f32(x).f32(z).f32(y).bytes() for x, z, y in seg)) for seg in segments]
    hdta = form('HDTA', form('0001', *sgmts))
    w = Writer().i32(len(points))
    for x, y in points:
        w.f32(x).f32(y)
    w.f32(width).i32(family_id).i32(feather_type).f32(feather).i32(feather_shader).f32(feather_shader_distance)
    return form('AROA', form('0005', ihdr(True, name), form('DATA', hdta, chunk('DATA', w.bytes()))))


def boundary_polyline(name, points, line_width, feather_type=0, feather=0.0):
    w = Writer().i32(len(points))
    for x, y in points:
        w.f32(x).f32(y)
    w.i32(feather_type).f32(feather).f32(line_width)
    return form('BPLN', form('0001', ihdr(True, name), chunk('DATA', w.bytes())))
