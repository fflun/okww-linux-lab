# Third-party sources

This repository contains experimental adapters and platform-boundary changes for
[OK-WW](https://github.com/ok-oldking/ok-wuthering-waves), based on v3.6.7,
commit `7df910be3b91e73be0f7a96d34fb4091510f7fac`. See the preserved AGPL-3.0
license in `LICENSE`. Modifications were made on 2026-10-04 for Linux experiments.

`code/cloud_keymap.py` contains key maps derived from
[March7thAssistant](https://github.com/moesnow/March7thAssistant),
`module/automation/cdp_input.py`, commit
`881e90b4ce50611d26ecdcb06ee6ecd07cc76b6e`, under GPL-3.0.
The full license is preserved in `licenses/March7thAssistant-GPL-3.0.txt`.
No Star Rail tasks or account information are included.

The runtime depends on [ok-script](https://github.com/ok-oldking/ok-script).
Its source, binaries, Qt dependencies and model assets are not bundled here.
`prepare_stage.py` accepts a separately obtained source snapshot and preserves
its license when preparing a local stage. The framework's own license terms
continue to apply; this repository does not relicense that dependency.

`patches/okww-platform.patch` applies against the stated OK-WW base; copy
`platform/platform_io.py` to the target's `src/platform_io.py` when reviewing it.
These changes isolate operating-system APIs; they do not replace combat logic.

OCR packages, models and Chinese fonts are installed or supplied separately and
retain their respective upstream licenses.
