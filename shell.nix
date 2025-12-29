{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    zola
    nodejs_20
  ];

  shellHook = ''
    echo "federicocarrone.com dev environment"
    echo ""
    echo "Commands:"
    echo "  zola serve        - Start dev server"
    echo "  npm install       - Install dependencies"
    echo "  npm run build-css - Minify CSS"
    echo ""
  '';
}
