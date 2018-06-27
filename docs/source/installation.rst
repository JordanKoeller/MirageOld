.. Installation details.

Installing Mirage
=================

The easiest way to get Mirage is to clone from the `github repository <https://github.com/JordanKoeller/Mirage>`_. Then run the command ``bash setup`` from the project directory. This command will use the Python package manager ``pip`` to install all dependencies, and compile all the C code. Note that this installs the bare basics of the dependencies for the program. Running the command ``bash setup --all`` will install all possible dependencies.

Once the setup script has been run, you will be asked if you would like to add ``lens_analysis`` to your ``.bashrc`` profile. If you choose yes, you will be able to run ``$ lens_analysis`` and open a python interpreter with the program already imported. Otherwise, you will need to run the ``lens_analysis`` script from inside ``scripts/`` to launch the program. For more info on using the program, see :doc:`Getting Started with Mirage <gettingstarted>`.