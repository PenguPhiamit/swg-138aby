"""swgfmt: our SWG client-format tools in one place (Fable T1, 14 Oct 2026).

    sys.path.insert(0, '<...>/outputs/tools'); from swgfmt import swg_tables, trn_iff, tre_write, ui_inc, fmt_tools, hoth_ui, ws_read

swg_tables   CSTB / DTII / STF readers and writers, SOE CRC          trn_iff   IFF parse/build, TRE reading, the client's load order
tre_write    TRE writer                                               ui_inc    planet blocks for the two UI includes
fmt_tools    the builder's call shapes (stf/dt/cstb/tre_pack, read_tre, walk_tres)   hoth_ui   Hoth's UI blocks   ws_read   .ws snapshots
The old module paths (Fable-*/tools/<name>.py) are shims that hand their imports to these files.
"""
