# Partner-overlap audit of the ladder and splice pool (data building, DATA)

Lead's request 13 Nov 2026 (urgent), after a reviewer's finding on `/mnt/t7/smad_next/AR1/pool.csv`. Run 20:17-20:20
by the machine clock. Manifests and the builders' lists only: CPU, no image opened, no score read, no result
recomputed, no MEDS. Code `src/DATA/partner_overlap_audit.py`; counts `partner_overlap_tables.json` and
`partner_overlap_dev_test.json` (this folder); per-arm clean evaluation host lists on
`/mnt/t7/smad_next/DATA/overlap/` (FRGC / colorFERET subject ids stay there; this file gives counts only).

## Method

- **Rows.** Each training and evaluation row is resolved to its host persons, its other (partner) persons and the
  source photos it is made from, through the builders' own lists:
  - AR1 manifests (p1, p2 and the photos behind tem1 / tem2);
  - `AR1/pool.csv` (H, S, B per host). Splices: S4 = H + B, S3 = H + S, S0 = H. Warp-only toward the own second photo
    (R2w) = H + S landmarks; warp-only toward the partner shape (R2w4) = H + B landmarks;
  - the AF0 manifest (A, B; halfA = A only, halfB = B only);
  - SM1 halves (hA = H, hB = B);
  - the MS1 FFHQ lists, DG1 set B (src_a, src_b) and AG1 (photo_a, photo_b).
- **Landmarks.** Landmarks taken from a photo count as use of that photo.
- **Photo identity.** A photo is identified by the raw photo it comes from: colorFERET name through
  `dmad/data/maps/feret_map.csv`; FRGC still id from the r6 frame name or `r6_train_sources.csv`; AG1 through
  `photos.json`; mirrors map to the host photo.
- **Coverage.** Every row of every list resolved: 0 unresolved training ids, 0 unresolved evaluation ids, 0 unmapped
  photos. Benchmark cells are not in these development manifests.
- **Training lists.**
  - The FS1 block (Sb, the frozen candidate, seeds 403-407, with A and B).
  - All AB1 arms (overlay: SbZ, SbH, SbS, AS, Sp; x: Sbx; fm: SbFM; b2: SbR, SbnS0, SbnS3, SbH61, SbSp).
  - SE1 (SE).
- **Evaluation sets.** pn1_eval (FS1), ab1_eval, ab1x_eval (ladder, splices, AF0 fields, MS1 FFHQ hold-out, border
  rows, FFHQ landmark_combined) and the GD ladder (pr1_gd).
- **Positive control.** Treating the development ladder rows as if they were a training list, 2,718 of the 7,258
  test-host rows of ab1x_eval are flagged, so the check does detect sharing where it exists.

## Answer in one paragraph

**Training against evaluation: no overlap in any list.** For every training list above and every evaluation set:
- no evaluation row has a host or a partner who is a person of that training list;
- no evaluation row uses a source photo of that training list;
- every evaluation host is clean;
- no evaluation host's person component contains a training person.

How the training side stays closed:
- Training partners are all training hosts (0 partner-only persons in every list).
- 32 of the 156 training hosts have a test host as pool partner; none of their partner photos is in any training list
  (they carry no two-person training rows; Sb uses 124 hosts with a morph).
- **Corrected by the addendum below:** these 32 hosts do have S3 and S0 splice rows in Sb, and those rows use the test
  partner's landmarks (geometry only, no pixels). The "no overlap" statement holds for persons' pixels and photos, not
  for face shape.

**Within the evaluation sets the reviewer's finding holds:**
- 99 of the 191 read test hosts have a development host as partner;
- 99 of the 100 development hosts are partners of read test hosts;
- 51 development hosts have a test host as partner;
- the partner photo B is the partner's own S photo on all 536 pool hosts.

Consequences:
- 111 of the 191 test hosts have at least one evaluation row that contains a development person or photo; 80 are
  clean of development.
- 171 of the 191 read test hosts share a person component with a development host.
- Across training and evaluation together the FRGC / colorFERET person graph has 142
  components; the largest has 432 persons (sizes 1: 21, 2: 67, 3: 22, 4: 6, 5: 6, 7: 2, 8: 3, 9: 3, 10: 2, 11: 1, 12: 1, 14: 1, 15: 1, 23: 1, 40: 2, 53: 1, 127: 1, 432: 1).

## Development against test (ladder and splice rows of ab1x_eval)

| Quantity | Count |
|---|---|
| read test hosts | 191 |
| development hosts | 100 |
| read test hosts whose partner is a development host | 99 |
| development hosts that are the partner of a read test host | 99 |
| development hosts whose partner is a test host | 51 |
| test hosts with a row touching a development person or photo | 111 of 191 |
| read test hosts in a person component with a development host | 171 |
| persons / photos shared by development and test rows | 150 / 150 |

Test rows that touch development persons or photos, by family and rung:
- ladder|R0: 153
- ladder|R2w: 306
- ladder|R2w4: 222
- ladder|R3: 204
- ladder|R3m: 204
- ladder|R4: 444
- splice|R2w4_bg: 111
- splice|R2w4_face: 111
- splice|R2w_bg: 51
- splice|R2w_face: 51
- splice|R4_bg: 111
- splice|R4_face: 111
- splice|S0: 51
- splice|S0_bg: 51
- splice|S0_face: 51
- splice|S3: 51
- splice|S3_bg: 51
- splice|S3_face: 51
- splice|S4: 111
- splice|S4_bg: 111
- splice|S4_face: 111

Pool partner roles (host role -> partner role), all 536 hosts:
- dev host -> partner excluded: 49
- dev host -> partner test: 51
- excluded host -> partner test: 48
- excluded host -> partner train: 32
- test host -> partner dev: 100
- test host -> partner excluded: 31
- test host -> partner test: 69
- train host -> partner test: 32
- train host -> partner train: 124

## Tables per training list (rows of each evaluation set; any = host, partner or photo shared)

### Sb (FS1, seeds 403-407; frozen candidate)

Training file `PN1/fs_tree/pn1/data/manifests/train_Sb.csv` (sha256 2cf3fda3affc8dd3...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### A (FS1)

Training file `PN1/fs_tree/pn1/data/manifests/train_A.csv` (sha256 af070a60529db3e8...): 637 host persons, 0 partner-only persons, 798 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### B (FS1)

Training file `PN1/fs_tree/pn1/data/manifests/train_B.csv` (sha256 bd53dc3252a76767...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbH61 (AB1/b2)

Training file `AB1/b2/manifests/train_SbH61.csv` (sha256 0c8c253c890b2c76...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbR (AB1/b2)

Training file `AB1/b2/manifests/train_SbR.csv` (sha256 0c9ddfb719cdf630...): 625 host persons, 10 partner-only persons, 827 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbSp (AB1/b2)

Training file `AB1/b2/manifests/train_SbSp.csv` (sha256 07b9e6eab398a721...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbnS0 (AB1/b2)

Training file `AB1/b2/manifests/train_SbnS0.csv` (sha256 90d4a267c2101fbe...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbnS3 (AB1/b2)

Training file `AB1/b2/manifests/train_SbnS3.csv` (sha256 17009309bb904c69...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbFM (AB1/fm)

Training file `AB1/fm/manifests/train_SbFM.csv` (sha256 1231204496664287...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### AS (AB1/overlay_tree/pn1/data)

Training file `AB1/overlay_tree/pn1/data/manifests/train_AS.csv` (sha256 b7e9f3a33bcc547f...): 637 host persons, 0 partner-only persons, 798 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbH (AB1/overlay_tree/pn1/data)

Training file `AB1/overlay_tree/pn1/data/manifests/train_SbH.csv` (sha256 b8e17cd283510c66...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbS (AB1/overlay_tree/pn1/data)

Training file `AB1/overlay_tree/pn1/data/manifests/train_SbS.csv` (sha256 9c7e43ff30988897...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SbZ (AB1/overlay_tree/pn1/data)

Training file `AB1/overlay_tree/pn1/data/manifests/train_SbZ.csv` (sha256 9b4295546cf90bfb...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### Sp (AB1/overlay_tree/pn1/data)

Training file `AB1/overlay_tree/pn1/data/manifests/train_Sp.csv` (sha256 cf386dc7aaaee572...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### Sbx (AB1/x)

Training file `AB1/x/manifests/train_Sbx.csv` (sha256 4e403717df11a49f...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

### SE (SE1)

Training file `SE1/manifests/train_SE.csv` (sha256 c4e5aa474c87399d...): 637 host persons, 0 partner-only persons, 830 source photos; unresolved row ids: 0.

| Evaluation set | rows checked | host is a training person | partner is a training person | shares a training photo | any | clean hosts / hosts (by role) |
|---|---|---|---|---|---|---|
| pn1_eval (FS1) | 19797 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3000/3000; test 191/191 |
| ab1_eval | 21277 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| ab1x_eval | 24859 | 0 | 0 | 0 | 0 | af0_dev 115/115; dev 100/100; ffhq 3300/3300; test 191/191 |
| pr1_gd (GD ladder) | 11042 | 0 | 0 | 0 | 0 | af0_dev 5/5; dev 22/22; excluded 22/22; feret 5/5; ffhq 3000/3000; test 193/193 |

## Which reviewed results are affected in principle (nothing recomputed)

- **Not affected by training overlap.** These keep their training-side meaning:
  - "On new persons" reads: S4 against S3 and R4 against R3 on test or development hosts (PR1 part 1, AB1, SE1);
  - the test-host halves of the training-host against test-host splice margin;
  - the GD ladder reads (PR1 part 2);
  - the AF0 development and FFHQ landmark_combined reads.

  None of their evaluation persons or photos was trained on by Sb, A, B, any AB1 arm or SE.
- **Training-list probes** (reads on the training hosts' own rows, for example "26-37% of its own training same-person
  splices", the training-host margin) stay inside training persons. No training host's partner is an evaluation
  person, so these probes are not contaminated by evaluation rows.
- **Affected in principle: independence between development and test.**
  - Any rule fixed on development hosts and applied to test hosts shares photos and persons with them: 111 of 191 test
    hosts. Examples: a development threshold from ladder rows, a selection rule, a calibration, or "replicated on
    development and test".
  - A development read and a test read are therefore not independent replications.
  - In a test R4 or S4 row the second identity is, for 99 hosts, a development person whose own photo also appears in
    the development R3 and S3 rows.
- **Affected in principle: intervals.** Bootstrap intervals that resample hosts as independent units are
  anti-conservative. Hosts are linked through partners: within the evaluation pool, and across training and evaluation
  together, the person graph has a component of 432 persons.
- **Not affected:** anything read only on unseen-source sets (TT1, MEDS, CFD, KDEF, the MS1 FFHQ hold-out). This audit
  found no FRGC / colorFERET evaluation person in them.

## Files

- `src/DATA/partner_overlap_audit.py`.
- `experiments/DATA_builds/partner_overlap_tables.json`, `partner_overlap_dev_test.json` (counts).
- `/mnt/t7/smad_next/DATA/overlap/clean_eval_hosts.csv` (training list, evaluation set, host, role: every evaluation
  host, since all are clean of training).
- `/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv` (80 test hosts).


## Addendum (13 Nov 2026, 20:29-20:35 machine clock): record keeper's gaps

Code `src/DATA/partner_overlap_addendum.py`; it re-runs the audit and adds the items below. Counts are in
`partner_overlap_addendum.json`. Commit 681715d is not an audit commit (it carries the eye-distance measurement, the
D5 lists and the battery tables). The audit commit is 1b05940.

### (1) Positive control, now in code

The development ladder rows of ab1x_eval (role dev, fam ladder: 1700 rows) were treated as a training list:
2718 of the 7258 test-host rows share a host or partner person or a source photo with
them.

### (2) Unmapped photos

- Unmapped photos (keyed by path): 0 in every training list and 0 in every evaluation set.
- Every source frame on disk maps to a raw photo name: AR1 FERET 325, AR1 FRGC 1,281, AF0 FERET 652, AF0 FRGC 63, all
  mapped. FRGC frames named `a*.png` map through `r6_train_sources.csv` (copy in `volatile_backup_20261113`); the r6
  frames carry the still id in their name.
- I found no frame without a raw photo name. If the record keeper's 81 FRGC frames are `a*.png` frames looked up
  without `r6_train_sources.csv`, they are mapped here. They are not among unmapped photos, because there are none.
- The case where one raw photo is reached by two paths is handled: identity is the raw photo name, not the path.

### (3) Geometry sharing (shape without pixels)

Definitions from the builders:
- **7b splices** (`src/AR1/splice.py`, ARMS7B): every arm uses one hull drawn from the mean of the host's and the
  partner B's landmarks.
  - S4 = R4 pixels inside that hull on an R2w4 base;
  - S3 = R3 pixels inside it on an R2w base;
  - S0 = R2w pixels inside it on an R2w4 base, where R2w4 is the host warped to the host + partner mean shape.
- So S3 carries the partner's landmarks as the outline of its mask. S0 and S4 carry them in the warp of their base,
  and the blanked copies carry them in the mask.
- AR1 R2w4 and R4, the SM1 halves, and the AF0 / MS1 fields and halves use both persons of their pair. GAN and
  diffusion rows have no landmark geometry.

| Training list | rows | training rows whose geometry uses an evaluation person | of which | evaluation rows whose geometry uses a training person (incl. geometry persons) |
|---|---|---|---|---|
| Sb (FS1, seeds 403-407; frozen candidate) | 8386 | 64 | splice_S3 32, splice_S0 32 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| A (FS1) | 1992 | 0 | - | 0 |
| B (FS1) | 7762 | 0 | - | 0 |
| SbH61 (AB1/b2) | 8548 | 69 | splice_S3 34, splice_S0 35 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| SbR (AB1/b2) | 8424 | 71 | splice_S3 35, splice_S0 36 | pn1_eval (FS1) 1140, ab1_eval 1140, ab1x_eval 1140, pr1_gd (GD ladder) 246 |
| SbSp (AB1/b2) | 8560 | 0 | - | 0 |
| SbnS0 (AB1/b2) | 8074 | 32 | splice_S3 32 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| SbnS3 (AB1/b2) | 8074 | 32 | splice_S0 32 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| SbFM (AB1/fm) | 8946 | 64 | splice_S3 32, splice_S0 32 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| AS (AB1/overlay_tree/pn1/data) | 2850 | 0 | - | 0 |
| SbH (AB1/overlay_tree/pn1/data) | 7200 | 90 | splice_S3 44, splice_S0 46 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| SbS (AB1/overlay_tree/pn1/data) | 8692 | 72 | splice_S3 36, splice_S0 36 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| SbZ (AB1/overlay_tree/pn1/data) | 7868 | 73 | splice_S3 36, splice_S0 37 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| Sp (AB1/overlay_tree/pn1/data) | 7762 | 0 | - | 0 |
| Sbx (AB1/x) | 10484 | 75 | splice_S3 38, splice_S0 37 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |
| SE (SE1) | 10046 | 64 | splice_S3 32, splice_S0 32 | pn1_eval (FS1) 1216, ab1_eval 1216, ab1x_eval 1216, pr1_gd (GD ladder) 265 |

**The 32 training hosts whose pool partner is a test host, in the Sb training list:**
- Row kinds: lad_R0 32, lad_R2w 32, lad_S3 32, lad_S0 32. All are negatives (label 0); there is no R4 and no S4.
- All 32 S3 and all 32 S0 rows use the partner's landmarks. The partners are 32 distinct test hosts, all of them read
  test hosts. The lad_R0 and lad_R2w rows do not use them.
- The same 32 links appear in every arm that keeps Sb's S3 and S0 rows: SbZ, SbS, SbH, SbH61, SbR, SbFM, Sbx and SE.
  SbnS0 keeps only S3, SbnS3 keeps only S0.
- Arms without these rows have 0: A, B, AS, Sp, SbSp.
- The extra rows in some arms (for example SbH 90) are repeated rows of the same 32 hosts.
- The reverse counts (1,216 evaluation rows; 265 GD rows) are the evaluation rows of these same 32 test persons, so
  they are not a separate link.

**What this means for the reads "on new persons":**
- For the 32 read test hosts above, Sb (and the arms listed) saw their face shape during training: the landmark
  geometry of the S0 base warp and the S3 / S0 hull outline. Sb never saw their pixels or photos.
- This is a shape-only link, not an appearance link. It lives in negatives (label 0) of training hosts whose own
  pixels fill the image.
- A read that treats these 32 test hosts as fully new persons is, for those hosts, new in appearance but not in
  landmark shape. The 159 other read test hosts and all development hosts have no such link.
- No result is recomputed here. A sensitivity read without these 32 hosts would separate the two. That needs an owner
  amendment.
