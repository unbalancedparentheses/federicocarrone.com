{
  description = "Federico Carrone's personal website";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            zola
            nodejs_20
            lightningcss
          ];

          shellHook = ''
            echo "federicocarrone.com dev environment"
            echo ""
            echo "Commands:"
            echo "  zola serve        - Start dev server at http://127.0.0.1:1111"
            echo "  zola build        - Build static site"
            echo "  npm install       - Install Node dependencies"
            echo "  npm run build-css - Minify CSS"
            echo ""
          '';
        };
      }
    );
}
