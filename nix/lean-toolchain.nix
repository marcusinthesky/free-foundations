# Official Lean binary, packaged by the pinned lean4-nix provider as in pricing-perspective.
# Keep the tag and archive hashes aligned with src/lean/lean-toolchain.
{ pkgs, lean4-nix }:
let
  leanManifest = {
    tag = "v4.35.0";
    toolchain = {
      x86_64-linux = {
        url = "https://github.com/leanprover/lean4/releases/download/v4.35.0/lean-4.35.0-linux.tar.zst";
        hash = "sha256-colZekRUMkbJInuMrlAXZ+CVzhf21Ei5X8So3Jcmj20=";
      };
      aarch64-linux = {
        url = "https://github.com/leanprover/lean4/releases/download/v4.35.0/lean-4.35.0-linux_aarch64.tar.zst";
        hash = "sha256-yPD4o5IOg5cYsTQ+Z4H9gKPpsQJPvNcHjrMPVOgGsCg=";
      };
    };
  };
in
# `.lean-all` is the bundled toolchain derivation (bin/{lean,lake,leanc} +
# lib/lean/*). We pass `pkgs` explicitly so callPackage always satisfies
# toolchain.nix's `pkgs` formal regardless of the caller's package set.
(pkgs.callPackage (lean4-nix + "/lib/toolchain.nix") { inherit pkgs; }).fetchBinaryLean leanManifest
