{
  description = "Yuuno combines Jupyter with VapourSynth";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = { nixpkgs, flake-utils, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      ################################
      # Change this
      defaultPython = "python39";
      supportedPythonVersions = [
        "python39"
        "python38"
        "python37"
      ];

      requirements = py: with py.pkgs; [
        (vapoursynthModule py)
        pillow
        jupyter
        traitlets
        jinja2
        ipywidgets
        pillow
        psutil
      ];

      ################################
      # Constructing the packages

      pkgs = nixpkgs.legacyPackages.${system};

      allSupportedPythons = f: builtins.listToAttrs (map (py: {
        name = py;
        value = f pkgs.${py};
      }) supportedPythonVersions);

      vapoursynthModule = py: py.pkgs.buildPythonPackage {
        src = pkgs.vapoursynth.src;
        pname = "vapoursynth";
        version = pkgs.vapoursynth.version;
        nativeBuildInputs = with py.pkgs; [ cython setuptools ];
        buildInputs = [ pkgs.vapoursynth ];
      };

      nodePackage = (pkgs.yarn2nix-moretea.mkYarnPackage {
        src = ./yuuno-jupyter;
        yarnLock = ./yuuno-jupyter/yarn.lock;
      }).overrideAttrs (old: {
        buildPhase = (if old ? buildPhase then old.buildPhase else "") + "\nyarn run build";
      });

    in
      rec {
        packages =
          (allSupportedPythons (py: py.pkgs.buildPythonPackage {
            pname = "yuuno";
            version = "1.3";
            src = ./.;
            buildInputs = requirements py;

            COMPILED_YUUNO_JS = "${nodePackage}/libexec/yuuno-jupyter/deps/yuuno_ipython/build";

            installCheckPhase = ''
              for path in tests/*; do
                name=$(basename $path)
                if [[ $name == test_* ]]; then
                  python -m unittest tests.''${name%.*}
                fi
              done
            '';
          })) // {
            javascript = nodePackage;
          };

        defaultPackage = packages.${defaultPython};

        devShells = allSupportedPythons (py: pkgs.mkShell {
          buildInputs = [
            (py.withPackages (_: requirements py))

            pkgs.yarn
          ];
        });
        devShell = devShells.${defaultPython};
      }
    );
}
