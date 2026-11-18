# Local HQ identity mapping: bounded audit, 14 November2026

Verdict: **NOT ADMITTED — no authoritative local-image-to-CelebA mapping is established.** This is a provenance blocker for the localHQ arm, not a scientific no-go on lookalike yield. No label was assigned, no FRembedding used, no mining/GPU run, no large download or Googlequota retry performed.

## Established evidence

1. Official PGGAN source at commit2504c3f3cb98ca58751610ad61fa1097313152bd defines final_md5 over RGB uint8 CHW bytes AFTER adding the decrypted correction. proc_md5 is the correspondingpre-correctionCHWchecksum. PNGcontainerbytes are not thedefinition. Thus root's decodedRGBCHWcheck used the correct finalrepresentation. OfficialTFRecordexport shuffles using RandomState123; extractionorder is not inherently mappingindexorder. [Official source](https://github.com/tkarras/progressive_growing_of_gans/blob/2504c3f3cb98ca58751610ad61fa1097313152bd/dataset_tool.py#L512)
2. The localZIP's recordedSHA256bda2d6f0df08f6362057224e1007d3eacfd603f5f5cb67475451c7284e11eb2d matches liveHF LFSobjectSHA; bothsizes33948106021bytes. The previousMS1preparer explicitly verified thathash before creatingzip_sha_ok, whose recordedvalue also agrees. This audit did NOT reread33.9GB to produce a fresh fullarchivehash. The source remains the thirdpartyIceclearmirror, not theofficialrelease. [Mirror file](https://huggingface.co/datasets/Iceclear/CelebA-HQ1024/blob/main/CelebA-HQ-1024.zip)
3. ZIPcentraldirectory:30001members includingonedirectory;30000uniquePNGfilenames,00001..30000; nozero-lengthfile, duplicatefilename, embeddedmapping/README orZIPcomment. This does not prove all30000images valid/distinct. Mirrorcard explicitly says oneimage wasmissing due touploaderror; its report is not resolved by filenamecount. [Mirror card](https://huggingface.co/datasets/Iceclear/CelebA-HQ1024/blob/main/README.md)
4. Twelvefixedsampleindices1,2,17,101,1000,5000,10000,15000,20000,25000,29999,30000 decoded successfully as1024RGB. For each,51representations(rawPNG,RGBHWC,officialRGBCHW and all48losslesschannelpermutation/axisflip/swapCHWforms) were compared against BOTH all30000officialproc_md5 andfinal_md5 entries. **Zeroexactmatches.** This rulesout these simple byte/layout explanations in thesamples, not everypossibletransformation or everyarchiveimage. No similarity-basedcorrespondence wasattempted. Audit6.34seconds; source and results saved.
5. ExistingMS1celebahq_prep.py uses `idx=Path(zipmember).stem`, writes frames/keys withthatstem and logs index00001,00002,... . Those are localZIPkeys, NOT established officialHQindices. Neither joiningdirectly to0-basedPGGANidx nor subtracting1 is authorized. The existingofficialjoin's70missingprocessedCelebArows is a valid statement about thePGGANlist; its50-numbered-key overlap withlocalembeddings cannot establish thoseimages' identities while correspondence is unresolved. Embeddingcomponentlabels are not identitytruth.

## Executable options

- **Immediate admittedroute:** proceed with separatelyregistered labelled128pxCelebA tailcalibration using authoritativeoriginalimage_id→person_id labels. It answers lowresolutiontailfeasibility; it cannot be calledHQconstruction or establish the localHQmapping. Root/Sol own thatregisteredcalibration; no newmining is authorized by thisaudit.
- **To use this exactlocalZIP:** require an uploader/officialsource provenance bridge identifying exactoriginalimage IDs for theseexactPNGbytes, or a documentedreversible transformation yielding exactofficialproc/finalchecksums. An officialCelebAMask-HQ mapping alone cannot prove thatIceclear used itsnumbering. Do not substitute visual/embeddingnearest-neighbor guesses.
- **To replace thissource:** reconstruct an admittedsubset using theofficialPGGANpipeline with exactoriginalCelebAJPEGs, landmarks and encryptedcorrectionshards, preserving per-imagefinal_md5 and officialidx/orig_file, or acquire an independentlyverifiedofficialimagepack+mapping. CurrentlocalinventoryfoundprocessedCelebA but noofficialunalignedJPEG/deltashards. This is a separate data-acquisition/build task; no large acquisition executed. A validnewsubset can be smaller and need not rescue all30000mirrorkeys.

## Reproducibility

Local audit folder: /mnt/t7/Datasety/downloads/CelebAMask-HQ/official_metadata_20261114/
- check_local_samples.py: bounded rerunnableexistingZIPcheck, not labeladmission.
- CHECKSUM_BRIDGE_12.json SHA2568a81c72d7894d02121609878a896f1c47a467be1bfa49e60d3b03471bb68a1bb.
- official_pggan_dataset_tool.py SHA25652b73ca95731dffdc9c064feb3bf5f6457965fe70befd9b2bea3930f39242dcb; immutablecommitcopy verified identical.
- HF_TREE.json SHA256ecd9b8484ef9f9ef013de214a64b6e6b3343891d61820c0fe2b795f5ed4887f8 recordsprimaryHF LFSmetadata.

No conclusion of intentionalcorruption, datasetmislabeling or wrongpersonidentity follows; exactmapping remains unproven. Do not silentlyrepair the labels or historicalsplits.
