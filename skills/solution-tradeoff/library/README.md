# Packaged perspective library

This folder holds your own verified perspective files, so that they ship inside the skill you upload (decision 18). It is the third source the skill searches, after perspective files attached to the chat or in the project's files, and after a folder you name or set in `perspectives.library` in `assets/config.yaml`. The shipped defaults in `references/perspectives/` come last. On a matching `id`, the higher source wins.

To use it:

1. Copy each verified perspective file here as `<id>.md`, in the format of `references/perspective-format.md`, with `verified: true`, `verified_by` and `verified_at` in its header.
2. Run `make package`. The package includes every `.md` file in this folder except this README.

The files in this folder are your own material: git ignores everything here except this README, so they are never committed. Where a file lives does not make it verified; the verification gate reads its header and this run's confirmation.
