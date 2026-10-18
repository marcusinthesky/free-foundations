{ pkgs, ... }:
{
  name = "free-foundations";
  packages = with pkgs; [
    git
    gh
    just
    prek
    convco
    jq
    nixfmt
    statix
    deadnix
    rumdl
    codespell
    lychee
    tombi
    python313
    uv
    ruff
    nodejs
    bun
    typescript
    biome
    elan
    tex-fmt
    (texliveInfraOnly.withPackages (ps: [
      ps.chktex
      ps.texcount
      # Matplotlib PGF text metrics; Tectonic typesets the final manuscript.
      ps.latex-bin
      ps.graphics
      ps.epstopdf-pkg
      ps.underscore
      ps.lm
    ]))
    tectonic
    # Blueprint dependency graphs: pygraphviz builds against this graphviz.
    graphviz
    (rWrapper.override { packages = with rPackages; [ robustbase ]; })
  ];
  env = {
    # The Hugging Face S3 gateway (DVC remote) does not parse the trailing checksums
    # recent botocore sends by default.
    AWS_REQUEST_CHECKSUM_CALCULATION = "when_required";
    AWS_RESPONSE_CHECKSUM_VALIDATION = "when_required";
    CFLAGS = "-I${pkgs.graphviz}/include";
    LDFLAGS = "-L${pkgs.graphviz}/lib -L${pkgs.graphviz}/lib/graphviz -Wl,-rpath,${pkgs.graphviz}/lib:${pkgs.graphviz}/lib/graphviz";
  };
  enterShell = ''
    uv sync --frozen
    export PATH="$PWD/.venv/bin:$PATH"
    prek install
  '';
  enterTest = ''
    just check
  '';
}
