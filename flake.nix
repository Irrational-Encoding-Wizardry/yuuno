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

      pkgs = import nixpkgs {
        inherit system;
      };

      allSupportedPythons = f: builtins.listToAttrs (map (py: {
        name = py;
        value = f py pkgs.${py};
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

      mkDirectoryWith = yuuno: python: pkgs.runCommandNoCC "" {} ''
        export PATH=${python.withPackages (ps: with ps; [jupyter yuuno])}/bin:$PATH
        export JUPYTER_DATA_DIR=$out/data
        export JUPYTER_CONFIG_DIR=$out/config
        mkdir -p $out/{data,config}

        python -m notebook.nbextensions install --py --user yuuno_ipython
        python -m notebook.nbextensions enable --py --user yuuno_ipython
      '';

    in
      rec {
        packages =
          (allSupportedPythons (_: py: py.pkgs.buildPythonPackage {
            pname = "yuuno";
            version = "1.3";
            src = ./.;
            propagatedBuildInputs = requirements py;

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

        apps = allSupportedPythons (name: py: {
          type = "app";
          program =
            let
              pyWithPackages = (pkgs.jupyter.override{
                python3 = py;
              });

              cfg = mkDirectoryWith packages.${name} py;
            in
            toString (pkgs.writeShellScript "yuuno-jupyter" ''
              TDIR=$(mktemp -d)
              cp --no-preserve=mode,ownership -r ${cfg}/* $TDIR
              export JUPYTER_CONFIG_DIR=$TDIR/config
              export JUPYTER_DATA_DIR=$TDIR/data
              echo $TDIR
              exec -a "$0" ${pyWithPackages}/bin/jupyter-notebook "$@"
            '');
        });
        defaultApp = apps.${defaultPython};


        devShells = allSupportedPythons (_: py: pkgs.mkShell {
          buildInputs = [
            (py.withPackages (_: requirements py))

            pkgs.yarn
          ];
        });
        devShell = devShells.${defaultPython};
      }
    );
}
