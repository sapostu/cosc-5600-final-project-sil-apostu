# COSC 5600 - Fall 2025 - Graduate - Final Project Code

A compact, modular project used for the COSC 5600 course made by me, Silviu George Apostu.

**Table of Contents**
- Overview
- Requirements for all operating systems
- Installation
  
- Usage
- Notes
- Contact

Overview
--------

This project is written to be decoupled, modular, and easy to read, test, and scale. 

Requirements for ALL operating system
------------

1. **Git** must be installed. Check on any OS with `git -v`

2. **Python 3** must be installed. 

- `py -V` on in Windows Command Prompt

- `python3 -v` or `python -v` on Unix/Linux



3. **pip** or **pip3** must be installed

- check with `pip -v` or `pip3 -v`

#### CRITICAL PART

----------python package `scikit-learn` or `sklearn` MUST be downloaded it. 


5. `git-lfs` (only required if you need to edit the large dataset files tracked with LFS)

## Running the application

MAC OS 
------------

1. Clone the repository then `cd` into the cloned project:

```bash
git clone <repo-url>
```

2. Place your `config.json` file in the project root (next to `Main.py`).

3. Create and activate the virtual environment using the provided scripts. If the scripts are not executable, make them executable first:

```bash
chmod +x Script/create_venv.sh Script/activate.sh Script/deactivate.sh Script/optimized_python_run.sh
sh Script/create_venv.sh
source Script/activate.sh
```

4. Verify the virtual environment's Python points to the `venv` directory:

```bash
which python    # should show something like /.../venv/bin/python
```

5. Run the project ( Python creates a lot of bloat; this script runs application then cleans up bloat ) :

```bash
sh ./Script/optimized_python_run
```


Windows
------------

1. ensure repo is cloned

2. verify `python` OR `python3`, `pip` OR `pip3` and `scikit-learn` OR `sklearn` all installed

3. run the app via `py .\Main.py`

NOTE: I recommend running this in VS Code. After running, you can go to `Source Control` tab then delete all the Python bloat

Linux ( Ubuntu Example )
------------

1. ensure repo is cloned

2. verify `python` OR `python3`, `pip` OR `pip3` and `scikit-learn` OR `sklearn` all installed

* scikit can be download on ubuntu with `sudo apt install python3-sklearn` if you have sudo access

3. run the app via `py .\Main.py`

NOTE: I recommend running this in VS Code. After running, you can go to `Source Control` tab then delete all the Python bloat

Usage
-----
1. Important fields `NUM_ITEMS_TO_TEST` and `SEED` in `Main.py`. Ensure to set these how you want or use default

  - `NUM_ITEMS_TO_TEST` is a number. This is how many items from the dataset chosen will be randomly chosen
  - `SEED` is a string. This deterministically randomly chooses test items from the dataset

2. Ensure you run the scripts listed earlier. No command line inputs or anything. Just watch my app work.
3. If you need to modify or replace dataset files, ensure Git LFS is installed before pulling changes.
4. If a script fails due to execution permissions, set the executable bit (e.g., `chmod +x Script/<script>.sh`).

Notes
-----

- This repository is organized for readability and testability; modules in `Model/`, `Service/` and `Util/` are separated to make developing easier for me
- When editing datasets or committing large files, use Git LFS to avoid repository bloat.
- The more you increase `NUM_ITEMS_TO_TEST`, the higher change the app will fail. This is due to LLM API limits. Running things at scale is expensive. I don't have that kind of money


