# Finite-saturation implementation plan

Root coordinates one shared checkout. Separate agents own the new theorem, source comparison, and checker/tests/protocol. Existing Python and standard-library arithmetic suffice; the unchanged sharp-cost helper supplies exact rank weights and logarithm enclosures.

- [x] Explore the hybrid upper and finite lower directions. Identify the hybrid architecture as prior art; derive and independently review the stronger finite-slice lemma and high-budget arbitrary-grid result in ignored notes.
- [x] Freeze the specification and bounded protocol before the saved calculation (`4eedbd2`).
- [x] Write the full theorem and focused primary-source comparison; independently check the transcription and source passages.
- [x] Write meaningful failing tests before implementation, then implement the frozen checker with six source pins and conservative rounding. Preserve all prior files.
- [x] Independently review the checker; run focused tests under standard-library and optimized Python and the full suite; commit reviewed sources before the full calculation. All 241 tests pass; 14 focused tests also pass with site packages disabled and under optimized Python. Review corrected conservative handling of unresolved integer caps and added a failing-then-passing regression.
- [x] Run the frozen calculation twice to separate paths, compare bytes, and report only the observed scope and counts. Reviewed source commit `52e1b4b` preceded both runs. Both outputs are 17,746 identical bytes, SHA-256 `7a406e94bcbaf1105df94934163ec4491ce1a200ccdbf9da273993fcc926af53`; 644 grids and 20,608 configurations pass.
- [x] Update navigation/provenance; verify old pins, local links, storage, source freeze, and staged Git bytes. Seventy source/document pins across ten manifests pass in both worktree and Git index; 104 changed-document local links resolve; all prior saved-evidence verifiers pass. Workspace is about 48 MB including Git and local reproductions. Separate agent review reconciled every report count, source pin, and artifact hash.
- [ ] Publish and verify public main/tag; record the bounded phase's completion while leaving the broader goal active.

Key hazards: rare or zero positive counts; adaptively interleaved block queries; conditioning on stopped histories; tiny caps; strict unsafe alternatives after rounding; envelope versus individual-row log-concavity; n/a=4 endpoint; silently changing the declared target family; removing the deterministic prefix cap; claims of originality for classical threshold sampling.
