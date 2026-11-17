{
  pkgs,
  inputs,
  lib,
  ...
}:
let
  # Isolate the compiler's package set; other development and inference tools keep their pin.
  leanPkgs = import inputs.nixpkgs-lean { inherit (pkgs.stdenv.hostPlatform) system; };
in
{
  name = "free-foundations";
  packages =
    assert builtins.elem pkgs.stdenv.hostPlatform.system [
      "x86_64-linux"
      "aarch64-linux"
    ];
    with pkgs;
    [
      git
      gh
      just
      prek
      convco
      jq
      rumdl
      codespell
      lychee
      nixfmt
      statix
      deadnix
      actionlint
      shellcheck
      shfmt
      tombi
      just-lsp
      ripgrep
      python313
      uv
      ruff
      pyrefly
      (callPackage ./pkgs/schematter.nix { })
      patchelf
      (callPackage ./pkgs/agentsync.nix { })
      (import ./pkgs/lean-toolchain.nix {
        pkgs = leanPkgs;
        inherit (inputs) lean4-nix;
      })
      curl
      gnutar
      zstd
      # Blueprint dependency graphs: pygraphviz builds against this graphviz.
      graphviz
      swig
      stdenv.cc
      tectonic
      tex-fmt
      (texliveInfraOnly.withPackages (ps: [
        ps.chktex
        ps.kpathsea
        ps.texcount
        # Matplotlib PGF text metrics; Tectonic typesets the final manuscript.
        ps.latex-bin
        ps.graphics
        ps.epstopdf-pkg
        ps.underscore
        ps.lm
      ]))
      pandoc
      # The Fernández replication's robust MM betas (fernandez/betas.R).
      (rWrapper.override {
        packages = with rPackages; [
          robustbase
          robust
        ];
      })
    ];
  env = {
    UV_PYTHON_DOWNLOADS = "never";
    UV_PYTHON = "${pkgs.python313}/bin/python3";
    # Nix's Python does not consult nix-ld, so manylinux wheels (numpy, torch) need the
    # C++ runtime; CUDA wheels find the host driver under NixOS's opengl-driver path.
    LD_LIBRARY_PATH = "${
      lib.makeLibraryPath [
        pkgs.stdenv.cc.cc.lib
        pkgs.zlib
      ]
    }:/run/opengl-driver/lib";
    LEAN_BLUEPRINT_CFLAGS = "-I${pkgs.lib.getDev pkgs.graphviz}/include";
    LEAN_BLUEPRINT_LDFLAGS = "-L${pkgs.lib.getLib pkgs.graphviz}/lib -L${pkgs.lib.getLib pkgs.graphviz}/lib/graphviz -Wl,-rpath,${pkgs.lib.getLib pkgs.graphviz}/lib:${pkgs.lib.getLib pkgs.graphviz}/lib/graphviz";
    PROJECT_RUNTIME_LINKER = pkgs.stdenv.cc.bintools.dynamicLinker;
    PROJECT_RUNTIME_LIBRARIES = lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.glibc
      pkgs.zlib
    ];
    # The Hugging Face S3 gateway (DVC remote) does not parse the trailing checksums
    # recent botocore sends by default.
    AWS_REQUEST_CHECKSUM_CALCULATION = "when_required";
    AWS_RESPONSE_CHECKSUM_VALIDATION = "when_required";
  };
  enterShell = "unset PYTHONPATH PYTHONHOME VIRTUAL_ENV";
  enterTest = "just check";
}
