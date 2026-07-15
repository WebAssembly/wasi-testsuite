# shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
    buck2
    dotslash
  ];

  shellHook = ''
    # Create and activate virtual environment
    if [ ! -d .venv ]; then
      python3 -m venv .venv
    fi
    source .venv/bin/activate
    
    # Install requirements
    pip install -r test-runner/requirements.txt
    pip install -r test-runner/requirements/dev.txt
  '';
}
