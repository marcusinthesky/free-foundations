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
    (texliveInfraOnly.withPackages (ps: [ ps.chktex ]))
    tectonic
    # Blueprint dependency graphs: pygraphviz builds against this graphviz.
    graphviz
    (rWrapper.override { packages = with rPackages; [ robustbase ]; })
  ];
  env = {
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
