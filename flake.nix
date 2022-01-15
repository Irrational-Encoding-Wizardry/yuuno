{
  description = "Yuuno combines Jupyter with VapourSynth";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    jupyterWith = {
      url = "github:tweag/jupyterWith";
    };
  };

  outputs = { nixpkgs, flake-utils, jupyterWith, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      ################################
      # Change this
      defaultPython = "python39";
      supportedPythonVersions = [
        "python39"
        "python38"
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
        overlays = [] ++ (builtins.attrValues jupyterWith.overlays);
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

      yuuno4jupyter = (pkgs.yarn2nix-moretea.mkYarnPackage {
        src = ./yuuno-jupyter;
        yarnLock = ./yuuno-jupyter/yarn.lock;
      }).overrideAttrs (old: {
        buildPhase = (if old ? buildPhase then old.buildPhase else "") + "\nyarn run build";
      });

      mkDirectoryWith = yuuno: python: pkgs.runCommandNoCC "" {} ''
        export PATH=${python.withPackages (ps: with ps; [jupyter yuuno ipywidgets])}/bin:$PATH
        export JUPYTER_DATA_DIR=$out/data
        export JUPYTER_CONFIG_DIR=$out/config
        mkdir -p $out/{data,config}

        python -m notebook.nbextensions install --py --user yuuno_ipython
        python -m notebook.nbextensions enable --py --user yuuno_ipython

        python -m notebook.nbextensions install --py --user widgetsnbextension
        python -m notebook.nbextensions enable --py --user widgetsnbextension
      '';

    in
      rec {
        packages =
          (allSupportedPythons (_: py: py.pkgs.buildPythonPackage {
            pname = "yuuno";
            version = "1.3";
            src = ./.;
            propagatedBuildInputs = requirements py;

            COMPILED_YUUNO_JS = "${yuuno4jupyter}/libexec/yuuno-jupyter/deps/yuuno_ipython/build";

            installCheckPhase = ''
              for path in tests/*; do
                name=$(basename $path)
                if [[ $name == test_* ]]; then
                  python -m unittest tests.''${name%.*}
                fi
              done
            '';
          })) // {
            jupyter-frontend = yuuno4jupyter;
          };

        defaultPackage = packages.${defaultPython};

        apps = allSupportedPythons (name: py: {
          type = "app";
          program =
            let
              pyWithPackages = (pkgs.jupyter.override{
                python3 = py.withPackages (_: requirements py);
                definitions = {
                  python3 = {
                    displayName = "Python 3 with Yuuno";
                    argv = [
                      "${py.withPackages (_: requirements py)}/bin/python"
                      "-m"
                      "ipykernel_launcher"
                      "-f"
                      "{connection_file}"
                    ];
                    language = "python";
                    logo32 = "lol";
                    logo64 = "lol";
                  };
                };
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
          }) // (pkgs.lib.mapAttrs' (k: v: { name = "${k}-lab"; value = v; }) (allSupportedPythons (name: py: {
            type = "app";
            program =
              let
                ipython = pkgs.jupyterWith.kernels.iPythonWith {
                  name = "python";
                  python3 = py;
                  packages = ps: (requirements py) ++ (with ps; [debugpy]);
                };

                jupyterlab = pkgs.jupyterWith.jupyterlabWith {
                  kernels = [ ipython ];
                  extraPackages = ps: with ps; [ipywidgets];
                };
              in
                toString (pkgs.writeShellScript "yuuno-jupyterlab" ''
                  export PATH=${pkgs.lib.makeBinPath (with pkgs;[yarn nodejs])}:$PATH
                  exec -a "$0" ${jupyterlab}/bin/jupyter-lab "$@"
                '');
          })));
        defaultApp = apps.${defaultPython};


        devShells = allSupportedPythons (_: py: pkgs.mkShell {
          buildInputs = [
            (py.withPackages (_: requirements py))

            pkgs.yarn
            pkgs.nodePackages.lerna
          ];
        });
        devShell = devShells.${defaultPython};

        checks = packages;
      }
    );
}
