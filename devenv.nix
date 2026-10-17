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
    (rWrapper.override { packages = with rPackages; [ robustbase ]; })
  ];
  enterShell = ''
    uv sync --frozen
    export PATH="$PWD/.venv/bin:$PATH"
    prek install
  '';
  enterTest = ''
    just check
  '';
}
