# SWG content warning inventory

October 13, 2026. Read-only archive index audit.

All 51 configured server archives are present. Thirty-five distinct paths appeared in the audited startup warnings. A file can be present but unsupported by a server parser.

The scan decoded 116 version-0005 archives across the server set and original disc; it did not decode 59 newer version-0006 original disc archives. “No match” below applies only to decoded archives.

| Warning path | Index evidence | Interpretation |
|---|---|---|
| `appearance/corellian_corvette_pob.pob` | No match in decoded indexes | Unresolved object/effect/template reference; investigate specific usage |
| `appearance/godclient_cylinder_30.apt` | No match in decoded indexes | Referenced by developer/no-build marker templates; likely helper asset |
| `appearance/particle_test_31.prt` | No match in decoded indexes | Unresolved object/effect/template reference; investigate specific usage |
| `appearance/pt_light_indoor_glow.prt` | Loaded `patch_07.tre`; `PEFT` particle form | Present; server leaves particle form uninstantiated |
| `appearance/thed_wter_falls_anim1.apt` | No match in decoded indexes | Unresolved object/effect/template reference; investigate specific usage |
| `clientdata/ship/client_shared_blacksun_transport.cdf` | No match in decoded indexes | Ship client-data lookup; collision/attachment data needs review |
| `clientdata/ship/client_shared_escape_pod.cdf` | No match in decoded indexes | Ship client-data lookup; collision/attachment data needs review |
| `clientdata/ship/client_shared_hutt_transport.cdf` | No match in decoded indexes | Ship client-data lookup; collision/attachment data needs review |
| `datatables/space/ship_chassis_arc170.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_blacksun_medium_s01.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_blacksun_medium_s02.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_blacksun_medium_s03.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_blacksun_medium_s04.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_blacksun_transport.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_generic.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_hutt_turret_ship.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_merchant_cruiser_light.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_merchant_cruiser_medium.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_mining_asteroid_dynamic.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_mining_asteroid_static.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_player_arc170.iff` | Original disc `patch_15_00.tre`; Original disc `patch_17_00.tre` | Later-patch asset outside configured pre-CU set; compatibility review needed |
| `datatables/space/ship_chassis_player_jedi_starfighter.iff` | Original disc `patch_15_00.tre`; Original disc `patch_17_00.tre` | Later-patch asset outside configured pre-CU set; compatibility review needed |
| `datatables/space/ship_chassis_player_test_falcon.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_rebel_shuttle.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_smuggler_warlord_ship.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_tiedefender.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_tiedefender_tier1.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_tiedefender_tier2.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_tiedefender_tier3.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_tiedefender_tier4.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_tiedefender_tier5.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `datatables/space/ship_chassis_transport_science.iff` | No match in decoded indexes | Ship hardpoint lookup; loader tolerates absent table; ship support unverified |
| `object/tangible/component/vehicle/base/base_vehicle.iff` | No match in decoded indexes | Unresolved object/effect/template reference; investigate specific usage |
| `object/tangible/component/vehicle/base/shared_base_vehicle.iff` | No match in decoded indexes | Unresolved object/effect/template reference; investigate specific usage |
| `snapshot/tutorial.ws` | No match in decoded indexes | Snapshot is optional in loader; tutorial is created by screenplay |

The “expected SHOT, found SSHP” template warnings and Mantis credential error are separate from these missing-path rows. See SWG-content-research.md for their assessment.
